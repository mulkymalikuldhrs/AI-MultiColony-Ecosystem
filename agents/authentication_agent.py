"""
🔐 Authentication Agent - KYC, Payment Verification, and User Management
Advanced AI agent for user authentication, KYC verification, and payment processing

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import logging
import hashlib
import secrets
import time
import re
import sqlite3
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import requests
import subprocess
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
import pyotp
from PIL import Image
import cv2
import numpy as np

@dataclass
class User:
    """User account information"""
    user_id: str
    username: str
    email: str
    phone: Optional[str]
    kyc_status: str  # pending, verified, rejected, expired
    account_status: str  # active, suspended, banned, pending_payment
    created_at: datetime
    last_login: Optional[datetime] = None
    payment_status: str = "unpaid"  # unpaid, paid, expired
    subscription_type: str = "free"  # free, basic, premium, enterprise
    verification_level: int = 0  # 0=none, 1=email, 2=phone, 3=kyc, 4=full
    metadata: Dict[str, Any] = None

@dataclass
class KYCDocument:
    """KYC document information"""
    document_id: str
    user_id: str
    document_type: str  # ktp, passport, driver_license, bank_statement
    document_number: str
    full_name: str
    date_of_birth: Optional[str]
    address: Optional[str]
    uploaded_at: datetime
    verification_status: str  # pending, verified, rejected
    verification_notes: Optional[str] = None
    confidence_score: float = 0.0

@dataclass
class PaymentRecord:
    """Payment transaction record"""
    payment_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: str
    payment_provider: str
    status: str  # pending, completed, failed, refunded
    created_at: datetime
    completed_at: Optional[datetime] = None
    verification_code: Optional[str] = None
    metadata: Dict[str, Any] = None

class AuthenticationAgent:
    """
    Authentication Agent: Comprehensive user authentication and verification
    
    Capabilities:
    - 🔐 Multi-factor authentication
    - 📋 KYC (Know Your Customer) verification
    - 💳 Payment verification and processing
    - 👤 User account management
    - 🔍 Identity verification
    - 📱 2FA/TOTP implementation
    - 🌐 SSO (Single Sign-On) integration
    - 🔒 Session management
    - 📊 Authentication analytics
    - 🚫 Fraud detection and prevention
    """
    
    def __init__(self):
        self.agent_id = "authentication_agent"
        self.name = "Authentication Agent"
        self.status = "initializing"
        self.version = "1.0.0"
        self.start_time = datetime.now()
        
        # Core capabilities
        self.capabilities = [
            "multi_factor_authentication",
            "kyc_verification",
            "payment_verification",
            "user_management",
            "identity_verification",
            "two_factor_auth",
            "session_management",
            "fraud_detection",
            "compliance_management",
            "authentication_analytics"
        ]
        
        # User management
        self.users = {}
        self.active_sessions = {}
        self.kyc_documents = {}
        self.payment_records = {}
        
        # Authentication configuration
        self.auth_config = {
            "session_timeout": 3600,  # 1 hour
            "password_min_length": 8,
            "max_login_attempts": 5,
            "lockout_duration": 900,  # 15 minutes
            "require_2fa": True,
            "kyc_required_for_paid": True,
            "auto_verify_owner": True
        }
        
        # KYC configuration
        self.kyc_config = {
            "required_documents": ["ktp"],  # Indonesian ID required
            "manual_review_threshold": 0.7,
            "auto_approve_threshold": 0.9,
            "document_expiry_days": 365,
            "owner_ktp": "1107151509970001",  # Mulky Malikul Dhaher
            "owner_name": "Mulky Malikul Dhaher"
        }
        
        # Payment configuration
        self.payment_config = {
            "supported_currencies": ["USD", "IDR"],
            "supported_methods": ["bank_transfer", "crypto", "e_wallet"],
            "payment_providers": {
                "midtrans": {"api_key": None, "active": False},
                "xendit": {"api_key": None, "active": False},
                "gopay": {"api_key": None, "active": False},
                "dana": {"api_key": None, "active": False}
            },
            "subscription_prices": {
                "basic": {"usd": 9.99, "idr": 150000},
                "premium": {"usd": 29.99, "idr": 450000},
                "enterprise": {"usd": 99.99, "idr": 1500000}
            }
        }
        
        # Security keys
        self.jwt_secret = None
        self.encryption_key = None
        self.totp_issuer = "Dhaher AI Ecosystem"
        
        # Fraud detection
        self.fraud_patterns = {
            "suspicious_ips": set(),
            "failed_attempts": {},
            "rate_limits": {}
        }
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize authentication infrastructure
        self.initialize_auth_infrastructure()
        
        # Load configuration
        self.load_auth_configuration()
        
        # Initialize owner account
        self.initialize_owner_account()
        
        self.logger.info("Authentication Agent initialized successfully")
        self.status = "ready"
    
    def setup_logging(self):
        """Setup logging for Authentication Agent"""
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "authentication.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AuthenticationAgent")
    
    def initialize_auth_infrastructure(self):
        """Initialize authentication infrastructure"""
        # Create authentication directories
        auth_dirs = [
            "data/auth",
            "data/auth/users",
            "data/auth/kyc",
            "data/auth/payments",
            "data/auth/sessions",
            "data/auth/logs"
        ]
        
        for directory in auth_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.initialize_auth_database()
        
        # Initialize encryption
        self.initialize_auth_encryption()
    
    def initialize_auth_database(self):
        """Initialize SQLite database for authentication"""
        db_dir = Path("data/auth")
        self.db_path = db_dir / "authentication.db"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    kyc_status TEXT DEFAULT 'pending',
                    account_status TEXT DEFAULT 'pending_payment',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    payment_status TEXT DEFAULT 'unpaid',
                    subscription_type TEXT DEFAULT 'free',
                    verification_level INTEGER DEFAULT 0,
                    totp_secret TEXT,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kyc_documents (
                    document_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    document_type TEXT NOT NULL,
                    document_number TEXT,
                    full_name TEXT,
                    date_of_birth TEXT,
                    address TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verification_status TEXT DEFAULT 'pending',
                    verification_notes TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    document_data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_records (
                    payment_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    payment_method TEXT,
                    payment_provider TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    verification_code TEXT,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_logs (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    details TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Authentication database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize authentication database: {e}")
    
    def initialize_auth_encryption(self):
        """Initialize encryption for authentication"""
        try:
            # Generate or load JWT secret
            jwt_file = Path("data/auth/.jwt.key")
            if jwt_file.exists():
                with open(jwt_file, 'r') as f:
                    self.jwt_secret = f.read().strip()
            else:
                self.jwt_secret = secrets.token_urlsafe(64)
                with open(jwt_file, 'w') as f:
                    f.write(self.jwt_secret)
                os.chmod(jwt_file, 0o600)
            
            # Generate or load encryption key
            encryption_file = Path("data/auth/.encryption.key")
            if encryption_file.exists():
                with open(encryption_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                self.encryption_key = Fernet.generate_key()
                with open(encryption_file, 'wb') as f:
                    f.write(self.encryption_key)
                os.chmod(encryption_file, 0o600)
            
            self.logger.info("Authentication encryption initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
    
    def load_auth_configuration(self):
        """Load authentication configuration"""
        config_file = Path("data/auth/auth_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.auth_config.update(config.get("auth_config", {}))
                    self.kyc_config.update(config.get("kyc_config", {}))
                    self.payment_config.update(config.get("payment_config", {}))
                    
                self.logger.info("Authentication configuration loaded")
                
            except Exception as e:
                self.logger.error(f"Failed to load auth configuration: {e}")
    
    def initialize_owner_account(self):
        """Initialize owner account (Mulky Malikul Dhaher) with full privileges"""
        try:
            owner_user_id = "owner_mulky_malikul_dhaher"
            
            # Check if owner account already exists
            if owner_user_id not in self.users:
                # Create owner account
                owner_user = User(
                    user_id=owner_user_id,
                    username="mulkymalikuldhaher",
                    email="mulky@dhaher.ai",
                    phone="+62", # Indonesian phone prefix
                    kyc_status="verified",
                    account_status="active",
                    created_at=datetime.now(),
                    payment_status="paid",
                    subscription_type="enterprise",
                    verification_level=4,  # Full verification
                    metadata={
                        "ktp": self.kyc_config["owner_ktp"],
                        "full_name": self.kyc_config["owner_name"],
                        "role": "owner",
                        "privileges": "all"
                    }
                )
                
                self.users[owner_user_id] = owner_user
                
                # Auto-verify owner KYC
                if self.kyc_config["auto_verify_owner"]:
                    # Schedule async verification for later when event loop is available
                    self.logger.info("Owner KYC auto-verification scheduled")
                
                self.logger.info("Owner account initialized with full privileges")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize owner account: {e}")
    
    async def register_user(self, username: str, email: str, password: str, 
                          phone: Optional[str] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a new user"""
        self.logger.info(f"Registering new user: {username}")
        
        try:
            # Validate input
            validation_result = self._validate_registration_data(username, email, password)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Check if user already exists
            if self._user_exists(username, email):
                return {"success": False, "error": "User already exists"}
            
            # Generate user ID
            user_id = hashlib.md5(f"{username}_{email}_{datetime.now()}".encode()).hexdigest()[:12]
            
            # Hash password
            salt = secrets.token_bytes(32)
            password_hash = self._hash_password(password, salt)
            
            # Create user account
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                phone=phone,
                kyc_status="pending",
                account_status="pending_payment",
                created_at=datetime.now(),
                payment_status="unpaid",
                subscription_type="free",
                verification_level=1,  # Email verified
                metadata=metadata or {}
            )
            
            self.users[user_id] = user
            
            # Save to database
            await self._save_user_to_database(user, password_hash, salt)
            
            # Generate payment verification code
            payment_code = await self._generate_payment_verification_code(user_id)
            
            # Log registration
            await self._log_auth_action(user_id, "user_registration", True, {"username": username})
            
            self.logger.info(f"User registered successfully: {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "payment_verification_code": payment_code,
                "message": "User registered. Payment required to activate account.",
                "next_steps": [
                    "Complete payment using the verification code",
                    "Upload KYC documents for verification",
                    "Set up 2FA for enhanced security"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"User registration failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def authenticate_user(self, identifier: str, password: str, 
                              totp_code: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate user with username/email and password"""
        self.logger.info(f"Authenticating user: {identifier}")
        
        try:
            # Find user
            user = self._find_user_by_identifier(identifier)
            if not user:
                await self._log_auth_action(None, "login_attempt", False, {"identifier": identifier, "error": "user_not_found"})
                return {"success": False, "error": "Invalid credentials"}
            
            # Check account status
            if user.account_status == "suspended":
                return {"success": False, "error": "Account suspended"}
            elif user.account_status == "banned":
                return {"success": False, "error": "Account banned"}
            elif user.account_status == "pending_payment" and user.user_id != "owner_mulky_malikul_dhaher":
                return {"success": False, "error": "Payment required to access account"}
            
            # Verify password
            stored_hash, salt = await self._get_user_password_data(user.user_id)
            if not self._verify_password(password, stored_hash, salt):
                await self._log_auth_action(user.user_id, "login_attempt", False, {"error": "invalid_password"})
                return {"success": False, "error": "Invalid credentials"}
            
            # Check 2FA if required
            if self.auth_config["require_2fa"] and user.verification_level >= 2:
                totp_secret = await self._get_user_totp_secret(user.user_id)
                if totp_secret and not self._verify_totp(totp_secret, totp_code):
                    await self._log_auth_action(user.user_id, "login_attempt", False, {"error": "invalid_2fa"})
                    return {"success": False, "error": "Invalid 2FA code"}
            
            # Create session
            session_token = await self._create_user_session(user.user_id)
            
            # Update last login
            user.last_login = datetime.now()
            await self._update_user_in_database(user)
            
            # Log successful login
            await self._log_auth_action(user.user_id, "login_success", True)
            
            self.logger.info(f"User authenticated successfully: {user.user_id}")
            
            return {
                "success": True,
                "user_id": user.user_id,
                "session_token": session_token,
                "user_info": {
                    "username": user.username,
                    "email": user.email,
                    "subscription_type": user.subscription_type,
                    "verification_level": user.verification_level,
                    "kyc_status": user.kyc_status
                },
                "permissions": self._get_user_permissions(user)
            }
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    async def verify_payment(self, user_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify payment and activate user account"""
        self.logger.info(f"Verifying payment for user: {user_id}")
        
        try:
            if user_id not in self.users:
                return {"success": False, "error": "User not found"}
            
            user = self.users[user_id]
            
            # Generate payment record
            payment_id = hashlib.md5(f"{user_id}_payment_{datetime.now()}".encode()).hexdigest()[:12]
            
            payment_record = PaymentRecord(
                payment_id=payment_id,
                user_id=user_id,
                amount=payment_data.get("amount", 0.0),
                currency=payment_data.get("currency", "USD"),
                payment_method=payment_data.get("method", "bank_transfer"),
                payment_provider=payment_data.get("provider", "manual"),
                status="pending",
                created_at=datetime.now(),
                verification_code=payment_data.get("verification_code"),
                metadata=payment_data
            )
            
            # Simulate payment verification (in real implementation, this would integrate with payment gateways)
            verification_result = await self._verify_payment_with_provider(payment_record)
            
            if verification_result["success"]:
                # Update payment status
                payment_record.status = "completed"
                payment_record.completed_at = datetime.now()
                
                # Update user account
                user.payment_status = "paid"
                user.account_status = "active"
                user.subscription_type = payment_data.get("subscription_type", "basic")
                
                # Save updates
                await self._save_payment_record(payment_record)
                await self._update_user_in_database(user)
                
                # Log payment verification
                await self._log_auth_action(user_id, "payment_verified", True, {"payment_id": payment_id})
                
                self.logger.info(f"Payment verified successfully for user: {user_id}")
                
                return {
                    "success": True,
                    "payment_id": payment_id,
                    "account_activated": True,
                    "subscription_type": user.subscription_type,
                    "message": "Payment verified. Account activated successfully."
                }
            else:
                payment_record.status = "failed"
                await self._save_payment_record(payment_record)
                
                return {"success": False, "error": "Payment verification failed"}
            
        except Exception as e:
            self.logger.error(f"Payment verification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def upload_kyc_document(self, user_id: str, document_type: str, 
                                document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload and verify KYC document"""
        self.logger.info(f"Processing KYC document for user: {user_id}")
        
        try:
            if user_id not in self.users:
                return {"success": False, "error": "User not found"}
            
            # Generate document ID
            document_id = hashlib.md5(f"{user_id}_{document_type}_{datetime.now()}".encode()).hexdigest()[:12]
            
            # Extract document information
            document_number = document_data.get("document_number", "")
            full_name = document_data.get("full_name", "")
            
            # Special handling for owner KYC
            if (user_id == "owner_mulky_malikul_dhaher" or 
                document_number == self.kyc_config["owner_ktp"]):
                verification_status = "verified"
                confidence_score = 1.0
                verification_notes = "Owner account - auto-verified"
            else:
                # Perform KYC verification
                verification_result = await self._verify_kyc_document(document_type, document_data)
                verification_status = verification_result["status"]
                confidence_score = verification_result["confidence_score"]
                verification_notes = verification_result.get("notes")
            
            # Create KYC document record
            kyc_document = KYCDocument(
                document_id=document_id,
                user_id=user_id,
                document_type=document_type,
                document_number=document_number,
                full_name=full_name,
                date_of_birth=document_data.get("date_of_birth"),
                address=document_data.get("address"),
                uploaded_at=datetime.now(),
                verification_status=verification_status,
                verification_notes=verification_notes,
                confidence_score=confidence_score
            )
            
            self.kyc_documents[document_id] = kyc_document
            
            # Update user KYC status
            user = self.users[user_id]
            if verification_status == "verified":
                user.kyc_status = "verified"
                user.verification_level = max(user.verification_level, 3)
            
            # Save to database
            await self._save_kyc_document(kyc_document)
            await self._update_user_in_database(user)
            
            # Log KYC upload
            await self._log_auth_action(user_id, "kyc_upload", True, {
                "document_type": document_type,
                "verification_status": verification_status
            })
            
            self.logger.info(f"KYC document processed: {document_id} - {verification_status}")
            
            return {
                "success": True,
                "document_id": document_id,
                "verification_status": verification_status,
                "confidence_score": confidence_score,
                "message": f"KYC document {verification_status}"
            }
            
        except Exception as e:
            self.logger.error(f"KYC document processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_2fa(self, user_id: str) -> Dict[str, Any]:
        """Setup two-factor authentication for user"""
        self.logger.info(f"Setting up 2FA for user: {user_id}")
        
        try:
            if user_id not in self.users:
                return {"success": False, "error": "User not found"}
            
            user = self.users[user_id]
            
            # Generate TOTP secret
            totp_secret = pyotp.random_base32()
            
            # Create TOTP URI for QR code
            totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                name=user.email,
                issuer_name=self.totp_issuer
            )
            
            # Generate QR code
            qr_code_data = await self._generate_qr_code(totp_uri)
            
            # Save TOTP secret (encrypted)
            await self._save_user_totp_secret(user_id, totp_secret)
            
            # Update user verification level
            user.verification_level = max(user.verification_level, 2)
            await self._update_user_in_database(user)
            
            self.logger.info(f"2FA setup completed for user: {user_id}")
            
            return {
                "success": True,
                "totp_secret": totp_secret,
                "qr_code": qr_code_data,
                "backup_codes": self._generate_backup_codes(),
                "message": "2FA setup completed. Scan QR code with authenticator app."
            }
            
        except Exception as e:
            self.logger.error(f"2FA setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """Get comprehensive authentication status"""
        total_users = len(self.users)
        verified_users = len([u for u in self.users.values() if u.kyc_status == "verified"])
        paid_users = len([u for u in self.users.values() if u.payment_status == "paid"])
        active_sessions = len(self.active_sessions)
        
        return {
            "agent_status": self.status,
            "total_users": total_users,
            "verified_users": verified_users,
            "paid_users": paid_users,
            "active_sessions": active_sessions,
            "kyc_documents": len(self.kyc_documents),
            "payment_records": len(self.payment_records),
            "owner_account": {
                "user_id": "owner_mulky_malikul_dhaher",
                "name": self.kyc_config["owner_name"],
                "ktp": self.kyc_config["owner_ktp"],
                "status": "verified"
            },
            "security_features": {
                "2fa_enabled": self.auth_config["require_2fa"],
                "kyc_required": self.kyc_config["kyc_required_for_paid"],
                "session_timeout": self.auth_config["session_timeout"]
            },
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600
        }
    
    # Private helper methods
    
    async def _auto_verify_owner_kyc(self, user_id: str):
        """Auto-verify owner KYC documents"""
        try:
            # Create automatic KYC verification for owner
            document_id = hashlib.md5(f"{user_id}_auto_kyc_{datetime.now()}".encode()).hexdigest()[:12]
            
            kyc_document = KYCDocument(
                document_id=document_id,
                user_id=user_id,
                document_type="ktp",
                document_number=self.kyc_config["owner_ktp"],
                full_name=self.kyc_config["owner_name"],
                uploaded_at=datetime.now(),
                verification_status="verified",
                verification_notes="Owner account - auto-verified",
                confidence_score=1.0
            )
            
            self.kyc_documents[document_id] = kyc_document
            await self._save_kyc_document(kyc_document)
            
            self.logger.info("Owner KYC auto-verified")
            
        except Exception as e:
            self.logger.error(f"Owner KYC auto-verification failed: {e}")
    
    def _validate_registration_data(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Validate user registration data"""
        # Username validation
        if len(username) < 3 or len(username) > 30:
            return {"valid": False, "error": "Username must be 3-30 characters"}
        
        if not re.match("^[a-zA-Z0-9_]+$", username):
            return {"valid": False, "error": "Username can only contain letters, numbers, and underscore"}
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {"valid": False, "error": "Invalid email format"}
        
        # Password validation
        if len(password) < self.auth_config["password_min_length"]:
            return {"valid": False, "error": f"Password must be at least {self.auth_config['password_min_length']} characters"}
        
        return {"valid": True}
    
    def _user_exists(self, username: str, email: str) -> bool:
        """Check if user already exists"""
        for user in self.users.values():
            if user.username == username or user.email == email:
                return True
        return False
    
    def _hash_password(self, password: str, salt: bytes) -> bytes:
        """Hash password with salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    def _verify_password(self, password: str, stored_hash: bytes, salt: bytes) -> bool:
        """Verify password against stored hash"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        try:
            kdf.verify(password.encode(), stored_hash)
            return True
        except:
            return False
    
    async def _generate_payment_verification_code(self, user_id: str) -> str:
        """Generate unique payment verification code"""
        code = f"PAY_{user_id[:8].upper()}_{secrets.token_hex(4).upper()}"
        return code
    
    def _get_user_permissions(self, user: User) -> List[str]:
        """Get user permissions based on role and subscription"""
        permissions = ["basic_access"]
        
        if user.user_id == "owner_mulky_malikul_dhaher":
            return ["all_permissions"]
        
        if user.payment_status == "paid":
            permissions.append("paid_features")
        
        if user.kyc_status == "verified":
            permissions.append("verified_features")
        
        if user.subscription_type == "premium":
            permissions.extend(["premium_features", "advanced_agents"])
        elif user.subscription_type == "enterprise":
            permissions.extend(["enterprise_features", "all_agents", "custom_deployment"])
        
        return permissions

# Global instance
authentication_agent = AuthenticationAgent()

# Export for use by other modules
__all__ = ['AuthenticationAgent', 'authentication_agent', 'User', 'KYCDocument', 'PaymentRecord']
