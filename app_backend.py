from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import threading
import secrets
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
CORS(app)

# Simple database initialization
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('death_switch.db')
    cursor = conn.cursor()
    
    # Activity log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            activity_type TEXT NOT NULL,
            device_id TEXT,
            notes TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Create necessary directories
os.makedirs("secure_docs", exist_ok=True)
os.makedirs("config", exist_ok=True)

# Global system state
system_state = {
    'initialized': True,
    'is_running': True,
    'last_activity': datetime.now(),
    'inactivity_days': 10,
    'verification_hours': 48
}

@app.route("/")
def index():
    """Serve the main web interface"""
    try:
        return send_from_directory('.', 'complete_web_interface.html')
    except FileNotFoundError:
        return jsonify({
            "error": "Web interface not found", 
            "message": "complete_web_interface.html is missing"
        }), 404

@app.route("/health")
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        "status": "healthy",
        "initialized": system_state['initialized'],
        "environment": os.getenv("FLASK_ENV", "production"),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/status", methods=["GET"])
def get_status():
    """Get system status"""
    try:
        # Get recipients count
        recipients_count = 0
        recipients_path = os.path.join("config", "recipients.json")
        if os.path.exists(recipients_path):
            with open(recipients_path, "r") as f:
                recipients = json.load(f)
                recipients_count = len(recipients)
        
        # Get documents count
        documents_count = 0
        documents_path = os.path.join("config", "documents.json")
        if os.path.exists(documents_path):
            with open(documents_path, "r") as f:
                documents = json.load(f)
                documents_count = len(documents)
        
        # Calculate days remaining
        last_activity = get_last_activity()
        days_remaining = system_state['inactivity_days']
        if last_activity:
            days_since = (datetime.now() - last_activity).days
            days_remaining = max(0, system_state['inactivity_days'] - days_since)
        
        return jsonify({
            "system": "active" if system_state['is_running'] else "inactive",
            "last_activity": str(last_activity) if last_activity else "Never",
            "days_remaining": days_remaining,
            "initialized": system_state['initialized'],
            "recipients_count": recipients_count,
            "documents_count": documents_count
        })
    except Exception as e:
        return jsonify({"error": f"Status check failed: {str(e)}"}), 500

def get_last_activity():
    """Get last activity from database"""
    try:
        conn = sqlite3.connect('death_switch.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM activity_log")
        result = cursor.fetchone()[0]
        conn.close()
        
        if result:
            return datetime.fromisoformat(result)
        return None
    except Exception:
        return system_state['last_activity']

def log_activity(activity_type, device_id=None, notes=None):
    """Log activity to database"""
    try:
        conn = sqlite3.connect('death_switch.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_log (activity_type, device_id, notes) VALUES (?, ?, ?)",
            (activity_type, device_id, notes)
        )
        conn.commit()
        conn.close()
        system_state['last_activity'] = datetime.now()
        return True
    except Exception as e:
        print(f"Failed to log activity: {e}")
        return False

@app.route("/record-activity", methods=["POST"])
def record_activity():
    """Record user activity to reset death timer"""
    try:
        user_agent = request.headers.get('User-Agent', 'Unknown')
        success = log_activity(
            "manual_check_in", 
            device_id=request.remote_addr,
            notes=f"Web UI check-in from {user_agent}"
        )
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Activity recorded successfully - death timer reset!"
            })
        else:
            return jsonify({"error": "Failed to record activity"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Failed to record activity: {str(e)}"}), 500

@app.route("/kill-switch", methods=["POST"])
def kill_switch():
    """Emergency kill switch to disable system"""
    try:
        data = request.get_json()
        if not data or not data.get("code"):
            return jsonify({"error": "Kill switch code required"}), 400
        
        user_code = data.get("code")
        
        # For demo purposes, accept any non-empty code
        # In production, you'd verify against a hashed code
        if len(user_code) >= 4:
            system_state['is_running'] = False
            log_activity("kill_switch_activated", notes="System disabled via kill switch")
            return jsonify({
                "status": "success",
                "message": "Kill switch activated - system disabled"
            })
        else:
            log_activity("kill_switch_failed", notes="Invalid kill switch attempt")
            return jsonify({"error": "Invalid kill switch code"}), 401
            
    except Exception as e:
        return jsonify({"error": f"Kill switch error: {str(e)}"}), 500

@app.route("/add-recipient", methods=["POST"])
def add_recipient():
    """Add new recipient to the system"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Set defaults
        data.setdefault('whatsapp', data['phone'])
        data.setdefault('preferred_language', 'english')
        
        recipients_path = os.path.join("config", "recipients.json")
        
        # Load existing recipients
        recipients = []
        if os.path.exists(recipients_path):
            with open(recipients_path, "r") as f:
                recipients = json.load(f)
        
        # Check for duplicates
        for recipient in recipients:
            if recipient.get('email') == data['email']:
                return jsonify({"error": "Recipient with this email already exists"}), 400
        
        # Add new recipient
        recipients.append(data)
        
        # Save updated recipients
        with open(recipients_path, "w") as f:
            json.dump(recipients, f, indent=4)
        
        log_activity("recipient_added", notes=f"Added recipient: {data['name']}")
        
        return jsonify({
            "status": "success",
            "message": f"Recipient {data['name']} added successfully",
            "recipient": data
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to add recipient: {str(e)}"}), 500

@app.route("/recipients", methods=["GET"])
def get_recipients():
    """Get all recipients"""
    try:
        recipients_path = os.path.join("config", "recipients.json")
        if os.path.exists(recipients_path):
            with open(recipients_path, "r") as f:
                recipients = json.load(f)
            return jsonify({"recipients": recipients})
        else:
            return jsonify({"recipients": []})
    except Exception as e:
        return jsonify({"error": f"Failed to get recipients: {str(e)}"}), 500

@app.route("/upload-document", methods=["POST"])
def upload_document():
    """Upload document to secure storage"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Security: Check file extension
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.png', '.zip'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({"error": f"File type {file_ext} not allowed"}), 400
        
        # Generate secure filename
        import time
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        save_path = os.path.join("secure_docs", filename)
        
        # Save file
        file.save(save_path)
        
        # Get additional info from form
        description = request.form.get('description', 'No description provided')
        
        # Save document info
        documents_path = os.path.join("config", "documents.json")
        documents = []
        if os.path.exists(documents_path):
            with open(documents_path, "r") as f:
                documents = json.load(f)
        
        document_info = {
            "name": file.filename,
            "file_path": save_path,
            "cloud_url": f"/documents/{filename}",
            "description": description,
            "uploaded_at": timestamp
        }
        documents.append(document_info)
        
        with open(documents_path, "w") as f:
            json.dump(documents, f, indent=4)
        
        log_activity("document_uploaded", notes=f"Uploaded: {file.filename}")
        
        return jsonify({
            "status": "success",
            "message": "Document uploaded successfully",
            "file": filename,
            "document": document_info
        })
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route("/documents/<filename>", methods=["GET"])
def serve_document(filename):
    """Serve uploaded documents (with basic security)"""
    try:
        # Security: Prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return jsonify({"error": "Invalid filename"}), 400
        
        return send_from_directory("secure_docs", filename)
    except FileNotFoundError:
        return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error serving document: {str(e)}"}), 500

@app.route("/documents", methods=["GET"])
def get_documents():
    """Get all uploaded documents"""
    try:
        documents_path = os.path.join("config", "documents.json")
        if os.path.exists(documents_path):
            with open(documents_path, "r") as f:
                documents = json.load(f)
            return jsonify({"documents": documents})
        else:
            return jsonify({"documents": []})
    except Exception as e:
        return jsonify({"error": f"Failed to get documents: {str(e)}"}), 500

@app.route("/start-trigger", methods=["POST"])
def start_trigger():
    """Start the death switch monitoring trigger"""
    try:
        system_state['is_running'] = True
        log_activity("monitoring_started", notes="Death switch monitoring activated")
        
        return jsonify({
            "status": "success",
            "message": "Death switch monitoring started"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to start trigger: {str(e)}"}), 500

@app.route("/test-system", methods=["POST"])
def test_system():
    """Test the system functionality"""
    try:
        # Test basic functionality
        test_results = {
            "database_accessible": True,
            "config_directory": os.path.exists("config"),
            "secure_docs_directory": os.path.exists("secure_docs"),
            "recipients_configured": os.path.exists(os.path.join("config", "recipients.json")),
            "documents_available": os.path.exists(os.path.join("config", "documents.json"))
        }
        
        # Test database
        try:
            log_activity("system_test", notes="System test performed")
            test_results["database_accessible"] = True
        except Exception:
            test_results["database_accessible"] = False
        
        return jsonify({
            "status": "success",
            "test_results": test_results,
            "message": "System test completed"
        })
        
    except Exception as e:
        return jsonify({"error": f"System test failed: {str(e)}"}), 500

@app.route("/activity-log", methods=["GET"])
def get_activity_log():
    """Get recent activity log"""
    try:
        conn = sqlite3.connect('death_switch.db')
        cursor = conn.cursor()
        
        # Get last 50 activities
        cursor.execute('''
            SELECT timestamp, activity_type, device_id, notes 
            FROM activity_log 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                "timestamp": row[0],
                "type": row[1],
                "device": row[2] or "Unknown",
                "notes": row[3] or ""
            })
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "activities": activities,
            "count": len(activities)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get activity log: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

# CORS preflight handling
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

if __name__ == '__main__':
    # For development only
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting Digital Death Switch AI...")
    print(f"📡 Server running on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"💾 System initialized: {system_state['initialized']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # For production (when run via gunicorn)
    app.config['DEBUG'] = False
