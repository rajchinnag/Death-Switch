# Email Configuration (Required)
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Twilio Configuration (Required for SMS/WhatsApp)
TWILIO_SID=your_twilio_account_sid
TWILIO_TOKEN=your_twilio_auth_token
TWILIO_PHONE=+1234567890

# System Configuration
INACTIVITY_DAYS=10
VERIFICATION_HOURS=48
SECRET_KEY=your_secret_key_here
FLASK_ENV=production

# Database (Railway will auto-provide DATABASE_URL)
DATABASE_URL=sqlite:///death_switch.db

# Optional: Kill Switch
KILL_SWITCH_HASH=your_hashed_kill_switch_code

# Optional: WhatsApp Business API
WHATSAPP_BUSINESS_TOKEN=your_whatsapp_business_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Optional: Google Drive Integration
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id