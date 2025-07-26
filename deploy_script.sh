#!/bin/bash

# Quick Deploy Script for Death Switch AI on Railway
# Run this script after setting up your repository

echo "🚂 Death Switch AI - Railway Deployment Script"
echo "================================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Initializing..."
    git init
    git branch -M main
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your credentials before deploying!"
    echo "   Required: EMAIL, EMAIL_PASSWORD, TWILIO_SID, TWILIO_TOKEN"
fi

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "⚠️  config.json not found. Copying from example..."
    cp config.json.example config.json
    echo "📝 Please edit config.json with your settings if needed"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p secure_docs config static
touch secure_docs/.gitkeep config/.gitkeep static/.gitkeep

# Add all files to git
echo "📦 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy Death Switch AI to Railway" || echo "No changes to commit"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "🚂 Railway CLI not found. You can:"
    echo "   1. Install with: npm install -g @railway/cli"
    echo "   2. Or deploy via GitHub connection at railway.app"
else
    echo "🚂 Railway CLI found. You can now run:"
    echo "   railway login"
    echo "   railway init"
    echo "   railway up"
fi

echo ""
echo "✅ Repository prepared for Railway deployment!"
echo ""
echo "🔧 Next Steps:"
echo "   1. Edit .env file with your credentials"
echo "   2. Push to GitHub: git push origin main"
echo "   3. Connect repository to Railway at railway.app"
echo "   4. Add environment variables in Railway dashboard"
echo "   5. Add PostgreSQL database addon"
echo "   6. Deploy!"
echo ""
echo "📚 Environment variables needed in Railway:"
echo "   EMAIL, EMAIL_PASSWORD, TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE"
echo "   INACTIVITY_DAYS, VERIFICATION_HOURS, SECRET_KEY"
echo ""
echo "🌍 Your app will be available at: https://your-app-name.railway.app"