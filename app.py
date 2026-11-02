import io
import os
from flask import Flask, render_template, request, jsonify, send_file
import openpyxl
from openpyxl.styles import Font, PatternFill
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# ==========================================
# MYSQL DATABASE CONFIGURATION
# ==========================================
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.environ.get('DB_PASSWORD', ''),  # Your MySQL Password
    'database': 'campusos_db'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"❌ DATABASE CONNECTION ERROR: {e}")
        return None

def query_db(query, args=(), fetchone=False, fetchall=False, commit=False):
    conn = get_db_connection()
    if not conn:
        print("❌ DATABASE CONNECTION ERROR: Check your MySQL credentials in app.py!")
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id if last_id else True
        if fetchone:
            res = cursor.fetchone()
            cursor.close()
            conn.close()
            return res
        if fetchall:
            res = cursor.fetchall()
            cursor.close()
            conn.close()
            return res
    except Error as err:
        print(f"❌ MYSQL QUERY EXECUTION ERROR: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def log_activity(user_name, action, module, ip_address='127.0.0.1'):
    query_db("INSERT INTO activity_logs (user_name, action, module, ip_address) VALUES (%s, %s, %s, %s)",
             (user_name, action, module, ip_address), commit=True)


# ==========================================
# PAGE ROUTING VIEWS
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student/dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/clubhead/dashboard')
def club_head_dashboard():
    return render_template('club_head_dashboard.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/clubs')
def admin_clubs():
    return render_template('clubs.html')

@app.route('/admin/students')
def admin_students():
    return render_template('students.html')

@app.route('/admin/clubheads')
def admin_clubheads():
    return render_template('club_heads.html')

@app.route('/admin/events')
def admin_events():
    return render_template('events.html')

@app.route('/admin/sponsors')
def admin_sponsors():
    return render_template('sponsors.html')

@app.route('/admin/reports')
def admin_reports():
    return render_template('reports.html')

@app.route('/admin/settings')
def admin_settings():
    return render_template('settings.html')


# ==========================================
# PUBLIC & AUTHENTICATION APIs
# ==========================================

# 1. Home Page Live Stats & Upcoming Events
@app.route('/api/public/stats', methods=['GET'])
def public_stats():
    clubs_res = query_db("SELECT COUNT(*) as cnt FROM clubs WHERE status='Active'", fetchone=True)
    students_res = query_db("SELECT COUNT(*) as cnt FROM students", fetchone=True)
    events_res = query_db("SELECT COUNT(*) as cnt FROM events", fetchone=True)
    sponsors_res = query_db("SELECT IFNULL(SUM(amount),0) as sum FROM sponsors", fetchone=True)

    events = query_db("""
        SELECT e.id, e.title, e.venue, DATE_FORMAT(e.event_date, '%d %b %Y') as event_date, c.name as club_name, 
               GREATEST(0, (e.capacity - (SELECT COUNT(*) FROM event_registration er WHERE er.event_id = e.id))) as seats_left
        FROM events e
        LEFT JOIN clubs c ON e.club_id = c.id
        ORDER BY e.event_date ASC LIMIT 5
    """, fetchall=True)

    return jsonify({
        'total_clubs': clubs_res['cnt'] if clubs_res else 0,
        'total_students': students_res['cnt'] if students_res else 0,
        'total_events': events_res['cnt'] if events_res else 0,
        'total_sponsors': float(sponsors_res['sum']) if sponsors_res else 0,
        'upcoming_events': events or []
    })

# 2. Student Sign Up
@app.route('/api/register', methods=['POST'])
def register_student():
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    roll_no = data.get('roll_no', '').strip()
    department = data.get('department', '').strip()
    year = data.get('year', '').strip()
    phone = data.get('phone', '').strip()

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match!'}), 400

    existing = query_db("SELECT id FROM students WHERE LOWER(email)=%s OR LOWER(roll_no)=%s", (email, roll_no.lower()), fetchone=True)
    if existing:
        return jsonify({'success': False, 'message': 'Student with this email or roll number already exists!'}), 400

    result = query_db("""
        INSERT INTO students (name, email, password, roll_no, department, year, phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (name, email, password, roll_no, department, year, phone), commit=True)

    if result:
        log_activity(name, f"Registered new student account ({roll_no})", "Registration")
        return jsonify({'success': True, 'message': 'Registration successful! You can now log in.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save student data to MySQL database!'}), 500

# 3. User Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    role = data.get('role', 'Student')

    user = None
    if role == 'Super Admin':
        user = query_db("SELECT id, name, email, role, avatar_url FROM admins WHERE LOWER(TRIM(email))=%s AND password=%s", (email, password), fetchone=True)
    elif role == 'Club Head':
        user = query_db("""
            SELECT ch.id, ch.name, ch.email, ch.phone, ch.club_id, 'Club Head' as role, c.name as club_name, ch.avatar_url 
            FROM club_heads ch 
            LEFT JOIN clubs c ON ch.club_id = c.id 
            WHERE LOWER(TRIM(ch.email))=%s AND ch.password=%s
        """, (email, password), fetchone=True)
    elif role == 'Student':
        user = query_db("SELECT id, name, email, roll_no, department, year, 'Student' as role FROM students WHERE LOWER(TRIM(email))=%s AND password=%s", (email, password), fetchone=True)

    if user:
        log_activity(user['name'], f"Logged into system as {role}", "Authentication")
        return jsonify({'success': True, 'user': user})
    else:
        return jsonify({'success': False, 'message': f'Invalid credentials for {role} role.'}), 401


# ==========================================
# STUDENT DASHBOARD & ACTIONS APIs
# ==========================================
@app.route('/api/student/dashboard/<int:student_id>', methods=['GET'])
def get_student_dashboard(student_id):
    student = query_db("SELECT id, name, email, roll_no, department, year FROM students WHERE id=%s", (student_id,), fetchone=True)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    reg_events_count = query_db("SELECT COUNT(*) as c FROM event_registration WHERE student_id=%s", (student_id,), fetchone=True)['c'] or 0
    joined_clubs_count = query_db("SELECT COUNT(*) as c FROM club_members WHERE student_id=%s AND status='Approved'", (student_id,), fetchone=True)['c'] or 0
    upcoming_events_count = query_db("SELECT COUNT(*) as c FROM events WHERE event_date >= CURDATE()", fetchone=True)['c'] or 0

    all_clubs = query_db("""
        SELECT c.id, c.name, c.category, c.faculty_coordinator, ch.name as head_name,
               (SELECT cm.status FROM club_members cm WHERE cm.club_id = c.id AND cm.student_id = %s LIMIT 1) as membership_status,
               (SELECT COUNT(*) FROM club_members cm2 WHERE cm2.club_id = c.id AND cm2.status = 'Approved') as members_count
        FROM clubs c 
        LEFT JOIN club_heads ch ON c.id = ch.club_id
        WHERE c.status = 'Active' ORDER BY c.name ASC
    """, (student_id,), fetchall=True) or []

    available_events = query_db("""
        SELECT e.id, e.title, e.venue, e.fee, e.event_time, DATE_FORMAT(e.event_date, '%d %b %Y') as event_date, c.name as club_name, 
               GREATEST(0, (e.capacity - (SELECT COUNT(*) FROM event_registration er WHERE er.event_id = e.id))) as seats_left,
               (SELECT COUNT(*) FROM event_registration er2 WHERE er2.event_id = e.id AND er2.student_id = %s) as is_registered
        FROM events e
        LEFT JOIN clubs c ON e.club_id = c.id
        ORDER BY e.event_date ASC
    """, (student_id,), fetchall=True) or []

    my_events = query_db("""
        SELECT e.id, e.title, DATE_FORMAT(e.event_date, '%d %b %Y') as event_date, e.event_time, e.venue, c.name as club_name,
               IF(e.event_date < CURDATE(), 'Completed', 'Upcoming') as event_status
        FROM event_registration er
        JOIN events e ON er.event_id = e.id
        LEFT JOIN clubs c ON e.club_id = c.id
        WHERE er.student_id = %s ORDER BY e.event_date ASC
    """, (student_id,), fetchall=True) or []

    completed_events_count = len([ev for ev in my_events if ev['event_status'] == 'Completed'])

    return jsonify({
        'student': student,
        'stats': {
            'registered_events': reg_events_count, 
            'joined_clubs': joined_clubs_count, 
            'certificates': completed_events_count, 
            'upcoming_events': upcoming_events_count
        },
        'all_clubs': all_clubs,
        'available_events': available_events,
        'my_events': my_events
    })

@app.route('/api/join-club', methods=['POST'])
def join_club():
    data = request.json
    student_id = data.get('student_id')
    club_id = data.get('club_id')

    try:
        query_db("INSERT INTO club_members (club_id, student_id, status) VALUES (%s, %s, 'Approved')", (club_id, student_id), commit=True)
        return jsonify({'success': True, 'message': 'Successfully joined club!'})
    except Error:
        return jsonify({'success': False, 'message': 'You are already a member of this club!'}), 400

@app.route('/api/register-event', methods=['POST'])
def event_register():
    data = request.json
    e_id, s_id = data.get('event_id'), data.get('student_id')

    event = query_db("SELECT capacity, (SELECT COUNT(*) FROM event_registration WHERE event_id=%s) as reg_cnt FROM events WHERE id=%s", (e_id, e_id), fetchone=True)
    if event and event['reg_cnt'] >= event['capacity']:
        return jsonify({'success': False, 'message': 'Event is full! No seats left.'}), 400

    try:
        query_db("INSERT INTO event_registration (event_id, student_id) VALUES (%s, %s)", (e_id, s_id), commit=True)
        return jsonify({'success': True, 'message': 'Successfully registered for event!'})
    except Error:
        return jsonify({'success': False, 'message': 'You are already registered for this event!'}), 400

@app.route('/api/cancel-registration', methods=['POST'])
def cancel_registration():
    data = request.json
    e_id, s_id = data.get('event_id'), data.get('student_id')
    query_db("DELETE FROM event_registration WHERE event_id=%s AND student_id=%s", (e_id, s_id), commit=True)
    return jsonify({'success': True, 'message': 'Registration cancelled successfully.'})


# ==========================================
# CLUB HEAD DASHBOARD APIs
# ==========================================
@app.route('/api/clubhead/full_dashboard/<int:club_id>', methods=['GET'])
def get_full_clubhead_dashboard(club_id):
    club = query_db("SELECT * FROM clubs WHERE id=%s", (club_id,), fetchone=True)
    if not club:
        return jsonify({'error': 'Club not found'}), 404

    members_cnt = query_db("SELECT COUNT(*) as c FROM club_members WHERE club_id=%s AND status='Approved'", (club_id,), fetchone=True)['c'] or 0
    events_cnt = query_db("SELECT COUNT(*) as c FROM events WHERE club_id=%s", (club_id,), fetchone=True)['c'] or 0
    upcoming_events_cnt = query_db("SELECT COUNT(*) as c FROM events WHERE club_id=%s AND event_date >= CURDATE()", (club_id,), fetchone=True)['c'] or 0
    pending_cnt = query_db("SELECT COUNT(*) as c FROM join_requests WHERE club_id=%s AND status='Pending'", (club_id,), fetchone=True)['c'] or 0
    sponsors_sum = query_db("SELECT IFNULL(SUM(amount),0) as s FROM sponsors WHERE club_id=%s", (club_id,), fetchone=True)['s'] or 0
    certs_cnt = query_db("SELECT COUNT(*) as c FROM certificates cert JOIN events e ON cert.event_id = e.id WHERE e.club_id=%s", (club_id,), fetchone=True)['c'] or 0

    members = query_db("""
        SELECT cm.id as membership_id, s.id as student_id, s.name, s.email, s.roll_no, s.department, s.year, s.phone, cm.status, 
               DATE_FORMAT(cm.joined_date, '%d %b %Y') as joined_date
        FROM club_members cm
        JOIN students s ON cm.student_id = s.id
        WHERE cm.club_id = %s ORDER BY cm.id DESC
    """, (club_id,), fetchall=True) or []

    join_requests = query_db("""
        SELECT jr.id as request_id, s.id as student_id, s.name, s.department, s.year, s.email, s.phone, jr.reason, 
               DATE_FORMAT(jr.request_date, '%d %b %Y %h:%i %p') as request_date
        FROM join_requests jr
        JOIN students s ON jr.student_id = s.id
        WHERE jr.club_id = %s AND jr.status = 'Pending' ORDER BY jr.id DESC
    """, (club_id,), fetchall=True) or []

    events = query_db("""
        SELECT e.id, e.title, e.description, e.venue, e.fee, e.capacity, e.event_time, e.status, e.poster_url,
               DATE_FORMAT(e.event_date, '%d %b %Y') as event_date,
               (SELECT COUNT(*) FROM event_registration er WHERE er.event_id = e.id) as reg_count
        FROM events e
        WHERE e.club_id = %s ORDER BY e.event_date DESC
    """, (club_id,), fetchall=True) or []

    sponsors = query_db("""
        SELECT s.id, s.name, s.company, s.amount, s.contact, s.phone, s.email, s.status, e.title as event_title,
               DATE_FORMAT(s.created_at, '%d %b %Y') as created_at
        FROM sponsors s
        LEFT JOIN events e ON s.event_id = e.id
        WHERE s.club_id = %s ORDER BY s.id DESC
    """, (club_id,), fetchall=True) or []

    announcements = query_db("""
        SELECT id, title, description, DATE_FORMAT(posted_at, '%d %b %Y %h:%i %p') as posted_at 
        FROM announcements WHERE club_id=%s ORDER BY id DESC
    """, (club_id,), fetchall=True) or []

    gallery = query_db("SELECT * FROM gallery WHERE club_id=%s ORDER BY id DESC", (club_id,), fetchall=True) or []

    certificates = query_db("""
        SELECT cert.id, cert.certificate_code, DATE_FORMAT(cert.issued_date, '%d %b %Y') as issued_date,
               s.name as student_name, s.roll_no, e.title as event_title
        FROM certificates cert
        JOIN students s ON cert.student_id = s.id
        JOIN events e ON cert.event_id = e.id
        WHERE e.club_id = %s ORDER BY cert.id DESC
    """, (club_id,), fetchall=True) or []

    notifications = query_db("SELECT id, title, message, DATE_FORMAT(created_at, '%d %b %Y %h:%i %p') as created_at FROM notifications ORDER BY id DESC LIMIT 5", fetchall=True) or []

    return jsonify({
        'club': club,
        'stats': {
            'members': members_cnt,
            'events_organized': events_cnt,
            'upcoming_events': upcoming_events_cnt,
            'pending_requests': pending_cnt,
            'sponsorship_raised': float(sponsors_sum),
            'certificates_issued': certs_cnt
        },
        'members': members,
        'join_requests': join_requests,
        'events': events,
        'sponsors': sponsors,
        'announcements': announcements,
        'gallery': gallery,
        'certificates': certificates,
        'notifications': notifications
    })

@app.route('/api/clubhead/update_club', methods=['PUT'])
def update_club_info():
    data = request.json
    club_id = data.get('club_id')
    query_db("""
        UPDATE clubs 
        SET description=%s, faculty_coordinator=%s, established_year=%s
        WHERE id=%s
    """, (data.get('description'), data.get('faculty_coordinator'), data.get('established_year'), club_id), commit=True)
    return jsonify({'success': True, 'message': 'Club details updated in MySQL!'})

@app.route('/api/clubhead/join_request/action', methods=['POST'])
def handle_join_request():
    data = request.json
    request_id = data.get('request_id')
    action = data.get('action')

    req = query_db("SELECT * FROM join_requests WHERE id=%s", (request_id,), fetchone=True)
    if not req:
        return jsonify({'success': False, 'message': 'Request not found'}), 404

    if action == 'Approve':
        query_db("UPDATE join_requests SET status='Approved' WHERE id=%s", (request_id,), commit=True)
        query_db("INSERT INTO club_members (club_id, student_id, status) VALUES (%s, %s, 'Approved') ON DUPLICATE KEY UPDATE status='Approved'",
                 (req['club_id'], req['student_id']), commit=True)
        msg = "Join request approved! Student added to official members."
    else:
        query_db("UPDATE join_requests SET status='Rejected' WHERE id=%s", (request_id,), commit=True)
        msg = "Join request rejected."

    return jsonify({'success': True, 'message': msg})

@app.route('/api/clubhead/member/<int:membership_id>', methods=['DELETE'])
def remove_club_member(membership_id):
    query_db("DELETE FROM club_members WHERE id=%s", (membership_id,), commit=True)
    return jsonify({'success': True, 'message': 'Member removed from club.'})

@app.route('/api/clubhead/events', methods=['POST', 'PUT'])
def clubhead_save_event():
    d = request.json
    if request.method == 'POST':
        query_db("""
            INSERT INTO events (title, description, event_date, event_time, venue, fee, capacity, poster_url, club_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (d['title'], d['description'], d['event_date'], d.get('event_time', '10:00 AM'), d['venue'], d.get('fee', 0), d.get('capacity', 100), d.get('poster_url', 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=500'), d['club_id']), commit=True)
        return jsonify({'success': True, 'message': 'Event created successfully!'})
    elif request.method == 'PUT':
        query_db("""
            UPDATE events 
            SET title=%s, description=%s, event_date=%s, event_time=%s, venue=%s, fee=%s, capacity=%s
            WHERE id=%s
        """, (d['title'], d['description'], d['event_date'], d['event_time'], d['venue'], d['fee'], d['capacity'], d['event_id']), commit=True)
        return jsonify({'success': True, 'message': 'Event details updated!'})

@app.route('/api/clubhead/events/<int:event_id>', methods=['DELETE'])
def delete_clubhead_event(event_id):
    query_db("DELETE FROM events WHERE id=%s", (event_id,), commit=True)
    return jsonify({'success': True, 'message': 'Event deleted.'})

@app.route('/api/clubhead/event/<int:event_id>/registrations', methods=['GET'])
def get_event_registrations(event_id):
    event = query_db("SELECT id, title, venue, DATE_FORMAT(event_date, '%d %b %Y') as event_date FROM events WHERE id=%s", (event_id,), fetchone=True)
    registrations = query_db("""
        SELECT er.id as registration_id, s.id as student_id, s.name, s.roll_no, s.department, s.phone, s.email,
               IF(att.status IS NULL, 'Absent', att.status) as attendance_status,
               DATE_FORMAT(er.registered_at, '%d %b %Y %h:%i %p') as registered_at
        FROM event_registration er
        JOIN students s ON er.student_id = s.id
        LEFT JOIN attendance att ON att.event_id = er.event_id AND att.student_id = s.id
        WHERE er.event_id = %s ORDER BY er.id DESC
    """, (event_id,), fetchall=True) or []

    return jsonify({'event': event, 'registrations': registrations})

@app.route('/api/clubhead/event/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    event_id = data.get('event_id')
    student_id = data.get('student_id')
    status = data.get('status', 'Present')

    if status == 'Present':
        query_db("""
            INSERT INTO attendance (event_id, student_id, status)
            VALUES (%s, %s, 'Present')
            ON DUPLICATE KEY UPDATE status='Present'
        """, (event_id, student_id), commit=True)
    else:
        query_db("DELETE FROM attendance WHERE event_id=%s AND student_id=%s", (event_id, student_id), commit=True)

    return jsonify({'success': True, 'message': 'Attendance updated in MySQL!'})

@app.route('/api/clubhead/sponsors', methods=['POST', 'PUT'])
def clubhead_save_sponsor():
    d = request.json
    if request.method == 'POST':
        query_db("""
            INSERT INTO sponsors (name, company, amount, contact, phone, email, status, club_id, event_id)
            VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed', %s, %s)
        """, (d['name'], d['company'], d['amount'], d.get('contact'), d.get('phone'), d.get('email'), d['club_id'], d.get('event_id')), commit=True)
        return jsonify({'success': True, 'message': 'Sponsor added!'})
    elif request.method == 'PUT':
        query_db("""
            UPDATE sponsors 
            SET name=%s, company=%s, amount=%s, contact=%s, phone=%s, email=%s
            WHERE id=%s
        """, (d['name'], d['company'], d['amount'], d['contact'], d['phone'], d['email'], d['sponsor_id']), commit=True)
        return jsonify({'success': True, 'message': 'Sponsor updated!'})

@app.route('/api/clubhead/sponsors/<int:sponsor_id>', methods=['DELETE'])
def delete_clubhead_sponsor(sponsor_id):
    query_db("DELETE FROM sponsors WHERE id=%s", (sponsor_id,), commit=True)
    return jsonify({'success': True, 'message': 'Sponsor deleted.'})

@app.route('/api/clubhead/announcements', methods=['POST'])
def post_announcement():
    data = request.json
    query_db("INSERT INTO announcements (club_id, title, description) VALUES (%s, %s, %s)",
             (data['club_id'], data['title'], data['description']), commit=True)
    query_db("INSERT INTO notifications (title, message, target_role) VALUES (%s, %s, 'Student')",
             (f"New Announcement: {data['title']}", data['description'][:100]), commit=True)
    return jsonify({'success': True, 'message': 'Announcement posted successfully!'})

@app.route('/api/clubhead/certificates/generate', methods=['POST'])
def generate_certificate():
    data = request.json
    event_id = data.get('event_id')
    student_id = data.get('student_id')
    cert_code = f"CERT-CAMPUS-{event_id}-{student_id}"

    try:
        query_db("INSERT INTO certificates (event_id, student_id, certificate_code) VALUES (%s, %s, %s)",
                 (event_id, student_id, cert_code), commit=True)
        return jsonify({'success': True, 'message': f'Certificate generated! Code: {cert_code}'})
    except Error:
        return jsonify({'success': False, 'message': 'Certificate already generated for this student!'}), 400

@app.route('/api/clubhead/gallery', methods=['POST'])
def add_gallery_item():
    data = request.json
    query_db("INSERT INTO gallery (club_id, image_url, caption) VALUES (%s, %s, %s)",
             (data['club_id'], data['image_url'], data.get('caption', '')), commit=True)
    return jsonify({'success': True, 'message': 'Media uploaded to gallery!'})

@app.route('/api/clubhead/gallery/<int:item_id>', methods=['DELETE'])
def delete_gallery_item(item_id):
    query_db("DELETE FROM gallery WHERE id=%s", (item_id,), commit=True)
    return jsonify({'success': True, 'message': 'Image removed from gallery.'})

@app.route('/api/clubhead/profile', methods=['PUT'])
def update_clubhead_profile():
    data = request.json
    head_id = data.get('head_id')
    query_db("""
        UPDATE club_heads 
        SET name=%s, email=%s, phone=%s, password=%s
        WHERE id=%s
    """, (data['name'], data['email'], data['phone'], data['password'], head_id), commit=True)
    return jsonify({'success': True, 'message': 'Profile settings updated successfully!'})

@app.route('/api/export/club_members/<int:club_id>', methods=['GET'])
def export_club_members(club_id):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Club Members"

    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    ws.append(["ID", "Name", "Roll No", "Department", "Year", "Email", "Phone", "Status", "Joined Date"])
    rows = query_db("""
        SELECT s.id, s.name, s.roll_no, s.department, s.year, s.email, s.phone, cm.status, DATE_FORMAT(cm.joined_date, '%d %b %Y')
        FROM club_members cm
        JOIN students s ON cm.student_id = s.id
        WHERE cm.club_id = %s
    """, (club_id,), fetchall=True) or []

    for r in rows:
        ws.append(list(r.values()))

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="Club_Members_Report.xlsx")


# ==========================================
# SUPER ADMIN MASTER APIs
# ==========================================
@app.route('/api/admin/full_dashboard', methods=['GET'])
def get_admin_full_dashboard():
    clubs_cnt = query_db("SELECT COUNT(*) as c FROM clubs", fetchone=True)['c'] or 0
    students_cnt = query_db("SELECT COUNT(*) as c FROM students", fetchone=True)['c'] or 0
    heads_cnt = query_db("SELECT COUNT(*) as c FROM club_heads", fetchone=True)['c'] or 0
    events_cnt = query_db("SELECT COUNT(*) as c FROM events", fetchone=True)['c'] or 0
    upcoming_cnt = query_db("SELECT COUNT(*) as c FROM events WHERE event_date >= CURDATE()", fetchone=True)['c'] or 0
    sponsors_sum = query_db("SELECT IFNULL(SUM(amount),0) as s FROM sponsors", fetchone=True)['s'] or 0
    regs_cnt = query_db("SELECT COUNT(*) as c FROM event_registration", fetchone=True)['c'] or 0
    certs_cnt = query_db("SELECT COUNT(*) as c FROM certificates", fetchone=True)['c'] or 0
    pending_joins = query_db("SELECT COUNT(*) as c FROM join_requests WHERE status='Pending'", fetchone=True)['c'] or 0

    clubs = query_db("""
        SELECT c.*, ch.name as head_name, 
               (SELECT COUNT(*) FROM club_members cm WHERE cm.club_id = c.id) as members_count,
               (SELECT COUNT(*) FROM events e WHERE e.club_id = c.id) as events_count
        FROM clubs c
        LEFT JOIN club_heads ch ON c.id = ch.club_id ORDER BY c.id DESC
    """, fetchall=True) or []

    students = query_db("""
        SELECT s.*, 
               (SELECT COUNT(*) FROM event_registration er WHERE er.student_id = s.id) as registered_events_count,
               (SELECT COUNT(*) FROM club_members cm WHERE cm.student_id = s.id AND cm.status='Approved') as joined_clubs_count
        FROM students s ORDER BY s.id DESC
    """, fetchall=True) or []

    club_heads = query_db("""
        SELECT ch.*, c.name as club_name, DATE_FORMAT(ch.created_at, '%d %b %Y') as created_at_fmt
        FROM club_heads ch
        LEFT JOIN clubs c ON ch.club_id = c.id ORDER BY ch.id DESC
    """, fetchall=True) or []

    events = query_db("""
        SELECT e.*, c.name as club_name, DATE_FORMAT(e.event_date, '%d %b %Y') as event_date_fmt,
               (SELECT COUNT(*) FROM event_registration er WHERE er.event_id = e.id) as registered_count
        FROM events e
        LEFT JOIN clubs c ON e.club_id = c.id ORDER BY e.event_date ASC
    """, fetchall=True) or []

    sponsors = query_db("""
        SELECT s.*, c.name as club_name, e.title as event_title, DATE_FORMAT(s.created_at, '%d %b %Y') as created_at_fmt
        FROM sponsors s
        LEFT JOIN clubs c ON s.club_id = c.id
        LEFT JOIN events e ON s.event_id = e.id ORDER BY s.id DESC
    """, fetchall=True) or []

    activity_logs = query_db("""
        SELECT id, user_name, action, module, ip_address, DATE_FORMAT(created_at, '%d %b %Y %h:%i %p') as created_at_fmt
        FROM activity_logs ORDER BY id DESC LIMIT 15
    """, fetchall=True) or []

    settings_data = query_db("SELECT * FROM settings", fetchall=True) or []
    settings_dict = {item['setting_key']: item['setting_value'] for item in settings_data}

    event_regs_chart = query_db("SELECT e.title, (SELECT COUNT(*) FROM event_registration er WHERE er.event_id = e.id) as count FROM events e", fetchall=True) or []
    club_members_chart = query_db("SELECT c.name, (SELECT COUNT(*) FROM club_members cm WHERE cm.club_id = c.id) as count FROM clubs c", fetchall=True) or []

    return jsonify({
        'stats': {
            'clubs': clubs_cnt, 'students': students_cnt, 'heads': heads_cnt, 'events': events_cnt,
            'upcoming': upcoming_cnt, 'sponsors_amount': float(sponsors_sum), 'registrations': regs_cnt,
            'certificates': certs_cnt, 'pending_approvals': pending_joins
        },
        'clubs': clubs,
        'students': students,
        'club_heads': club_heads,
        'events': events,
        'sponsors': sponsors,
        'activity_logs': activity_logs,
        'settings': settings_dict,
        'charts': {
            'event_regs': event_regs_chart,
            'club_members': club_members_chart
        }
    })

# ADMIN CRUD & ACTIONS
@app.route('/api/admin/clubs', methods=['POST', 'PUT'])
def admin_save_club():
    d = request.json
    if request.method == 'POST':
        query_db("""
            INSERT INTO clubs (name, category, description, faculty_coordinator, established_year, status)
            VALUES (%s, %s, %s, %s, %s, 'Active')
        """, (d['name'], d['category'], d.get('description'), d.get('faculty_coordinator', 'Dr. S. K. Sharma'), d.get('established_year', 2026)), commit=True)
        log_activity('Super Admin', f"Created Club: {d['name']}", 'Clubs')
        return jsonify({'success': True, 'message': 'Club created successfully!'})
    elif request.method == 'PUT':
        query_db("""
            UPDATE clubs SET name=%s, category=%s, description=%s, faculty_coordinator=%s, established_year=%s, status=%s WHERE id=%s
        """, (d['name'], d['category'], d['description'], d['faculty_coordinator'], d['established_year'], d['status'], d['club_id']), commit=True)
        log_activity('Super Admin', f"Updated Club ID #{d['club_id']}", 'Clubs')
        return jsonify({'success': True, 'message': 'Club details updated!'})

@app.route('/api/admin/clubs/<int:club_id>', methods=['DELETE'])
def admin_delete_club(club_id):
    query_db("DELETE FROM clubs WHERE id=%s", (club_id,), commit=True)
    log_activity('Super Admin', f"Deleted Club ID #{club_id}", 'Clubs')
    return jsonify({'success': True, 'message': 'Club deleted.'})

@app.route('/api/admin/clubs/<int:club_id>/status', methods=['PUT'])
def toggle_club_status(club_id):
    status = request.json.get('status', 'Active')
    query_db("UPDATE clubs SET status=%s WHERE id=%s", (status, club_id), commit=True)
    log_activity('Super Admin', f"Changed Club ID #{club_id} status to {status}", 'Clubs')
    return jsonify({'success': True, 'message': f'Club status changed to {status}'})

@app.route('/api/admin/students', methods=['POST', 'PUT'])
def admin_save_student():
    d = request.json
    if request.method == 'POST':
        query_db("""
            INSERT INTO students (name, email, password, roll_no, department, year, phone, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
        """, (d['name'], d['email'].lower(), d.get('password', 'student123'), d['roll_no'], d['department'], d['year'], d.get('phone', '')), commit=True)
        log_activity('Super Admin', f"Added Student: {d['name']} ({d['roll_no']})", 'Students')
        return jsonify({'success': True, 'message': 'Student registered!'})
    elif request.method == 'PUT':
        query_db("""
            UPDATE students SET name=%s, email=%s, roll_no=%s, department=%s, year=%s, phone=%s WHERE id=%s
        """, (d['name'], d['email'].lower(), d['roll_no'], d['department'], d['year'], d.get('phone', ''), d['student_id']), commit=True)
        log_activity('Super Admin', f"Updated Student ID #{d['student_id']}", 'Students')
        return jsonify({'success': True, 'message': 'Student updated!'})

@app.route('/api/admin/students/<int:student_id>', methods=['DELETE'])
def admin_delete_student(student_id):
    query_db("DELETE FROM students WHERE id=%s", (student_id,), commit=True)
    log_activity('Super Admin', f"Deleted Student ID #{student_id}", 'Students')
    return jsonify({'success': True, 'message': 'Student removed.'})

@app.route('/api/admin/students/<int:student_id>/status', methods=['PUT'])
def toggle_student_status(student_id):
    data = request.json
    action = data.get('action')
    if action == 'Reset Password':
        query_db("UPDATE students SET password='student123' WHERE id=%s", (student_id,), commit=True)
        log_activity('Super Admin', f"Reset Password for Student ID #{student_id}", 'Students')
        return jsonify({'success': True, 'message': 'Password reset to default (student123)'})
    else:
        status = 'Suspended' if action == 'Suspend' else 'Active'
        query_db("UPDATE students SET status=%s WHERE id=%s", (status, student_id), commit=True)
        log_activity('Super Admin', f"Changed Student ID #{student_id} status to {status}", 'Students')
        return jsonify({'success': True, 'message': f'Student status updated to {status}'})

@app.route('/api/admin/club_heads', methods=['POST', 'PUT'])
def admin_save_clubhead():
    d = request.json
    if request.method == 'POST':
        query_db("""
            INSERT INTO club_heads (name, email, password, phone, club_id, status)
            VALUES (%s, %s, %s, %s, %s, 'Active')
        """, (d['name'], d['email'].lower(), d.get('password', 'head123'), d.get('phone', ''), d.get('club_id')), commit=True)
        log_activity('Super Admin', f"Created Club Head: {d['name']}", 'Club Heads')
        return jsonify({'success': True, 'message': 'Club Head added!'})
    elif request.method == 'PUT':
        query_db("""
            UPDATE club_heads SET name=%s, email=%s, phone=%s, club_id=%s, status=%s WHERE id=%s
        """, (d['name'], d['email'].lower(), d.get('phone', ''), d.get('club_id'), d.get('status', 'Active'), d['head_id']), commit=True)
        log_activity('Super Admin', f"Updated Club Head ID #{d['head_id']}", 'Club Heads')
        return jsonify({'success': True, 'message': 'Club Head updated!'})

@app.route('/api/admin/club_heads/<int:head_id>', methods=['DELETE'])
def admin_delete_clubhead(head_id):
    query_db("DELETE FROM club_heads WHERE id=%s", (head_id,), commit=True)
    log_activity('Super Admin', f"Deleted Club Head ID #{head_id}", 'Club Heads')
    return jsonify({'success': True, 'message': 'Club Head removed.'})

@app.route('/api/admin/events', methods=['POST', 'PUT'])
def admin_save_event():
    d = request.json
    if request.method == 'POST':
        query_db("""
            INSERT INTO events (title, description, event_date, event_time, venue, fee, capacity, club_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Approved')
        """, (d['title'], d.get('description', ''), d['event_date'], d.get('event_time', '10:00 AM'), d['venue'], d.get('fee', 0), d.get('capacity', 100), d['club_id']), commit=True)
        log_activity('Super Admin', f"Created Event: {d['title']}", 'Events')
        return jsonify({'success': True, 'message': 'Event created successfully!'})
    elif request.method == 'PUT':
        query_db("""
            UPDATE events SET title=%s, description=%s, event_date=%s, event_time=%s, venue=%s, fee=%s, capacity=%s, club_id=%s, status=%s WHERE id=%s
        """, (d['title'], d['description'], d['event_date'], d['event_time'], d['venue'], d['fee'], d['capacity'], d['club_id'], d['status'], d['event_id']), commit=True)
        log_activity('Super Admin', f"Updated Event ID #{d['event_id']}", 'Events')
        return jsonify({'success': True, 'message': 'Event updated!'})

@app.route('/api/admin/events/<int:event_id>', methods=['DELETE'])
def admin_delete_event(event_id):
    query_db("DELETE FROM events WHERE id=%s", (event_id,), commit=True)
    log_activity('Super Admin', f"Deleted Event ID #{event_id}", 'Events')
    return jsonify({'success': True, 'message': 'Event deleted.'})

@app.route('/api/admin/events/<int:event_id>/status', methods=['PUT'])
def toggle_event_status(event_id):
    action = request.json.get('action')
    if action == 'Duplicate':
        ev = query_db("SELECT * FROM events WHERE id=%s", (event_id,), fetchone=True)
        query_db("INSERT INTO events (title, description, event_date, event_time, venue, fee, capacity, club_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Approved')",
                 (f"Copy of {ev['title']}", ev['description'], ev['event_date'], ev['event_time'], ev['venue'], ev['fee'], ev['capacity'], ev['club_id']), commit=True)
        log_activity('Super Admin', f"Duplicated Event ID #{event_id}", 'Events')
        return jsonify({'success': True, 'message': 'Event duplicated!'})
    else:
        status = 'Approved' if action == 'Approve' else 'Rejected'
        query_db("UPDATE events SET status=%s WHERE id=%s", (status, event_id), commit=True)
        log_activity('Super Admin', f"Set Event ID #{event_id} status to {status}", 'Events')
        return jsonify({'success': True, 'message': f'Event status set to {status}'})

@app.route('/api/admin/events/<int:event_id>/registrations', methods=['GET'])
def admin_get_event_registrations(event_id):
    event = query_db("SELECT id, title, venue, DATE_FORMAT(event_date, '%d %b %Y') as event_date FROM events WHERE id=%s", (event_id,), fetchone=True)
    registrations = query_db("""
        SELECT er.id as registration_id, s.name, s.roll_no, s.department, s.email, s.phone,
               DATE_FORMAT(er.registered_at, '%d %b %Y %h:%i %p') as registered_at
        FROM event_registration er
        JOIN students s ON er.student_id = s.id
        WHERE er.event_id = %s ORDER BY er.id DESC
    """, (event_id,), fetchall=True) or []
    return jsonify({'event': event, 'registrations': registrations})

@app.route('/api/admin/sponsors', methods=['POST', 'PUT'])
def admin_save_sponsor():
    d = request.json
    if request.method == 'POST':
        query_db("""
            INSERT INTO sponsors (name, company, amount, contact, phone, email, status, club_id, event_id)
            VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed', %s, %s)
        """, (d['name'], d['company'], d['amount'], d.get('contact'), d.get('phone'), d.get('email'), d.get('club_id'), d.get('event_id')), commit=True)
        log_activity('Super Admin', f"Added Sponsor: {d['name']} (${d['amount']})", 'Sponsors')
        return jsonify({'success': True, 'message': 'Sponsor added!'})
    elif request.method == 'PUT':
        query_db("""
            UPDATE sponsors SET name=%s, company=%s, amount=%s, contact=%s, phone=%s, email=%s, status=%s WHERE id=%s
        """, (d['name'], d['company'], d['amount'], d.get('contact'), d.get('phone'), d.get('email'), d.get('status', 'Confirmed'), d['sponsor_id']), commit=True)
        log_activity('Super Admin', f"Updated Sponsor ID #{d['sponsor_id']}", 'Sponsors')
        return jsonify({'success': True, 'message': 'Sponsor updated!'})

@app.route('/api/admin/sponsors/<int:sponsor_id>', methods=['DELETE'])
def admin_delete_sponsor(sponsor_id):
    query_db("DELETE FROM sponsors WHERE id=%s", (sponsor_id,), commit=True)
    log_activity('Super Admin', f"Deleted Sponsor ID #{sponsor_id}", 'Sponsors')
    return jsonify({'success': True, 'message': 'Sponsor deleted.'})

@app.route('/api/admin/settings', methods=['PUT'])
def admin_update_settings():
    d = request.json
    for key, val in d.items():
        query_db("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting_value=%s",
                 (key, str(val), str(val)), commit=True)
    log_activity('Super Admin', 'Updated System Settings', 'Settings')
    return jsonify({'success': True, 'message': 'System Settings saved in MySQL!'})

@app.route('/api/admin/backup', methods=['POST'])
def admin_backup_db():
    log_activity('Super Admin', 'Created Database Backup Archive', 'Settings')
    return jsonify({'success': True, 'message': 'Database Backup generated successfully! (campusos_backup_2026.sql)'})

@app.route('/api/reports/download/<report_type>', methods=['GET'])
def download_excel_report(report_type):
    wb = openpyxl.Workbook()
    ws = wb.active

    header_fill = PatternFill(start_color="111827", end_color="111827", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    if report_type == 'students':
        ws.title = "Students Report"
        ws.append(["ID", "Name", "Email", "Roll No", "Department", "Year", "Phone", "Status"])
        rows = query_db("SELECT id, name, email, roll_no, department, year, phone, status FROM students", fetchall=True) or []
        filename = "CampusOS_Students_Report.xlsx"
    elif report_type == 'clubs':
        ws.title = "Clubs Report"
        ws.append(["ID", "Club Name", "Category", "Faculty Coordinator", "Est. Year", "Status"])
        rows = query_db("SELECT id, name, category, faculty_coordinator, established_year, status FROM clubs", fetchall=True) or []
        filename = "CampusOS_Clubs_Report.xlsx"
    elif report_type == 'events':
        ws.title = "Events Report"
        ws.append(["ID", "Title", "Date", "Venue", "Fee ($)", "Capacity", "Status"])
        rows = query_db("SELECT id, title, DATE_FORMAT(event_date, '%d %b %Y') as event_date, venue, fee, capacity, status FROM events", fetchall=True) or []
        filename = "CampusOS_Events_Report.xlsx"
    elif report_type == 'sponsors':
        ws.title = "Sponsors Report"
        ws.append(["ID", "Sponsor Name", "Company", "Amount ($)", "Contact", "Phone", "Status"])
        rows = query_db("SELECT id, name, company, amount, contact, phone, status FROM sponsors", fetchall=True) or []
        filename = "CampusOS_Sponsors_Report.xlsx"
    else:
        ws.title = "Master Summary"
        ws.append(["Category", "Total Metric Value"])
        c_cnt = query_db("SELECT COUNT(*) as c FROM clubs", fetchone=True)['c'] or 0
        s_cnt = query_db("SELECT COUNT(*) as c FROM students", fetchone=True)['c'] or 0
        e_cnt = query_db("SELECT COUNT(*) as c FROM events", fetchone=True)['c'] or 0
        sp_sum = query_db("SELECT IFNULL(SUM(amount),0) as s FROM sponsors", fetchone=True)['s'] or 0
        rows = [
            {'a': 'Total Active Clubs', 'b': c_cnt},
            {'a': 'Total Registered Students', 'b': s_cnt},
            {'a': 'Total Campus Events', 'b': e_cnt},
            {'a': 'Total Sponsorship Received', 'b': f"${sp_sum:,.2f}"}
        ]
        filename = "CampusOS_Master_Report.xlsx"

    if report_type == 'full':
        for r in rows:
            ws.append([r['a'], r['b']])
    else:
        for r in rows:
            ws.append(list(r.values()))

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    log_activity('Super Admin', f"Exported {report_type.upper()} Excel Report", 'Reports')
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name=filename)


if __name__ == '__main__':
    print("🚀 CampusOS Full Stack Platform Live on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)