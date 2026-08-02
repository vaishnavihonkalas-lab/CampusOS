let currentAdminUser = null;
let masterAdminData = null;

async function initAdminDashboard() {
    currentAdminUser = JSON.parse(localStorage.getItem('campusos_user'));
    if (!currentAdminUser || currentAdminUser.role !== 'Super Admin') {
        alert("Session expired. Super Admin login required.");
        window.location.href = '/';
        return;
    }

    document.getElementById('admin-name-display').innerText = currentAdminUser.name;
    if (currentAdminUser.avatar_url) {
        document.getElementById('admin-avatar').src = currentAdminUser.avatar_url;
    }

    loadMasterDashboardData();
}

async function loadMasterDashboardData() {
    try {
        const res = await fetch('/api/admin/full_dashboard');
        if (!res.ok) throw new Error("API Error");
        const data = await res.json();
        masterAdminData = data;

        // 1. STATS CARDS
        document.getElementById('ad-clubs').innerText = data.stats.clubs;
        document.getElementById('ad-students').innerText = data.stats.students;
        document.getElementById('ad-heads').innerText = data.stats.heads;
        document.getElementById('ad-events').innerText = data.stats.events;
        document.getElementById('ad-upcoming').innerText = data.stats.upcoming;
        document.getElementById('ad-sponsors').innerText = `$${data.stats.sponsors_amount.toLocaleString()}`;
        document.getElementById('ad-regs').innerText = data.stats.registrations;
        document.getElementById('ad-certs').innerText = data.stats.certificates;

        // 2. RECENT ACTIVITY LOGS
        const logBox = document.getElementById('recent-activity-list');
        if (data.activity_logs && data.activity_logs.length > 0) {
            logBox.innerHTML = data.activity_logs.slice(0, 6).map(l => `
                <div style="padding:10px 0; border-bottom:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="font-size:13px; color:var(--accent);">${l.action}</strong>
                        <div style="font-size:11px; color:var(--text-muted);">${l.user_name} • ${l.module}</div>
                    </div>
                    <small style="color:var(--text-muted); font-size:11px;">${l.created_at_fmt}</small>
                </div>
            `).join('');
        }

        // 3. CLUBS TABLE
        renderClubsTable(data.clubs);

        // 4. STUDENTS TABLE
        renderStudentsTable(data.students);

        // 5. CLUB HEADS TABLE
        renderClubHeadsTable(data.club_heads);

        // 6. EVENTS TABLE
        renderEventsTable(data.events);

        // 7. SPONSORS TABLE
        renderSponsorsTable(data.sponsors);

        // 8. AUDIT LOGS FULL TABLE
        renderAuditLogsTable(data.activity_logs);

        // 9. SETTINGS
        if (data.settings) {
            if(document.getElementById('set-college')) document.getElementById('edit-college-name').value = data.settings.college_name || '';
            if(document.getElementById('set-year')) document.getElementById('edit-academic-year').value = data.settings.academic_year || '';
        }

        // 10. CHARTS
        renderCharts(data.charts);

    } catch (err) {
        console.error(err);
    }
}

// RENDERERS
function renderClubsTable(clubs) {
    const tbody = document.getElementById('clubs-list');
    if (clubs && clubs.length > 0) {
        tbody.innerHTML = clubs.map(c => `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td>${c.category}</td>
                <td>${c.faculty_coordinator || 'Dr. S. K. Sharma'}</td>
                <td>${c.head_name || 'Unassigned'}</td>
                <td>${c.members_count}</td>
                <td>${c.events_count}</td>
                <td><span class="badge ${c.status === 'Active' ? 'badge-success' : 'badge-danger'}">${c.status}</span></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="toggleClubStatus(${c.id}, '${c.status === 'Active' ? 'Disabled' : 'Active'}')">${c.status === 'Active' ? 'Disable' : 'Enable'}</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteClub(${c.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-msg">No clubs registered</td></tr>`;
    }
}

function renderStudentsTable(students) {
    const tbody = document.getElementById('students-list');
    if (students && students.length > 0) {
        tbody.innerHTML = students.map(s => `
            <tr>
                <td><code>${s.roll_no}</code></td>
                <td><strong>${s.name}</strong></td>
                <td>${s.department}</td>
                <td>${s.year}</td>
                <td>${s.email}</td>
                <td>${s.phone || 'N/A'}</td>
                <td>${s.registered_events_count} Events</td>
                <td><span class="badge ${s.status === 'Active' ? 'badge-success' : 'badge-danger'}">${s.status}</span></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="toggleStudentStatus(${s.id}, '${s.status === 'Active' ? 'Suspend' : 'Activate'}')">${s.status === 'Active' ? 'Suspend' : 'Activate'}</button>
                    <button class="btn btn-secondary btn-sm" onclick="toggleStudentStatus(${s.id}, 'Reset Password')">Reset Pass</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteStudent(${s.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="9" class="empty-msg">No students registered</td></tr>`;
    }
}

function renderClubHeadsTable(heads) {
    const tbody = document.getElementById('clubheads-list');
    if (heads && heads.length > 0) {
        tbody.innerHTML = heads.map(h => `
            <tr>
                <td><strong>${h.name}</strong></td>
                <td><span class="badge badge-accent">${h.club_name || 'Unassigned'}</span></td>
                <td>${h.email}</td>
                <td>${h.phone || 'N/A'}</td>
                <td>${h.created_at_fmt}</td>
                <td><span class="badge badge-success">${h.status}</span></td>
                <td><button class="btn btn-danger btn-sm" onclick="deleteClubHead(${h.id})">Delete</button></td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-msg">No club heads assigned</td></tr>`;
    }
}

function renderEventsTable(events) {
    const tbody = document.getElementById('events-list');
    if (events && events.length > 0) {
        tbody.innerHTML = events.map(e => `
            <tr>
                <td><strong>${e.title}</strong></td>
                <td>${e.club_name || 'General'}</td>
                <td>${e.venue}</td>
                <td>${e.event_date_fmt}</td>
                <td>$${e.fee}</td>
                <td>${e.registered_count} / ${e.capacity}</td>
                <td><span class="badge ${e.status === 'Approved' ? 'badge-success' : 'badge-warning'}">${e.status}</span></td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="viewEventRegistrations(${e.id})">👥 View Regs</button>
                    <button class="btn btn-secondary btn-sm" onclick="duplicateEvent(${e.id})">📋 Duplicate</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteEvent(${e.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-msg">No events created</td></tr>`;
    }
}

function renderSponsorsTable(sponsors) {
    const tbody = document.getElementById('sponsors-list');
    if (sponsors && sponsors.length > 0) {
        tbody.innerHTML = sponsors.map(s => `
            <tr>
                <td><strong>${s.name}</strong></td>
                <td>${s.company}</td>
                <td>$${s.amount.toLocaleString()}</td>
                <td>${s.contact || 'N/A'}</td>
                <td>${s.club_name || 'General Campus'}</td>
                <td><span class="badge badge-success">${s.status}</span></td>
                <td><button class="btn btn-danger btn-sm" onclick="deleteSponsor(${s.id})">Delete</button></td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-msg">No sponsors found</td></tr>`;
    }
}

function renderAuditLogsTable(logs) {
    const tbody = document.getElementById('audit-logs-list');
    if (tbody && logs && logs.length > 0) {
        tbody.innerHTML = logs.map(l => `
            <tr>
                <td><strong>${l.user_name}</strong></td>
                <td>${l.action}</td>
                <td><span class="badge badge-accent">${l.module}</span></td>
                <td><code>${l.ip_address}</code></td>
                <td>${l.created_at_fmt}</td>
            </tr>
        `).join('');
    }
}

// NAVIGATION ROUTER
function navigateAdminSection(sectionId, linkElement) {
    document.querySelectorAll('.admin-section').forEach(sec => sec.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(li => li.classList.remove('active'));

    const targetSec = document.getElementById(`sec-${sectionId}`);
    if (targetSec) targetSec.classList.add('active');

    if (linkElement) {
        linkElement.parentElement.classList.add('active');
    }
}

// ACTION HANDLERS
async function toggleClubStatus(clubId, newStatus) {
    await fetch(`/api/admin/clubs/${clubId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    });
    loadMasterDashboardData();
}

async function deleteClub(clubId) {
    if (confirm("Delete club and all associated records?")) {
        await fetch(`/api/admin/clubs/${clubId}`, { method: 'DELETE' });
        loadMasterDashboardData();
    }
}

async function toggleStudentStatus(studentId, action) {
    const res = await fetch(`/api/admin/students/${studentId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
    });
    const d = await res.json();
    alert(d.message);
    loadMasterDashboardData();
}

async function deleteStudent(studentId) {
    if (confirm("Delete student?")) {
        await fetch(`/api/admin/students/${studentId}`, { method: 'DELETE' });
        loadMasterDashboardData();
    }
}

async function deleteClubHead(headId) {
    if (confirm("Remove club head?")) {
        await fetch(`/api/admin/club_heads/${headId}`, { method: 'DELETE' });
        loadMasterDashboardData();
    }
}

async function duplicateEvent(eventId) {
    await fetch(`/api/admin/events/${eventId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'Duplicate' })
    });
    loadMasterDashboardData();
}

async function deleteEvent(eventId) {
    if (confirm("Delete event?")) {
        await fetch(`/api/admin/events/${eventId}`, { method: 'DELETE' });
        loadMasterDashboardData();
    }
}

async function deleteSponsor(sponsorId) {
    if (confirm("Delete sponsor?")) {
        await fetch(`/api/admin/sponsors/${sponsorId}`, { method: 'DELETE' });
        loadMasterDashboardData();
    }
}

async function viewEventRegistrations(eventId) {
    openModal('registrations-modal');
    const res = await fetch(`/api/admin/events/${eventId}/registrations`);
    const data = await res.json();

    document.getElementById('reg-modal-title').innerText = `Registrations - ${data.event.title}`;
    const tbody = document.getElementById('event-regs-list');

    if (data.registrations && data.registrations.length > 0) {
        tbody.innerHTML = data.registrations.map(r => `
            <tr>
                <td><strong>${r.name}</strong></td>
                <td>${r.roll_no}</td>
                <td>${r.department}</td>
                <td>${r.email}</td>
                <td>${r.registered_at}</td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-msg">No registrations yet</td></tr>`;
    }
}

async function handleCreateClubSubmit(e) {
    e.preventDefault();
    await fetch('/api/admin/clubs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: document.getElementById('c-name').value,
            category: document.getElementById('c-cat').value,
            faculty_coordinator: document.getElementById('c-coord').value,
            established_year: document.getElementById('c-year').value,
            description: document.getElementById('c-desc').value
        })
    });
    closeModal('create-club-modal');
    loadMasterDashboardData();
}

async function handleCreateStudentSubmit(e) {
    e.preventDefault();
    await fetch('/api/admin/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: document.getElementById('st-name').value,
            roll_no: document.getElementById('st-roll').value,
            department: document.getElementById('st-dept').value,
            year: document.getElementById('st-year').value,
            email: document.getElementById('st-email').value,
            phone: document.getElementById('st-phone').value
        })
    });
    closeModal('create-student-modal');
    loadMasterDashboardData();
}

async function handleCreateEventSubmit(e) {
    e.preventDefault();
    await fetch('/api/admin/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: document.getElementById('ev-title').value,
            club_id: document.getElementById('ev-club').value,
            venue: document.getElementById('ev-venue').value,
            event_date: document.getElementById('ev-date').value,
            event_time: document.getElementById('ev-time').value,
            fee: document.getElementById('ev-fee').value,
            capacity: document.getElementById('ev-cap').value,
            description: document.getElementById('ev-desc').value
        })
    });
    closeModal('create-event-modal');
    loadMasterDashboardData();
}

async function handleSaveSettingsSubmit(e) {
    e.preventDefault();
    await fetch('/api/admin/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            college_name: document.getElementById('edit-college-name').value,
            academic_year: document.getElementById('edit-academic-year').value
        })
    });
    alert("System Settings Saved!");
    loadMasterDashboardData();
}

async function triggerBackup() {
    const res = await fetch('/api/admin/backup', { method: 'POST' });
    const d = await res.json();
    alert(d.message);
    loadMasterDashboardData();
}

function exportReportExcel(reportType) {
    window.location.href = `/api/reports/download/${reportType}`;
}

// MODAL & NAVIGATION HELPERS
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function filterTable(tableId, query) {
    const filter = query.toLowerCase();
    document.querySelectorAll(`#${tableId} tbody tr`).forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(filter) ? '' : 'none';
    });
}

function logout() {
    localStorage.removeItem('campusos_user');
    window.location.href = '/';
}

function goBack() { window.history.back(); }

// CHARTS
let chartRegs = null, chartMems = null;
function renderCharts(chartData) {
    const ctx1 = document.getElementById('eventRegsChart').getContext('2d');
    const ctx2 = document.getElementById('clubMembersChart').getContext('2d');

    if (chartRegs) chartRegs.destroy();
    if (chartMems) chartMems.destroy();

    chartRegs = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: chartData.event_regs.map(e => e.title),
            datasets: [{ label: 'Registrations', data: chartData.event_regs.map(e => e.count), backgroundColor: '#38bdf8' }]
        }
    });

    chartMems = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: chartData.club_members.map(c => c.name),
            datasets: [{ data: chartData.club_members.map(c => c.count), backgroundColor: ['#38bdf8', '#8b5cf6', '#10b981', '#f59e0b'] }]
        }
    });
}