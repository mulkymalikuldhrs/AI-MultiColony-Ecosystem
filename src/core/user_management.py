"""
💰 Premium User Management System
Registration, KYC verification, payment processing, dan license management

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
KTP: ████████████████ (Developer Access - Free Forever)
"""

import hashlib
import secrets
import json
import sqlite3
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
import base64

@dataclass
class User:
    """User data structure"""
    user_id: str
    email: str
    full_name: str
    ktp_number: str
    phone_number: str
    country: str
    registration_date: str
    kyc_status: str  # pending, verified, rejected
    payment_status: str  # unpaid, paid, expired
    license_key: Optional[str]
    subscription_type: str  # free, premium, enterprise
    subscription_expires: Optional[str]
    is_developer: bool
    is_active: bool
    last_login: Optional[str]

@dataclass
class Payment:
    """Payment data structure"""
    payment_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: str
    payment_status: str  # pending, completed, failed, refunded
    payment_date: str
    transaction_id: Optional[str]
    description: str

@dataclass
class LicenseKey:
    """License key data structure"""
    license_key: str
    user_id: str
    subscription_type: str
    created_date: str
    expires_date: str
    is_active: bool
    usage_count: int
    max_usage: int

class UserManagementSystem:
    """
    💰 Premium User Management System
    
    Features:
    - User registration & authentication
    - KYC verification with ID validation
    - Payment processing integration
    - License key generation & management
    - Subscription management
    - Developer privileges (Mulky Malikul Dhaher = Free)
    """
    
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        self.developer_ktp = "1107151509970001"  # Mulky Malikul Dhaher
        self.developer_name = "Mulky Malikul Dhaher"
        
        # Pricing configuration
        self.pricing = {
            "premium_monthly": {"amount": 99000, "currency": "IDR", "duration_days": 30},
            "premium_yearly": {"amount": 999000, "currency": "IDR", "duration_days": 365},
            "enterprise_monthly": {"amount": 499000, "currency": "IDR", "duration_days": 30},
            "enterprise_yearly": {"amount": 4999000, "currency": "IDR", "duration_days": 365}
        }
        
        self._setup_database()
        self._initialize_developer_account()
        
        print("💰 User Management System initialized")
        print(f"   Developer: {self.developer_name} (Free Access)")
        print(f"   Pricing: Starting from IDR {self.pricing['premium_monthly']['amount']:,}/month")
    
    def _setup_database(self):
        """Initialize database tables"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    ktp_number TEXT UNIQUE NOT NULL,
                    phone_number TEXT NOT NULL,
                    country TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    kyc_status TEXT DEFAULT 'pending',
                    payment_status TEXT DEFAULT 'unpaid',
                    license_key TEXT,
                    subscription_type TEXT DEFAULT 'free',
                    subscription_expires TEXT,
                    is_developer BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Payments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    payment_method TEXT NOT NULL,
                    payment_status TEXT DEFAULT 'pending',
                    payment_date TEXT NOT NULL,
                    transaction_id TEXT,
                    description TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # License keys table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS license_keys (
                    license_key TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    subscription_type TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    expires_date TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    usage_count INTEGER DEFAULT 0,
                    max_usage INTEGER DEFAULT 1000,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # KYC documents table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kyc_documents (
                    doc_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    document_data TEXT NOT NULL,
                    verification_status TEXT DEFAULT 'pending',
                    verification_date TEXT,
                    verification_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_ktp ON users(ktp_number)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_license_keys_user ON license_keys(user_id)")
    
    def _initialize_developer_account(self):
        """Initialize developer account with free access"""
        try:
            # Check if developer account exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT user_id FROM users WHERE ktp_number = ?", 
                                    (self.developer_ktp,))
                if cursor.fetchone():
                    print("  ✅ Developer account already exists")
                    return
            
            # Create developer account
            developer_user = User(
                user_id=f"dev_{self.developer_ktp}",
                email="mulkymalikuldhr@mail.com",
                full_name=self.developer_name,
                ktp_number=self.developer_ktp,
                phone_number="+62-XXX-XXXX-XXXX",
                country="Indonesia",
                registration_date=datetime.now().isoformat(),
                kyc_status="verified",
                payment_status="paid",
                license_key=self._generate_license_key("enterprise"),
                subscription_type="enterprise",
                subscription_expires=(datetime.now() + timedelta(days=36500)).isoformat(),  # 100 years
                is_developer=True,
                is_active=True,
                last_login=None
            )
            
            # Hash password (default: "developer123")
            password_hash = self._hash_password("developer123")
            
            # Store developer account
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users 
                    (user_id, email, password_hash, full_name, ktp_number, phone_number, 
                     country, registration_date, kyc_status, payment_status, license_key,
                     subscription_type, subscription_expires, is_developer, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    developer_user.user_id, developer_user.email, password_hash,
                    developer_user.full_name, developer_user.ktp_number, 
                    developer_user.phone_number, developer_user.country,
                    developer_user.registration_date, developer_user.kyc_status,
                    developer_user.payment_status, developer_user.license_key,
                    developer_user.subscription_type, developer_user.subscription_expires,
                    developer_user.is_developer, developer_user.is_active
                ))
                
                # Create license key record
                license_record = LicenseKey(
                    license_key=developer_user.license_key,
                    user_id=developer_user.user_id,
                    subscription_type="enterprise",
                    created_date=datetime.now().isoformat(),
                    expires_date=developer_user.subscription_expires,
                    is_active=True,
                    usage_count=0,
                    max_usage=999999999  # Unlimited for developer
                )
                
                conn.execute("""
                    INSERT INTO license_keys 
                    (license_key, user_id, subscription_type, created_date, 
                     expires_date, is_active, usage_count, max_usage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    license_record.license_key, license_record.user_id,
                    license_record.subscription_type, license_record.created_date,
                    license_record.expires_date, license_record.is_active,
                    license_record.usage_count, license_record.max_usage
                ))
            
            print(f"  ✅ Developer account created: {self.developer_name}")
            print(f"  🔑 Developer license key: {developer_user.license_key}")
            
        except Exception as e:
            print(f"❌ Error initializing developer account: {e}")
    
    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new user"""
        try:
            # Validate required fields
            required_fields = ['email', 'password', 'full_name', 'ktp_number', 'phone_number', 'country']
            for field in required_fields:
                if field not in user_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Check if user already exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT user_id FROM users WHERE email = ? OR ktp_number = ?", 
                                    (user_data['email'], user_data['ktp_number']))
                if cursor.fetchone():
                    return {"success": False, "error": "User already exists with this email or KTP number"}
            
            # Check if this is the developer
            is_developer = user_data['ktp_number'] == self.developer_ktp
            
            # Create user object
            user_id = str(uuid.uuid4())
            user = User(
                user_id=user_id,
                email=user_data['email'],
                full_name=user_data['full_name'],
                ktp_number=user_data['ktp_number'],
                phone_number=user_data['phone_number'],
                country=user_data['country'],
                registration_date=datetime.now().isoformat(),
                kyc_status="verified" if is_developer else "pending",
                payment_status="paid" if is_developer else "unpaid",
                license_key=None,
                subscription_type="enterprise" if is_developer else "free",
                subscription_expires=None,
                is_developer=is_developer,
                is_active=True,
                last_login=None
            )
            
            # Hash password
            password_hash = self._hash_password(user_data['password'])
            
            # Store user in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users 
                    (user_id, email, password_hash, full_name, ktp_number, phone_number, 
                     country, registration_date, kyc_status, payment_status, license_key,
                     subscription_type, subscription_expires, is_developer, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.user_id, user.email, password_hash, user.full_name,
                    user.ktp_number, user.phone_number, user.country,
                    user.registration_date, user.kyc_status, user.payment_status,
                    user.license_key, user.subscription_type, user.subscription_expires,
                    user.is_developer, user.is_active
                ))
            
            response = {
                "success": True,
                "message": "User registered successfully",
                "user_id": user.user_id,
                "kyc_required": not is_developer,
                "payment_required": not is_developer
            }
            
            if is_developer:
                # Generate license key for developer immediately
                license_key = self._generate_license_key("enterprise")
                self._assign_license_key(user.user_id, license_key, "enterprise", 36500)  # 100 years
                response["license_key"] = license_key
                response["message"] = "Developer account registered with free enterprise access"
            
            return response
            
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_id, password_hash, full_name, is_developer, 
                           is_active, subscription_type, license_key
                    FROM users WHERE email = ?
                """, (email,))
                
                user_data = cursor.fetchone()
                
                if not user_data:
                    return {"success": False, "error": "User not found"}
                
                user_id, stored_hash, full_name, is_developer, is_active, subscription_type, license_key = user_data
                
                if not is_active:
                    return {"success": False, "error": "Account is deactivated"}
                
                # Verify password
                if not self._verify_password(password, stored_hash):
                    return {"success": False, "error": "Invalid password"}
                
                # Update last login
                conn.execute("UPDATE users SET last_login = ? WHERE user_id = ?", 
                           (datetime.now().isoformat(), user_id))
                
                return {
                    "success": True,
                    "message": "Authentication successful",
                    "user_id": user_id,
                    "full_name": full_name,
                    "is_developer": bool(is_developer),
                    "subscription_type": subscription_type,
                    "license_key": license_key,
                    "session_token": self._generate_session_token(user_id)
                }
                
        except Exception as e:
            return {"success": False, "error": f"Authentication failed: {str(e)}"}
    
    def submit_kyc(self, user_id: str, kyc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit KYC verification documents"""
        try:
            # Validate KYC data
            required_fields = ['ktp_image', 'selfie_image', 'address_proof']
            for field in required_fields:
                if field not in kyc_data:
                    return {"success": False, "error": f"Missing KYC document: {field}"}
            
            # Store KYC documents
            with sqlite3.connect(self.db_path) as conn:
                for doc_type, doc_data in kyc_data.items():
                    doc_id = str(uuid.uuid4())
                    
                    conn.execute("""
                        INSERT INTO kyc_documents 
                        (doc_id, user_id, document_type, document_data, verification_status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (doc_id, user_id, doc_type, doc_data, 'pending'))
            
            # Auto-verify for developer
            user = self.get_user(user_id)
            if user and user.get('is_developer'):
                self._verify_kyc(user_id, auto_verify=True)
                return {
                    "success": True,
                    "message": "KYC documents submitted and auto-verified (Developer account)",
                    "verification_status": "verified"
                }
            
            # For regular users, start verification process
            verification_result = self._process_kyc_verification(user_id, kyc_data)
            
            return {
                "success": True,
                "message": "KYC documents submitted successfully",
                "verification_status": verification_result['status'],
                "estimated_processing_time": "1-3 business days"
            }
            
        except Exception as e:
            return {"success": False, "error": f"KYC submission failed: {str(e)}"}
    
    def _process_kyc_verification(self, user_id: str, kyc_data: Dict) -> Dict[str, Any]:
        """Process KYC verification (AI-powered validation)"""
        try:
            # Simulate AI-powered KYC verification
            print(f"🤖 Processing KYC verification for user {user_id}")
            
            verification_score = 0
            issues = []
            
            # Simulate document validation
            if 'ktp_image' in kyc_data:
                # Basic validation (in real implementation, use OCR and AI)
                if len(kyc_data['ktp_image']) > 1000:  # Basic size check
                    verification_score += 30
                else:
                    issues.append("KTP image quality too low")
            
            if 'selfie_image' in kyc_data:
                if len(kyc_data['selfie_image']) > 1000:
                    verification_score += 30
                else:
                    issues.append("Selfie image quality too low")
            
            if 'address_proof' in kyc_data:
                if len(kyc_data['address_proof']) > 500:
                    verification_score += 40
                else:
                    issues.append("Address proof unclear")
            
            # Determine verification status
            if verification_score >= 80:
                status = "verified"
                self._verify_kyc(user_id)
            elif verification_score >= 60:
                status = "manual_review"
            else:
                status = "rejected"
            
            return {
                "status": status,
                "score": verification_score,
                "issues": issues
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _verify_kyc(self, user_id: str, auto_verify: bool = False):
        """Mark KYC as verified"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Update user KYC status
                conn.execute("""
                    UPDATE users SET kyc_status = ?, payment_status = ? 
                    WHERE user_id = ?
                """, ("verified", "payment_required", user_id))
                
                # Update KYC documents status
                conn.execute("""
                    UPDATE kyc_documents 
                    SET verification_status = ?, verification_date = ?, 
                        verification_notes = ?
                    WHERE user_id = ?
                """, ("verified", datetime.now().isoformat(), 
                     "Auto-verified (Developer)" if auto_verify else "AI verification passed", 
                     user_id))
                
                print(f"  ✅ KYC verified for user {user_id}")
                
        except Exception as e:
            print(f"❌ KYC verification error: {e}")
    
    def process_payment(self, user_id: str, subscription_type: str, payment_method: str) -> Dict[str, Any]:
        """Process payment for subscription"""
        try:
            # Check if user is developer (free access)
            user = self.get_user(user_id)
            if user and user.get('is_developer'):
                return {
                    "success": True,
                    "message": "Payment not required for developer account",
                    "license_key": user.get('license_key'),
                    "subscription_type": "enterprise"
                }
            
            # Get pricing
            if subscription_type not in self.pricing:
                return {"success": False, "error": "Invalid subscription type"}
            
            pricing = self.pricing[subscription_type]
            
            # Create payment record
            payment_id = str(uuid.uuid4())
            payment = Payment(
                payment_id=payment_id,
                user_id=user_id,
                amount=pricing['amount'],
                currency=pricing['currency'],
                payment_method=payment_method,
                payment_status='pending',
                payment_date=datetime.now().isoformat(),
                transaction_id=None,
                description=f"Subscription: {subscription_type}"
            )
            
            # Store payment record
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO payments 
                    (payment_id, user_id, amount, currency, payment_method, 
                     payment_status, payment_date, transaction_id, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    payment.payment_id, payment.user_id, payment.amount,
                    payment.currency, payment.payment_method, payment.payment_status,
                    payment.payment_date, payment.transaction_id, payment.description
                ))
            
            # Process payment (simulate payment gateway)
            payment_result = self._process_payment_gateway(payment)
            
            if payment_result['success']:
                # Payment successful - generate license key
                license_key = self._generate_license_key(subscription_type.split('_')[0])
                duration_days = pricing['duration_days']
                
                self._assign_license_key(user_id, license_key, subscription_type, duration_days)
                
                # Update payment status
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE payments 
                        SET payment_status = ?, transaction_id = ?
                        WHERE payment_id = ?
                    """, ('completed', payment_result['transaction_id'], payment_id))
                
                return {
                    "success": True,
                    "message": "Payment processed successfully",
                    "payment_id": payment_id,
                    "license_key": license_key,
                    "subscription_type": subscription_type,
                    "expires_date": (datetime.now() + timedelta(days=duration_days)).isoformat()
                }
            else:
                # Payment failed
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE payments SET payment_status = ? WHERE payment_id = ?
                    """, ('failed', payment_id))
                
                return {
                    "success": False,
                    "error": "Payment processing failed",
                    "payment_id": payment_id
                }
                
        except Exception as e:
            return {"success": False, "error": f"Payment processing failed: {str(e)}"}
    
    def _process_payment_gateway(self, payment: Payment) -> Dict[str, Any]:
        """Simulate payment gateway processing"""
        try:
            print(f"💳 Processing payment: {payment.amount} {payment.currency}")
            
            # Simulate payment processing delay
            time.sleep(2)
            
            # Simulate payment success (90% success rate)
            import random
            if random.random() < 0.9:
                transaction_id = f"TXN_{int(time.time())}_{random.randint(1000, 9999)}"
                print(f"  ✅ Payment successful: {transaction_id}")
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "gateway_response": "Payment completed successfully"
                }
            else:
                print(f"  ❌ Payment failed: Insufficient funds")
                return {
                    "success": False,
                    "error": "Payment declined by bank"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_license_key(self, subscription_type: str) -> str:
        """Generate unique license key"""
        # Create license key format: AGENTIC-{TYPE}-{RANDOM}-{CHECKSUM}
        type_code = {
            'free': 'FREE',
            'premium': 'PREM',
            'enterprise': 'ENTR'
        }.get(subscription_type, 'UNKN')
        
        # Generate random part
        random_part = secrets.token_hex(8).upper()
        
        # Generate checksum
        checksum_data = f"{type_code}{random_part}{int(time.time())}"
        checksum = hashlib.md5(checksum_data.encode()).hexdigest()[:4].upper()
        
        license_key = f"AGENTIC-{type_code}-{random_part}-{checksum}"
        
        return license_key
    
    def _assign_license_key(self, user_id: str, license_key: str, subscription_type: str, duration_days: int):
        """Assign license key to user"""
        try:
            expires_date = (datetime.now() + timedelta(days=duration_days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Update user record
                conn.execute("""
                    UPDATE users 
                    SET license_key = ?, subscription_type = ?, 
                        subscription_expires = ?, payment_status = ?
                    WHERE user_id = ?
                """, (license_key, subscription_type, expires_date, 'paid', user_id))
                
                # Create license key record
                max_usage = {
                    'free': 100,
                    'premium': 10000,
                    'enterprise': 999999999
                }.get(subscription_type.split('_')[0], 1000)
                
                conn.execute("""
                    INSERT INTO license_keys 
                    (license_key, user_id, subscription_type, created_date, 
                     expires_date, is_active, usage_count, max_usage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    license_key, user_id, subscription_type, 
                    datetime.now().isoformat(), expires_date,
                    True, 0, max_usage
                ))
                
                print(f"  ✅ License key assigned: {license_key}")
                
        except Exception as e:
            print(f"❌ License key assignment error: {e}")
    
    def validate_license_key(self, license_key: str) -> Dict[str, Any]:
        """Validate license key and check usage limits"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT lk.*, u.full_name, u.is_developer, u.is_active
                    FROM license_keys lk
                    JOIN users u ON lk.user_id = u.user_id
                    WHERE lk.license_key = ?
                """, (license_key,))
                
                result = cursor.fetchone()
                
                if not result:
                    return {"valid": False, "error": "Invalid license key"}
                
                (lk_key, user_id, subscription_type, created_date, expires_date, 
                 is_active, usage_count, max_usage, created_at, 
                 full_name, is_developer, user_active) = result
                
                # Check if user account is active
                if not user_active:
                    return {"valid": False, "error": "User account is deactivated"}
                
                # Check if license is active
                if not is_active:
                    return {"valid": False, "error": "License key is deactivated"}
                
                # Check if license has expired
                if datetime.fromisoformat(expires_date) < datetime.now():
                    return {"valid": False, "error": "License key has expired"}
                
                # Check usage limits (unless developer)
                if not is_developer and usage_count >= max_usage:
                    return {"valid": False, "error": "License usage limit exceeded"}
                
                # License is valid - increment usage count
                conn.execute("""
                    UPDATE license_keys 
                    SET usage_count = usage_count + 1 
                    WHERE license_key = ?
                """, (license_key,))
                
                return {
                    "valid": True,
                    "user_id": user_id,
                    "full_name": full_name,
                    "subscription_type": subscription_type,
                    "expires_date": expires_date,
                    "usage_count": usage_count + 1,
                    "max_usage": max_usage,
                    "is_developer": bool(is_developer),
                    "remaining_usage": max_usage - (usage_count + 1) if not is_developer else "unlimited"
                }
                
        except Exception as e:
            return {"valid": False, "error": f"License validation failed: {str(e)}"}
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_id, email, full_name, ktp_number, phone_number, country,
                           registration_date, kyc_status, payment_status, license_key,
                           subscription_type, subscription_expires, is_developer, 
                           is_active, last_login
                    FROM users WHERE user_id = ?
                """, (user_id,))
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        "user_id": result[0],
                        "email": result[1],
                        "full_name": result[2],
                        "ktp_number": result[3],
                        "phone_number": result[4],
                        "country": result[5],
                        "registration_date": result[6],
                        "kyc_status": result[7],
                        "payment_status": result[8],
                        "license_key": result[9],
                        "subscription_type": result[10],
                        "subscription_expires": result[11],
                        "is_developer": bool(result[12]),
                        "is_active": bool(result[13]),
                        "last_login": result[14]
                    }
                
                return None
                
        except Exception as e:
            print(f"❌ Get user error: {e}")
            return None
    
    def get_user_payments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user payment history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT payment_id, amount, currency, payment_method, 
                           payment_status, payment_date, transaction_id, description
                    FROM payments WHERE user_id = ?
                    ORDER BY payment_date DESC
                """, (user_id,))
                
                payments = []
                for row in cursor.fetchall():
                    payments.append({
                        "payment_id": row[0],
                        "amount": row[1],
                        "currency": row[2],
                        "payment_method": row[3],
                        "payment_status": row[4],
                        "payment_date": row[5],
                        "transaction_id": row[6],
                        "description": row[7]
                    })
                
                return payments
                
        except Exception as e:
            print(f"❌ Get payments error: {e}")
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # User statistics
                cursor = conn.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_developer = 1")
                developer_accounts = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE kyc_status = 'verified'")
                verified_users = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE payment_status = 'paid'")
                paid_users = cursor.fetchone()[0]
                
                # Payment statistics
                cursor = conn.execute("SELECT COUNT(*) FROM payments WHERE payment_status = 'completed'")
                successful_payments = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT SUM(amount) FROM payments WHERE payment_status = 'completed'")
                total_revenue = cursor.fetchone()[0] or 0
                
                # License statistics
                cursor = conn.execute("SELECT COUNT(*) FROM license_keys WHERE is_active = 1")
                active_licenses = cursor.fetchone()[0]
                
                return {
                    "users": {
                        "total": total_users,
                        "verified": verified_users,
                        "paid": paid_users,
                        "developers": developer_accounts
                    },
                    "payments": {
                        "successful": successful_payments,
                        "total_revenue": total_revenue,
                        "currency": "IDR"
                    },
                    "licenses": {
                        "active": active_licenses
                    },
                    "system": {
                        "status": "operational",
                        "last_updated": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            return {"error": f"Stats retrieval failed: {str(e)}"}
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except:
            return False
    
    def _generate_session_token(self, user_id: str) -> str:
        """Generate session token for authenticated user"""
        timestamp = int(time.time())
        token_data = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
        return base64.b64encode(token_data.encode()).decode()

# Global instance
user_management = UserManagementSystem()

# Quick access functions
def register_user(user_data: Dict) -> Dict:
    """Quick user registration"""
    return user_management.register_user(user_data)

def authenticate_user(email: str, password: str) -> Dict:
    """Quick user authentication"""
    return user_management.authenticate_user(email, password)

def validate_license(license_key: str) -> Dict:
    """Quick license validation"""
    return user_management.validate_license_key(license_key)

if __name__ == "__main__":
    # Display system info
    print("💰 Premium User Management System")
    print(f"   Developer: Mulky Malikul Dhaher (KTP: ████████████████)")
    print(f"   Status: Free access forever for developer")
    
    stats = user_management.get_system_stats()
    print(f"   Total users: {stats['users']['total']}")
    print(f"   Verified users: {stats['users']['verified']}")
    print(f"   Active licenses: {stats['licenses']['active']}")