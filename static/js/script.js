// LOGIN SUBMIT HANDLER
async function handleLoginSubmit(e) {
    e.preventDefault();
    const role = window.currentSelectedRole || 'Student';
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role: role })
        });

        const data = await res.json();
        if (data.success) {
            localStorage.setItem('campusos_user', JSON.stringify(data.user));
            if (role === 'Super Admin') window.location.href = '/admin/dashboard';
            else if (role === 'Club Head') window.location.href = '/clubhead/dashboard';
            else window.location.href = '/student/dashboard';
        } else {
            alert(data.message);
        }
    } catch (err) {
        alert("Connection failed! Make sure Flask (app.py) is running.");
    }
}

// SIGNUP SUBMIT HANDLER
async function handleSignupSubmit(e) {
    e.preventDefault();
    const payload = {
        name: document.getElementById('reg-name').value.trim(),
        roll_no: document.getElementById('reg-roll').value.trim(),
        department: document.getElementById('reg-dept').value.trim(),
        year: document.getElementById('reg-year').value.trim(),
        email: document.getElementById('reg-email').value.trim(),
        phone: document.getElementById('reg-phone').value.trim(),
        password: document.getElementById('reg-pass').value.trim(),
        confirm_password: document.getElementById('reg-confirm-pass').value.trim()
    };

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        alert(data.message);
        if (data.success) {
            switchAuthTab('login');
            document.getElementById('login-email').value = payload.email;
            document.getElementById('login-password').value = payload.password;
        }
    } catch (err) {
        alert("Registration failed. Please check your MySQL database connection.");
    }
}