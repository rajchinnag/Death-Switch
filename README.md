# Death-Switch
# 💙 Digital Death Switch AI

An intelligent posthumous automation system that securely delivers your confidential documents to trusted recipients after inactivity and OTP failure — built with Flask, Twilio, Google Drive API, and WhatsApp integration.

## 🌟 Features

- **Smart Activity Monitoring**: Tracks device usage, app interactions, and user presence
- **Multi-Channel Notifications**: Email, SMS, and WhatsApp integration
- **Secure Document Delivery**: OTP-protected access to important documents
- **Multi-language Support**: Messages in 8 languages (English, Hindi, Telugu, Tamil, Kannada, Malayalam, Spanish, French)
- **Kill Switch**: Emergency disable functionality
- **Web Dashboard**: Complete control panel for configuration and monitoring
- **Cross-platform**: Windows, macOS, and Linux support

## 🚀 Quick Deploy on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### 1. Clone this repository
```bash
git clone https://github.com/yourusername/death-switch-ai.git
cd death-switch-ai
```

### 2. Set up environment variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

### 3. Deploy on Railway
- Connect your GitHub repository to Railway
- Add environment variables in Railway dashboard
- Add PostgreSQL database addon
- Deploy automatically!

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL` | Gmail address for notifications | `your_email@gmail.com` |
| `EMAIL_PASSWORD` | Gmail app password | `your_app_password` |
| `TWILIO_SID` | Twilio Account SID | `ACxxxxx...` |
| `TWILIO_TOKEN` | Twilio Auth Token | `your_token` |
| `TWILIO_PHONE` | Twilio phone number | `+1234567890` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `INACTIVITY_DAYS` | Days before trigger | `10` |
| `VERIFICATION_HOURS` | Hours to respond to OTP | `48` |
| `SECRET_KEY` | Flask secret key | Auto-generated |

## 📱 Usage

### Web Interface
Access the web dashboard at your deployed URL to:
- Configure recipients with preferred languages
- Upload important documents
- Monitor system status
- Test the system
- Set kill switch codes

### API Endpoints
- `GET /status` - System status
- `POST /record-activity` - Reset activity timer
- `POST /kill-switch` - Emergency disable
- `POST /add-recipient` - Add new recipient
- `POST /upload-document` - Upload document

## 🛡️ Security Features

- **OTP Verification**: Secure access to documents
- **Kill Switch**: Emergency system disable
- **Environment Variables**: No hardcoded credentials
- **Secure Hashing**: PBKDF2 for kill switch codes
- **Access Logging**: Complete activity audit trail

## 🌍 Supported Languages

Recipients can receive messages in their preferred language:
- 🇺🇸 English
- 🇮🇳 Hindi (हिंदी)
- 🇮🇳 Telugu (తెలుగు)
- 🇮🇳 Tamil (தமிழ்)
- 🇮🇳 Kannada (ಕನ್ನಡ)
- 🇮🇳 Malayalam (മലയാളം)
- 🇪🇸 Spanish (Español)
- 🇫🇷 French (Français)

## 🔧 Local Development

### Prerequisites
- Python 3.9+
- Gmail account with app password
- Twilio account (optional)

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/death-switch-ai.git
cd death-switch-ai

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Run the application
python app_backend.py
```

### Development Commands
```bash
# Start web interface
python app_backend.py

# Start background monitoring
python background_service.py start

# Test device monitoring
python device_monitor.py test

# Setup WhatsApp integration
python whatsapp_integration.py setup
```

## 📚 Documentation

### System Architecture
1. **Web Interface**: Flask-based control panel
2. **Background Service**: Continuous monitoring daemon
3. **Device Monitor**: Cross-platform activity detection
4. **Notification System**: Multi-channel message delivery
5. **Security Layer**: OTP and kill switch protection

### How It Works
1. **Monitor**: System tracks user activity across devices
2. **Trigger**: After configured inactivity period, sends OTP
3. **Verify**: User has limited time to respond with OTP
4. **Execute**: If no response, sends documents to recipients
5. **Secure**: Recipients get OTP-protected document access

## 🔍 Troubleshooting

### Common Issues

**Gmail Authentication Error**
- Enable 2FA on Gmail
- Generate app-specific password
- Use app password, not regular password

**Twilio SMS Failures**
- Verify phone numbers in Twilio console
- Check account balance
- Ensure phone numbers include country codes

**Railway Deployment Issues**
- Check build logs in Railway dashboard
- Verify all environment variables are set
- Ensure PostgreSQL addon is added

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This system is designed for legitimate posthumous document delivery. Users are responsible for:
- Complying with local laws and regulations
- Securing their credentials and access codes
- Testing the system thoroughly before relying on it
- Informing recipients about the system appropriately

---

**Made with 💙 for digital legacy protection**
