<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Death Switch AI - Control Panel</title>
    <style>
        /* [All previous CSS remains unchanged] */
        /* ... CSS code from previous version ... */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💙 Digital Death Switch AI</h1>
            <p class="subtitle">Life-Trigger Automation System</p>
        </div>

        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard', event)">📊 Dashboard</button>
            <button class="nav-tab" onclick="showTab('recipients', event)">👥 Recipients</button>
            <button class="nav-tab" onclick="showTab('documents', event)">📄 Documents</button>
            <button class="nav-tab" onclick="showTab('settings', event)">⚙️ Settings</button>
            <button class="nav-tab" onclick="showTab('monitoring', event)">🔍 Monitoring</button>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="status-card">
                <div class="status-indicator">✅</div>
                <h2>System Active</h2>
                <p>Last activity: <span id="last-activity">Loading...</span></p>
                <p>Next check: <span id="next-check">Loading...</span></p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="dashboard-recipients">0</div>
                    <div>Recipients</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="dashboard-documents">0</div>
                    <div>Documents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="dashboard-days">0</div>
                    <div>Days Remaining</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="dashboard-activities">0</div>
                    <div>Activities Logged</div>
                </div>
            </div>

            <div class="card">
                <h3>Quick Actions</h3>
                <button class="btn btn-success" onclick="recordActivity()">🔄 Record Activity</button>
                <button class="btn" onclick="testSystem()">🧪 Test System</button>
                <button class="btn btn-danger" onclick="showKillSwitch()">🚫 Kill Switch</button>
            </div>

            <div class="card">
                <h3>Recent Activity Log</h3>
                <div class="activity-log" id="activity-log">
                    <!-- Activity items will be fetched -->
                </div>
            </div>
        </div>

        <!-- Recipients Tab -->
        <div id="recipients" class="tab-content">
            <div class="card">
                <h3>📝 Add New Recipient</h3>
                <form id="recipient-form" data-user-id="{{ current_user.id }}">
                    <div class="form-group">
                        <label>Full Name *</label>
                        <input type="text" id="recipient-name" required>
                    </div>
                    <div class="form-group">
                        <label>Email Address *</label>
                        <input type="email" id="recipient-email" required>
                    </div>
                    <div class="form-group">
                        <label>Phone Number *</label>
                        <input type="tel" id="recipient-phone" placeholder="+91xxxxxxxxxx" required>
                    </div>
                    <div class="form-group">
                        <label>WhatsApp Number</label>
                        <input type="tel" id="recipient-whatsapp" placeholder="Same as phone if empty">
                    </div>
                    <div class="form-group">
                        <label>Preferred Language *</label>
                        <select id="recipient-language" required>
                            <option value="english">English</option>
                            <option value="hindi">Hindi (हिंदी)</option>
                            <option value="telugu">Telugu (తెలుగు)</option>
                            <option value="tamil">Tamil (தமிழ்)</option>
                            <option value="kannada">Kannada (ಕನ್ನಡ)</option>
                            <option value="malayalam">Malayalam (മലയാളം)</option>
                            <option value="spanish">Spanish (Español)</option>
                            <option value="french">French (Français)</option>
                        </select>
                    </div>
                    <button type="submit" class="btn">📂 Save Recipient</button>
                </form>
            </div>
        </div>

    </div>

    <script>
    function showTab(tabId, event) {
        const allTabs = document.querySelectorAll(".tab-content");
        const allButtons = document.querySelectorAll(".nav-tab");

        allTabs.forEach(tab => tab.classList.remove("active"));
        allButtons.forEach(btn => btn.classList.remove("active"));

        document.getElementById(tabId).classList.add("active");
        if (event) event.target.classList.add("active");
    }

    document.addEventListener("DOMContentLoaded", function () {
        fetch("/status")
            .then(res => res.json())
            .then(data => {
                document.getElementById("last-activity").textContent = data.last_activity || "N/A";
                document.getElementById("next-check").textContent = `${data.days_remaining || 0} days`;
                document.getElementById("dashboard-recipients").textContent = data.recipient_count || 0;
                document.getElementById("dashboard-documents").textContent = data.document_count || 0;
                document.getElementById("dashboard-days").textContent = data.days_remaining || 0;
                document.getElementById("dashboard-activities").textContent = data.activity_log_count || 0;

                const logEl = document.getElementById("activity-log");
                if (Array.isArray(data.activity_log)) {
                    logEl.innerHTML = data.activity_log.map(entry => `<div>${entry}</div>`).join('');
                }
            });

        document.getElementById("recipient-form").addEventListener("submit", function (e) {
            e.preventDefault();
            const userId = e.target.getAttribute("data-user-id");
            const recipient = {
                name: document.getElementById("recipient-name").value,
                email: document.getElementById("recipient-email").value,
                phone: document.getElementById("recipient-phone").value,
                whatsapp: document.getElementById("recipient-whatsapp").value || document.getElementById("recipient-phone").value,
                language: document.getElementById("recipient-language").value,
                user_id: userId
            };

            fetch("/add-recipient", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(recipient)
            })
            .then(res => res.json())
            .then(data => {
                alert(data.status || "Recipient added!");
                location.reload();
            })
            .catch(err => alert("Error adding recipient"));
        });
    });
    </script>
</body>
</html>
