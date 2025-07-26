#!/usr/bin/env python3
"""
WhatsApp Integration for Digital Death Switch AI
Supports multiple WhatsApp APIs and fallback methods
"""

import json
import requests
import time
import os
import logging
from typing import List, Dict, Optional
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppManager:
    """Handles WhatsApp message sending via multiple providers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_providers()
    
    def setup_providers(self):
        """Setup available WhatsApp providers"""
        self.providers = {}
        
        # Twilio WhatsApp Business API
        if all(key in self.config for key in ['twilio_sid', 'twilio_token', 'twilio_whatsapp_number']):
            self.providers['twilio'] = TwilioWhatsApp(self.config)
        
        # WhatsApp Business API (Official)
        if 'whatsapp_business_token' in self.config:
            self.providers['business_api'] = WhatsAppBusinessAPI(self.config)
        
        # WhatsApp Web API (Third-party)
        if 'whatsapp_web_api_url' in self.config:
            self.providers['web_api'] = WhatsAppWebAPI(self.config)
        
        # Baileys (JavaScript WhatsApp Web)
        if 'baileys_api_url' in self.config:
            self.providers['baileys'] = BaileysAPI(self.config)
        
        logger.info(f"Initialized {len(self.providers)} WhatsApp providers: {list(self.providers.keys())}")
    
    def send_message(self, phone_number: str, message: str, attachments: List[str] = None) -> bool:
        """Send WhatsApp message using available providers (with fallback)"""
        
        # Clean phone number
        phone_number = self.clean_phone_number(phone_number)
        
        # Try providers in order of reliability
        provider_order = ['business_api', 'twilio', 'web_api', 'baileys']
        
        for provider_name in provider_order:
            if provider_name in self.providers:
                try:
                    logger.info(f"Attempting WhatsApp send via {provider_name}")
                    provider = self.providers[provider_name]
                    
                    if attachments:
                        success = provider.send_message_with_attachments(phone_number, message, attachments)
                    else:
                        success = provider.send_message(phone_number, message)
                    
                    if success:
                        logger.info(f"✅ WhatsApp message sent successfully via {provider_name}")
                        return True
                    else:
                        logger.warning(f"❌ Failed to send via {provider_name}")
                        
                except Exception as e:
                    logger.error(f"❌ Error with {provider