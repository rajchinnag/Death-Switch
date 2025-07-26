from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import threading
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
CORS(app)

# Initialize Death Switch AI with error handling
dsa = None
try:
    from death_switch_system import DeathSwitchAI
    
    # Try to load config, create default if missing
    config_file = "config.json"
    if not os.path.exists(config_file):
        print("Creating default config file from environment variables...")
        default_config = {
            "email": os.getenv("EMAIL", "your_email@gmail.com"),
            "email_password": os.getenv("EMAIL_PASSWORD", "your_app_password"),
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", 587)),
            "twilio_sid": os.getenv("TWILIO_SID", ""),
            "twilio_token": os.getenv("TWILIO_TOKEN", ""),
            "twilio_phone": os.getenv("TWILIO_PHONE", ""),
            "inactivity_days": int(os.getenv("INACTIVITY_DAYS", 10)),
            "verification_hours": int(os.getenv("VERIFICATION_HOURS", 48)),
            "kill_switch_hash": os.getenv("KILL_SWITCH_HASH", ""),
            "recipients": [],
            "documents": []
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print("✅ Default config created successfully")
    
    dsa = DeathSwitchAI(config_file)
    app.config['DSA_INITIALIZED'] = True
    print("✅ DeathSwitchAI initialized successfully")
    
except Exception as e:
    print(f"⚠️ Warning: Could not initialize DeathSwitchAI: {e}")
    print("The web interface will still work but with limited functionality")
    app.config['DSA_INITIALIZED'] = False

# Create necessary directories
os.makedirs("secure_docs", exist_ok=True)
os.makedirs("config", exist_ok=True)

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
        "dsa_initialized": app.config.get('DSA_INITIALIZED', False),
        "environment": os.getenv("FLASK_ENV", "production"),
        "platform": "railway" if os.getenv("RAILWAY_ENVIRONMENT") else "unknown"
    })

@app.route("/status", methods=["GET"])
def get_status():
    """Get system status"""
    if not dsa:
        return jsonify({
            "error": "System not initialized",
            "message": "DeathSwitchAI could not be initialized. Check configuration."
        }), 500
    
    try:
        last_activity = dsa.db.get_last_activity()
        return jsonify({
            "system": "active",
            "last_activity": str(last_activity) if last_activity else "Never",
            "days_remaining": dsa.inactivity_days,
            "initialized": True,
            "recipients_count": len(dsa.recipients),
            "documents_count": len(dsa.documents)
        })
    except Exception as e:
        return jsonify({"error": f"Status check failed: {str(e)}"}), 500

@app.route("/record-activity", methods=["POST"])
def record_activity():
    """Record user activity to reset death timer"""
    if not dsa:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        user_agent = request.headers.get('User-Agent', 'Unknown')
        dsa.db.log_activity(
            "manual_check_in", 
            device_id=request.remote_addr,
            notes=f"Web UI check-in from {user_agent}"
        )
        return jsonify({
            "status": "success",
            "message": "Activity recorded successfully - death timer reset!"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to record activity: {str(e)}"}), 500

@app.route("/kill-switch", methods=["POST"])
def kill_switch():
    """Emergency kill switch to disable system"""
    if not dsa:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        data = request.get_json()
        if not data or not data.get("code"):
            return jsonify({"error": "Kill switch code required"}), 400
        
        user_code = data.get("code")
        
        # Check if kill switch is configured
        kill_switch_hash = dsa.config.get('kill_switch_hash', '')
        if not kill_switch_hash:
            return jsonify({
                "error": "Kill switch not configured",
                "message": "No kill switch code has been set for this system"
            }), 400
        
        if dsa.security.verify_kill_switch(user_code, kill_switch_hash):
            dsa.trigger_activated = False
            dsa.is_running = False
            dsa.db.log_activity("kill_switch_activated", notes="System disabled via kill switch")
            return jsonify({
                "status": "success",
                "message": "Kill switch activated - system disabled"
            })
        else:
            dsa.db.log_activity("kill_switch_failed", notes="Invalid kill switch attempt")
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
        
        # Update DSA instance if available
        if dsa:
            dsa.load_config(dsa.config_file if hasattr(dsa, 'config_file') else 'config.json')
        
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
    if not dsa:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        if hasattr(dsa, 'trigger_activated') and dsa.trigger_activated:
            return jsonify({
                "status": "already_running",
                "message": "Death switch trigger is already active"
            })
        
        def run_trigger():
            try:
                dsa.run_monitoring_cycle()
            except Exception as e:
                print(f"Error in trigger thread: {e}")
        
        thread = threading.Thread(target=run_trigger)
        thread.daemon = True  # Dies when main process dies
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "Death switch monitoring started"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to start trigger: {str(e)}"}), 500

@app.route("/test-system", methods=["POST"])
def test_system():
    """Test the system functionality"""
    if not dsa:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        # Test email configuration
        test_results = {
            "email_config": bool(dsa.config.get('email')),
            "twilio_config": bool(dsa.config.get('twilio_sid')),
            "recipients_configured": len(dsa.recipients) > 0,
            "documents_available": len(dsa.documents) > 0,
            "database_accessible": True
        }
        
        # Test database
        try:
            dsa.db.log_activity("system_test", notes="System test performed")
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
    if not dsa:
        return json