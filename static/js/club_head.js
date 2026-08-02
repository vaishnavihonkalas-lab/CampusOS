let currentClubHead = null;
let currentClubData = null;
let currentActiveEventId = null;

async function initClubHeadDashboard() {
    currentClubHead = JSON.parse(localStorage.getItem('campusos_user'));
    if (!currentClubHead || currentClubHead.role !== 'Club Head') {
        alert("Session expired. Please log in.");
        window.location.href = '/';
        return;
    }

    document.getElementById('head-name-display').innerText = currentClubHead.name;
    document.getElementById('club-name-display').innerText = currentClubHead.club_name || 'My Club';
    if (currentClubHead.avatar_url) {
        document.getElementById('head-avatar').src = currentClubHead.avatar_url;
    }

    loadDashboardData();
}

async function loadDashboardData() {
    try {
        const res = await fetch(`/api/clubhead/full_dashboard/${currentClubHead.club_id}`);
        if (!res.ok) throw new Error("API Error");
        const data = await res.json();
        currentClubData = data;

        // 1. STATS
        document.getElementById('st-members').innerText = data.stats.members;
        document.getElementById('st-events').innerText = data.stats.events_organized;
        document.getElementById('st-upcoming').innerText = data.stats.upcoming_events;
        document.getElementById('st-pending').innerText = data.stats.pending_requests;
        document.getElementById('pending-badge').innerText = data.stats.pending_requests;
        document.getElementById('st-sponsors').innerText = `$${data.stats.sponsorship_raised.toLocaleString()}`;
        document.getElementById('st-certs').innerText = data.stats.certificates_issued;

        // 2. CLUB INFO
        document.getElementById('info-club-name').innerText = data.club.name;
        document.getElementById('info-category').innerText = data.club.category;
        document.getElementById('info-coordinator').innerText = data.club.faculty_coordinator || 'Dr. S. K. Sharma';
        document.getElementById('info-year').innerText = data.club.established_year;
        document.getElementById('info-description').innerText = data.club.description;

        // Populate Edit Club Info Modal
        document.getElementById('edit-coord').value = data.club.faculty_coordinator || 'Dr. S. K. Sharma';
        document.getElementById('edit-year').value = data.club.established_year;
        document.getElementById('edit-desc').value = data.club.description;

        // 3. JOIN REQUESTS TABLE
        const reqTbody = document.getElementById('join-requests-tbl');
        if (data.join_requests && data.join_requests.length > 0) {
            reqTbody.innerHTML = data.join_requests.map(r => `
                <tr>
                    <td><strong>${r.name}</strong></td>
                    <td>${r.department}</td>
                    <td>${r.year}</td>
                    <td>${r.reason || 'N/A'}</td>
                    <td>${r.request_date}</td>
                    <td>
                        <button class="btn btn-success btn-sm" onclick="handleJoinRequestAction(${r.request_id}, 'Approve')">✔ Approve</button>
                        <button class="btn btn-danger btn-sm" onclick="handleJoinRequestAction(${r.request_id}, 'Reject')">✖ Reject</button>
                    </td>
                </tr>
            `).join('');
        } else {
            reqTbody.innerHTML = `<tr><td colspan="6" class="empty-msg">No pending requests</td></tr>`;
        }

        // 4. MEMBERS TABLE
        const memTbody = document.getElementById('members-list');
        if (data.members && data.members.length > 0) {
            memTbody.innerHTML = data.members.map(m => `
                <tr>
                    <td>${m.roll_no}</td>
                    <td><strong>${m.name}</strong></td>
                    <td>${m.department}</td>
                    <td>${m.year}</td>
                    <td>${m.email}</td>
                    <td>${m.phone || 'N/A'}</td>
                    <td><span style="color:var(--success); font-weight:bold;">${m.status}</span></td>
                    <td>${m.joined_date}</td>
                    <td><button class="btn btn-danger btn-sm" onclick="removeMember(${m.membership_id})">Remove</button></td>
                </tr>
            `).join('');
        } else {
            memTbody.innerHTML = `<tr><td colspan="9" class="empty-msg">No members found</td></tr>`;
        }

        // 5. EVENTS TABLE
        const evTbody = document.getElementById('events-list');
        if (data.events && data.events.length > 0) {
            evTbody.innerHTML = data.events.map(e => `
                <tr>
                    <td><strong>${e.title}</strong></td>
                    <td>${e.venue}</td>
                    <td>${e.event_date}</td>
                    <td>${e.event_time}</td>
                    <td>$${e.fee}</td>
                    <td>${e.reg_count} / ${e.capacity}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="openRegistrationsModal(${e.id})">👥 View Regs</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteEvent(${e.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        } else {
            evTbody.innerHTML = `<tr><td colspan="7" class="empty-msg">No events found</td></tr>`;
        }

        // 6. SPONSORS TABLE
        const spTbody = document.getElementById('sponsors-list');
        if (data.sponsors && data.sponsors.length > 0) {
            spTbody.innerHTML = data.sponsors.map(s => `
                <tr>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.company}</td>
                    <td>$${s.amount.toLocaleString()}</td>
                    <td>${s.contact || 'N/A'}</td>
                    <td>${s.phone || 'N/A'}</td>
                    <td>${s.email || 'N/A'}</td>
                    <td><button class="btn btn-danger btn-sm" onclick="deleteSponsor(${s.id})">Delete</button></td>
                </tr>
            `).join('');
        } else {
            spTbody.innerHTML = `<tr><td colspan="7" class="empty-msg">No sponsors found</td></tr>`;
        }

        // 7. ANNOUNCEMENTS
        const ancBox = document.getElementById('announcements-history-list');
        if (data.announcements && data.announcements.length > 0) {
            ancBox.innerHTML = data.announcements.map(a => `
                <div style="background:var(--bg-dark); padding:15px; border-radius:8px; margin-bottom:10px; border:1px solid var(--border-color);">
                    <h4 style="color:var(--accent);">${a.title}</h4>
                    <p style="font-size:13px; margin:5px 0;">${a.description}</p>
                    <small style="color:var(--text-muted);">${a.posted_at}</small>
                </div>
            `).join('');
        } else {
            ancBox.innerHTML = `<div class="empty-msg">No announcements posted</div>`;
        }

        // 8. GALLERY
        const galGrid = document.getElementById('gallery-grid');
        if (data.gallery && data.gallery.length > 0) {
            galGrid.innerHTML = data.gallery.map(g => `
                <div class="gallery-card">
                    <img src="${g.image_url}" alt="Gallery">
                    <p>${g.caption || ''}</p>
                    <button class="btn btn-danger btn-sm" style="margin:5px 10px 10px;" onclick="deleteGalleryItem(${g.id})">Delete</button>
                </div>
            `).join('');
        } else {
            galGrid.innerHTML = `<div class="empty-msg">No photos uploaded</div>`;
        }

        // 9. CERTIFICATES
        const certTbody = document.getElementById('certificates-list');
        if (data.certificates && data.certificates.length > 0) {
            certTbody.innerHTML = data.certificates.map(c => `
                <tr>
                    <td><code>${c.certificate_code}</code></td>
                    <td><strong>${c.student_name}</strong></td>
                    <td>${c.roll_no}</td>
                    <td>${c.event_title}</td>
                    <td>${c.issued_date}</td>
                </tr>
            `).join('');
        } else {
            certTbody.innerHTML = `<tr><td colspan="5" class="empty-msg">No certificates issued</td></tr>`;
        }

        // 10. NOTIFICATIONS
        const notifBox = document.getElementById('notif-list');
        if (data.notifications && data.notifications.length > 0) {
            notifBox.innerHTML = data.notifications.map(n => `
                <div style="padding:10px 0; border-bottom:1px solid var(--border-color);">
                    <strong style="font-size:12px; color:var(--accent);">${n.title}</strong>
                    <p style="font-size:12px; margin-top:2px;">${n.message}</p>
                </div>
            `).join('');
        } else {
            notifBox.innerHTML = `<div class="empty-msg">No notifications</div>`;
        }

        // Render Analytics Charts
        renderAnalyticsCharts(data);

    } catch (err) {
        console.error(err);
    }
}

// TAB SWITCHING
function switchDashboardTab(tabId, btnElement) {
    document.querySelectorAll('.tab-section').forEach(sec => sec.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    document.getElementById(`tab-${tabId}`).classList.add('active');
    if (btnElement) btnElement.classList.add('active');
}

// ACTION HANDLERS
async function handleJoinRequestAction(reqId, action) {
    const res = await fetch('/api/clubhead/join_request/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_id: reqId, action: action })
    });
    const d = await res.json();
    alert(d.message);
    loadDashboardData();
}

async function removeMember(memId) {
    if (confirm("Remove student from club?")) {
        await fetch(`/api/clubhead/member/${memId}`, { method: 'DELETE' });
        loadDashboardData();
    }
}

async function handleSaveClubInfo(e) {
    e.preventDefault();
    await fetch('/api/clubhead/update_club', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            club_id: currentClubHead.club_id,
            faculty_coordinator: document.getElementById('edit-coord').value,
            established_year: document.getElementById('edit-year').value,
            description: document.getElementById('edit-desc').value
        })
    });
    closeModal('edit-club-modal');
    loadDashboardData();
}

async function handleCreateEvent(e) {
    e.preventDefault();
    await fetch('/api/clubhead/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            club_id: currentClubHead.club_id,
            title: document.getElementById('ev-title').value,
            venue: document.getElementById('ev-venue').value,
            event_date: document.getElementById('ev-date').value,
            event_time: document.getElementById('ev-time').value,
            fee: document.getElementById('ev-fee').value,
            capacity: document.getElementById('ev-cap').value,
            description: document.getElementById('ev-desc').value
        })
    });
    closeModal('create-event-modal');
    loadDashboardData();
}

async function deleteEvent(id) {
    if (confirm("Delete event?")) {
        await fetch(`/api/clubhead/events/${id}`, { method: 'DELETE' });
        loadDashboardData();
    }
}

async function openRegistrationsModal(eventId) {
    currentActiveEventId = eventId;
    openModal('registrations-modal');

    const res = await fetch(`/api/clubhead/event/${eventId}/registrations`);
    const data = await res.json();

    document.getElementById('reg-modal-title').innerText = `Registrations - ${data.event.title}`;

    const tbody = document.getElementById('event-regs-list');
    if (data.registrations && data.registrations.length > 0) {
        tbody.innerHTML = data.registrations.map(r => `
            <tr>
                <td><strong>${r.name}</strong></td>
                <td>${r.roll_no}</td>
                <td>${r.department}</td>
                <td>
                    <input type="checkbox" ${r.attendance_status === 'Present' ? 'checked' : ''} 
                           onchange="markAttendanceAction(${r.student_id}, this.checked)"> Present
                </td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="generateCertAction(${r.student_id})">📜 Cert</button>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-msg">No registrations yet</td></tr>`;
    }
}

async function markAttendanceAction(studentId, isChecked) {
    await fetch('/api/clubhead/event/mark_attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            event_id: currentActiveEventId,
            student_id: studentId,
            status: isChecked ? 'Present' : 'Absent'
        })
    });
}

async function generateCertAction(studentId) {
    const res = await fetch('/api/clubhead/certificates/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: currentActiveEventId, student_id: studentId })
    });
    const d = await res.json();
    alert(d.message);
    loadDashboardData();
}

async function handleAddSponsor(e) {
    e.preventDefault();
    await fetch('/api/clubhead/sponsors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            club_id: currentClubHead.club_id,
            name: document.getElementById('sp-name').value,
            company: document.getElementById('sp-comp').value,
            amount: document.getElementById('sp-amount').value,
            contact: document.getElementById('sp-contact').value,
            phone: document.getElementById('sp-phone').value,
            email: document.getElementById('sp-email').value
        })
    });
    closeModal('add-sponsor-modal');
    loadDashboardData();
}

async function deleteSponsor(id) {
    if (confirm("Delete sponsor?")) {
        await fetch(`/api/clubhead/sponsors/${id}`, { method: 'DELETE' });
        loadDashboardData();
    }
}

async function handlePostAnnouncement(e) {
    e.preventDefault();
    await fetch('/api/clubhead/announcements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            club_id: currentClubHead.club_id,
            title: document.getElementById('anc-title').value,
            description: document.getElementById('anc-desc').value
        })
    });
    alert("Announcement posted!");
    loadDashboardData();
}

async function handleUploadGallery(e) {
    e.preventDefault();
    await fetch('/api/clubhead/gallery', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            club_id: currentClubHead.club_id,
            image_url: document.getElementById('gal-url').value,
            caption: document.getElementById('gal-caption').value
        })
    });
    loadDashboardData();
}

async function deleteGalleryItem(id) {
    if (confirm("Delete image?")) {
        await fetch(`/api/clubhead/gallery/${id}`, { method: 'DELETE' });
        loadDashboardData();
    }
}

function exportMembersExcel() {
    window.location.href = `/api/export/club_members/${currentClubHead.club_id}`;
}

// MODAL CONTROLLERS
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function openEditClubModal() { openModal('edit-club-modal'); }

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
function renderAnalyticsCharts(data) {
    const ctx1 = document.getElementById('registrationsChart').getContext('2d');
    const ctx2 = document.getElementById('membersChart').getContext('2d');

    if (chartRegs) chartRegs.destroy();
    if (chartMems) chartMems.destroy();

    chartRegs = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: data.events.map(e => e.title),
            datasets: [{ label: 'Registrations', data: data.events.map(e => e.reg_count), borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.2)', fill: true }]
        }
    });

    chartMems = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ['Approved Members', 'Pending Requests'],
            datasets: [{ label: 'Students Count', data: [data.stats.members, data.stats.pending_requests], backgroundColor: ['#10b981', '#f59e0b'] }]
        }
    });
}