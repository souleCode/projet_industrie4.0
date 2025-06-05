const serverUrl = "http://localhost:5000";

// ======================
// Login Page Handling
// ======================
if (document.getElementById('email')) {
    document.querySelector('form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        fetch(`${serverUrl}/login`, {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: email, password })
        })
        .then(response => {
            if (!response.ok) throw new Error('Invalid credentials');
            return response.json();
        })
        .then(data => {
            localStorage.setItem("jwt_token", data.token);
            window.location.href = "/dashboard";
        })
        .catch(error => {
            alert(error.message);
            console.error("Login error:", error);
        });
    });
}

// ======================
// Dashboard Handling
// ======================
if (document.querySelector('.pcs-table')) {
    // Authentication check
    if (!localStorage.getItem("jwt_token")) {
        window.location.href = "/login";
    }

    // Event Listeners
    document.querySelector('.logout-btn').addEventListener('click', () => {
        localStorage.removeItem("jwt_token");
        window.location.href = "/login";
    });

    document.querySelector('.action-btn.shutdown').addEventListener('click', shutdownAllOnline);
    document.getElementById('refresh-pcs-btn').addEventListener('click', pingPCs);

    // Initial load
    loadPCs();
    setInterval(loadPCs, 30000);
}

// ======================
// Core Functions
// ======================
function loadPCs() {
    fetch(`${serverUrl}/list-pcs`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem("jwt_token")}` }
    })
    .then(response => response.json())
    .then(pcs => {
        const tbody = document.querySelector('.pcs-table tbody');
        tbody.innerHTML = '';
        
        pcs.forEach(pc => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${pc.name}</td>
                <td>${pc.ip}</td>
                <td><span class="status ${pc.status}">${pc.status === 'online' ? 'Online' : 'Offline'}</span></td>
                <td><button class="shutdown-btn" onclick="shutdownPC('${pc.ip}')">Shutdown</button></td>
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => console.error("Error loading PCs:", error));
}

function shutdownPC(ip) {
    fetch(`${serverUrl}/trigger-shutdown`, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${localStorage.getItem("jwt_token")}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: ip })
    })
    .then(response => {
        if (!response.ok) throw new Error('Shutdown failed');
        loadPCs();
        alert('Shutdown command sent successfully');
    })
    .catch(error => {
        alert(error.message);
        console.error("Shutdown error:", error);
    });
}

function shutdownAllOnline() {
    fetch(`${serverUrl}/shutdown-all-online`, {
        method: "POST",
        headers: { 'Authorization': `Bearer ${localStorage.getItem("jwt_token")}` }
    })
    .then(response => {
        if (!response.ok) throw new Error('Global shutdown failed');
        loadPCs();
        alert('Shutdown command sent to all online PCs');
    })
    .catch(error => {
        alert(error.message);
        console.error("Global shutdown error:", error);
    });
}

function pingPCs() {
    fetch(`${serverUrl}/ping-pcs`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem("jwt_token")}` }
    })
    .then(() => {
        loadPCs();
        alert('PC statuses refreshed');
    })
    .catch(error => console.error("Refresh error:", error));
}

// ======================
// Schedule Shutdown Function
// ======================
if (document.getElementById('schedule-shutdown-btn')) {
    document.getElementById('schedule-shutdown-btn').addEventListener('click', scheduleShutdown);
}

function scheduleShutdown() {
    const shutdownTime = prompt("Entrez l'heure d'extinction (format 24h HH:MM):");
    
    if (shutdownTime) {
        fetch(`${serverUrl}/schedule-shutdown`, {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${localStorage.getItem("jwt_token")}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ time: shutdownTime })
        })
        .then(response => {
            if (!response.ok) throw new Error('Échec de la planification');
            alert(`Extinction planifiée pour ${shutdownTime}`);
        })
        .catch(error => {
            alert(error.message);
            console.error("Erreur de planification:", error);
        });
    }
}

// Make functions available globally
window.shutdownPC = shutdownPC;
