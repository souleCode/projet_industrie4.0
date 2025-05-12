const serverUrl = "http://localhost:5000";

function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch(`${serverUrl}/login`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            alert("Login successful!");
            localStorage.setItem("jwt_token", data.token);
            document.getElementById("login-form").style.display = "none";
            document.getElementById("pc-list").style.display = "block";
            document.getElementById("refresh-btn").style.display = "block";
            loadPCs(); // Load the PCs initially
        } else {
            alert("Invalid credentials.");
        }
    })
    .catch(error => console.error("Error during login:", error));
}

function loadPCs() {
    const token = localStorage.getItem("jwt_token");
    const status = document.getElementById("status-filter").value;  // Get filter value

    fetch(`${serverUrl}/list-pcs?status=${status}`, {
        method: "GET",
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const listDiv = document.getElementById("pc-list-content");
        listDiv.innerHTML = "";

        data.forEach(pc => {
            const pcDiv = document.createElement("div");
            pcDiv.className = "pc-item";
            pcDiv.innerHTML = `
                <strong>${pc.name} (${pc.ip})</strong> - ${pc.status}
                <button onclick="shutdownPC('${pc.ip}')">🔴 Shutdown</button>
            `;
            listDiv.appendChild(pcDiv);
        });
    })
    .catch(error => console.error("Error loading PCs:", error));
}

function shutdownPC(ip) {
    const token = localStorage.getItem("jwt_token");
    fetch(`${serverUrl}/trigger-shutdown`, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: ip })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        loadPCs(); // Refresh the list
    })
    .catch(error => console.error("Error shutting down PC:", error));
}

function shutdownAllOnline() {
    const token = localStorage.getItem("jwt_token");

    fetch(`${serverUrl}/shutdown-all-online`, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadPCs(); // Refresh the list
    })
    .catch(error => console.error("Error shutting down all online PCs:", error));
}

function scheduleShutdown() {
    const shutdownTime = prompt("Enter time for shutdown (24-hour format: HH:MM):");

    if (shutdownTime) {
        alert(`Shutdown scheduled for ${shutdownTime}`);
        fetch(`${serverUrl}/schedule-shutdown`, {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${localStorage.getItem("jwt_token")}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ time: shutdownTime })
        })
        .then(response => response.json())
        .then(data => {
            alert(`Shutdown scheduled for ${shutdownTime}`);
        })
        .catch(error => console.error("Error scheduling shutdown:", error));
    }
}

function pingPCs() {
    const token = localStorage.getItem("jwt_token");
    fetch(`${serverUrl}/ping-pcs`, {
        method: "GET",
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        alert("Status refreshed!");
        loadPCs(); // Refresh the list
    })
    .catch(error => console.error("Error pinging PCs:", error));
}

// Auto-refresh every 30 seconds
setInterval(loadPCs, 30000);
