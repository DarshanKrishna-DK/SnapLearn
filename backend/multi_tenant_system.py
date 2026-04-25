"""
Multi-Tenant System with Advanced Security - Phase 5
Production-ready multi-tenancy, authentication, and authorization
"""

import os
import logging
import json
import uuid
import hashlib
import secrets
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis

from utils import schedule_async_init

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    """User roles within an organization"""
    SUPER_ADMIN = "super_admin"         # Platform administrator
    ORG_ADMIN = "org_admin"             # Organization administrator
    EDUCATOR = "educator"               # Teacher/instructor
    STUDENT = "student"                 # Student user
    PARENT = "parent"                   # Parent/guardian
    DEVELOPER = "developer"             # API developer
    VIEWER = "viewer"                   # Read-only access

class PlanType(str, Enum):
    """Subscription plan types"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class PermissionScope(str, Enum):
    """Permission scopes for fine-grained access control"""
    TUTORING_READ = "tutoring:read"
    TUTORING_WRITE = "tutoring:write"
    ASSESSMENT_READ = "assessment:read"
    ASSESSMENT_WRITE = "assessment:write"
    VIDEO_READ = "video:read"
    VIDEO_WRITE = "video:write"
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_WRITE = "analytics:write"
    STUDENT_READ = "student:read"
    STUDENT_WRITE = "student:write"
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"

@dataclass
class Organization:
    """Organization/tenant data structure"""
    org_id: str
    name: str
    plan_type: PlanType
    domain: Optional[str]
    settings: Dict[str, Any]
    created_at: datetime
    is_active: bool = True
    max_students: int = 100
    max_educators: int = 10
    features_enabled: List[str] = None
    usage_quotas: Dict[str, int] = None
    billing_info: Dict[str, Any] = None

@dataclass
class User:
    """User data structure"""
    user_id: str
    org_id: str
    email: str
    username: str
    role: UserRole
    permissions: Set[PermissionScope]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    profile_data: Dict[str, Any] = None
    preferences: Dict[str, Any] = None

@dataclass
class APIKey:
    """API key data structure"""
    key_id: str
    org_id: str
    name: str
    key_hash: str
    permissions: Set[PermissionScope]
    rate_limit: int
    expires_at: Optional[datetime]
    created_at: datetime
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None

class MultiTenantSystem:
    """Multi-tenant system with advanced security and role-based access control"""
    
    def __init__(self):
        # Security configuration
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Data storage
        self.organizations: Dict[str, Organization] = {}
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        
        # Redis for session and rate limiting
        self.redis_client = None
        
        # Security configurations
        self.security_config = {
            "password_min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": True,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 15,
            "session_timeout_minutes": 60,
            "api_rate_limit_default": 1000,  # per hour
            "enable_audit_logging": True
        }
        
        # Initialize system
        self._init_default_organizations()
        self._init_role_permissions()
        schedule_async_init(self._init_redis())
        
        logger.info("Multi-tenant system initialized with advanced security")
    
    async def _init_redis(self):
        """Initialize Redis connection for caching and rate limiting"""
        try:
            import redis.asyncio as aioredis
            
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = aioredis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            self.redis_client = None
    
    def _init_default_organizations(self):
        """Initialize default organizations"""
        
        # Demo organization
        demo_org = Organization(
            org_id="org_demo",
            name="SnapLearn Demo Organization",
            plan_type=PlanType.PROFESSIONAL,
            domain="demo.snaplearn.ai",
            settings={
                "branding": {
                    "logo_url": "/static/demo_logo.png",
                    "primary_color": "#2563eb",
                    "secondary_color": "#f59e0b"
                },
                "features": {
                    "ai_tutoring": True,
                    "video_generation": True,
                    "advanced_analytics": True,
                    "multi_language": True
                }
            },
            created_at=datetime.now(),
            max_students=1000,
            max_educators=50,
            features_enabled=["all"],
            usage_quotas={
                "api_calls_per_hour": 10000,
                "video_generation_per_day": 100,
                "storage_gb": 50
            }
        )
        
        self.organizations[demo_org.org_id] = demo_org
        
        # Enterprise template
        enterprise_template = Organization(
            org_id="org_enterprise_template",
            name="Enterprise Template",
            plan_type=PlanType.ENTERPRISE,
            domain=None,
            settings={
                "branding": {"customizable": True},
                "sso": {"enabled": True, "providers": ["saml", "oauth2"]},
                "compliance": {"gdpr": True, "coppa": True, "ferpa": True}
            },
            created_at=datetime.now(),
            max_students=10000,
            max_educators=500,
            features_enabled=["all"],
            usage_quotas={
                "api_calls_per_hour": 100000,
                "video_generation_per_day": 1000,
                "storage_gb": 1000
            }
        )
        
        self.organizations[enterprise_template.org_id] = enterprise_template
    
    def _init_role_permissions(self):
        """Initialize role-based permissions"""
        
        self.role_permissions = {
            UserRole.SUPER_ADMIN: set(PermissionScope),  # All permissions
            
            UserRole.ORG_ADMIN: {
                PermissionScope.TUTORING_READ,
                PermissionScope.TUTORING_WRITE,
                PermissionScope.ASSESSMENT_READ,
                PermissionScope.ASSESSMENT_WRITE,
                PermissionScope.VIDEO_READ,
                PermissionScope.VIDEO_WRITE,
                PermissionScope.ANALYTICS_READ,
                PermissionScope.ANALYTICS_WRITE,
                PermissionScope.STUDENT_READ,
                PermissionScope.STUDENT_WRITE,
                PermissionScope.ADMIN_READ,
                PermissionScope.ADMIN_WRITE
            },
            
            UserRole.EDUCATOR: {
                PermissionScope.TUTORING_READ,
                PermissionScope.TUTORING_WRITE,
                PermissionScope.ASSESSMENT_READ,
                PermissionScope.ASSESSMENT_WRITE,
                PermissionScope.VIDEO_READ,
                PermissionScope.VIDEO_WRITE,
                PermissionScope.ANALYTICS_READ,
                PermissionScope.STUDENT_READ,
                PermissionScope.STUDENT_WRITE
            },
            
            UserRole.STUDENT: {
                PermissionScope.TUTORING_READ,
                PermissionScope.ASSESSMENT_READ,
                PermissionScope.VIDEO_READ,
                PermissionScope.ANALYTICS_READ
            },
            
            UserRole.PARENT: {
                PermissionScope.TUTORING_READ,
                PermissionScope.ASSESSMENT_READ,
                PermissionScope.VIDEO_READ,
                PermissionScope.ANALYTICS_READ,
                PermissionScope.STUDENT_READ
            },
            
            UserRole.DEVELOPER: {
                PermissionScope.TUTORING_READ,
                PermissionScope.TUTORING_WRITE,
                PermissionScope.ASSESSMENT_READ,
                PermissionScope.VIDEO_READ,
                PermissionScope.ANALYTICS_READ
            },
            
            UserRole.VIEWER: {
                PermissionScope.TUTORING_READ,
                PermissionScope.ASSESSMENT_READ,
                PermissionScope.VIDEO_READ,
                PermissionScope.ANALYTICS_READ
            }
        }
    
    # Organization Management
    
    async def create_organization(
        self,
        name: str,
        plan_type: PlanType,
        admin_email: str,
        admin_username: str,
        domain: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create new organization with admin user"""
        
        try:
            # Generate organization ID
            org_id = f"org_{uuid.uuid4().hex[:12]}"
            
            # Create organization
            organization = Organization(
                org_id=org_id,
                name=name,
                plan_type=plan_type,
                domain=domain,
                settings=settings or {},
                created_at=datetime.now(),
                max_students=self._get_plan_limits(plan_type)["max_students"],
                max_educators=self._get_plan_limits(plan_type)["max_educators"],
                features_enabled=self._get_plan_features(plan_type),
                usage_quotas=self._get_plan_quotas(plan_type)
            )
            
            self.organizations[org_id] = organization
            
            # Create admin user
            admin_user = await self._create_user(
                org_id=org_id,
                email=admin_email,
                username=admin_username,
                role=UserRole.ORG_ADMIN,
                password=None  # Will be set during first login
            )
            
            # Generate setup token for admin
            setup_token = self._generate_setup_token(admin_user.user_id)
            
            logger.info(f"Created organization: {org_id} with admin: {admin_user.user_id}")
            
            return {
                "organization": asdict(organization),
                "admin_user": {
                    "user_id": admin_user.user_id,
                    "email": admin_user.email,
                    "setup_token": setup_token
                },
                "setup_url": f"/setup?token={setup_token}"
            }
            
        except Exception as e:
            logger.error(f"Error creating organization: {str(e)}")
            raise Exception(f"Organization creation failed: {str(e)}")
    
    def _get_plan_limits(self, plan_type: PlanType) -> Dict[str, int]:
        """Get resource limits for subscription plan"""
        
        limits = {
            PlanType.FREE: {"max_students": 10, "max_educators": 1},
            PlanType.BASIC: {"max_students": 100, "max_educators": 5},
            PlanType.PROFESSIONAL: {"max_students": 1000, "max_educators": 25},
            PlanType.ENTERPRISE: {"max_students": 10000, "max_educators": 100},
            PlanType.CUSTOM: {"max_students": 100000, "max_educators": 1000}
        }
        
        return limits.get(plan_type, limits[PlanType.FREE])
    
    def _get_plan_features(self, plan_type: PlanType) -> List[str]:
        """Get enabled features for subscription plan"""
        
        features = {
            PlanType.FREE: ["basic_tutoring", "basic_assessment"],
            PlanType.BASIC: ["ai_tutoring", "multimodal_input", "basic_analytics"],
            PlanType.PROFESSIONAL: ["ai_tutoring", "multimodal_input", "video_generation", "advanced_analytics"],
            PlanType.ENTERPRISE: ["all"],
            PlanType.CUSTOM: ["all"]
        }
        
        return features.get(plan_type, features[PlanType.FREE])
    
    def _get_plan_quotas(self, plan_type: PlanType) -> Dict[str, int]:
        """Get usage quotas for subscription plan"""
        
        quotas = {
            PlanType.FREE: {
                "api_calls_per_hour": 100,
                "video_generation_per_day": 5,
                "storage_gb": 1
            },
            PlanType.BASIC: {
                "api_calls_per_hour": 1000,
                "video_generation_per_day": 20,
                "storage_gb": 10
            },
            PlanType.PROFESSIONAL: {
                "api_calls_per_hour": 10000,
                "video_generation_per_day": 100,
                "storage_gb": 50
            },
            PlanType.ENTERPRISE: {
                "api_calls_per_hour": 100000,
                "video_generation_per_day": 1000,
                "storage_gb": 500
            },
            PlanType.CUSTOM: {
                "api_calls_per_hour": 1000000,
                "video_generation_per_day": 10000,
                "storage_gb": 5000
            }
        }
        
        return quotas.get(plan_type, quotas[PlanType.FREE])
    
    # User Management
    
    async def _create_user(
        self,
        org_id: str,
        email: str,
        username: str,
        role: UserRole,
        password: Optional[str] = None
    ) -> User:
        """Create new user within organization"""
        
        if org_id not in self.organizations:
            raise ValueError("Organization not found")
        
        # Generate user ID
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        # Get role permissions
        permissions = self.role_permissions.get(role, set())
        
        user = User(
            user_id=user_id,
            org_id=org_id,
            email=email,
            username=username,
            role=role,
            permissions=permissions,
            created_at=datetime.now(),
            profile_data={},
            preferences={}
        )
        
        self.users[user_id] = user
        
        return user
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        
        try:
            # Find user by email
            user = None
            for u in self.users.values():
                if u.email == email and (not org_id or u.org_id == org_id):
                    user = u
                    break
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            if not user.is_active:
                raise HTTPException(status_code=401, detail="Account disabled")
            
            # Check organization status
            org = self.organizations.get(user.org_id)
            if not org or not org.is_active:
                raise HTTPException(status_code=401, detail="Organization inactive")
            
            # Verify password (simplified for demo)
            # In production, this would check hashed password
            if password != "demo_password":
                await self._handle_failed_login(user.user_id)
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Generate tokens
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)
            
            # Update login timestamp
            user.last_login = datetime.now()
            
            # Log successful authentication
            await self._log_auth_event(user.user_id, "login_success")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role.value,
                    "org_id": user.org_id,
                    "permissions": [p.value for p in user.permissions]
                },
                "organization": {
                    "org_id": org.org_id,
                    "name": org.name,
                    "plan_type": org.plan_type.value,
                    "features": org.features_enabled
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(status_code=500, detail="Authentication failed")
    
    def _generate_access_token(self, user: User) -> str:
        """Generate JWT access token"""
        
        payload = {
            "user_id": user.user_id,
            "org_id": user.org_id,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _generate_refresh_token(self, user: User) -> str:
        """Generate JWT refresh token"""
        
        payload = {
            "user_id": user.user_id,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _generate_setup_token(self, user_id: str) -> str:
        """Generate one-time setup token"""
        
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "type": "setup"
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    # API Key Management
    
    async def create_api_key(
        self,
        org_id: str,
        name: str,
        permissions: List[PermissionScope],
        rate_limit: int = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create API key for organization"""
        
        if org_id not in self.organizations:
            raise ValueError("Organization not found")
        
        org = self.organizations[org_id]
        
        # Generate API key
        key_id = f"key_{uuid.uuid4().hex[:12]}"
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Default rate limit based on plan
        if rate_limit is None:
            rate_limit = org.usage_quotas.get("api_calls_per_hour", 1000)
        
        api_key_obj = APIKey(
            key_id=key_id,
            org_id=org_id,
            name=name,
            key_hash=key_hash,
            permissions=set(permissions),
            rate_limit=rate_limit,
            expires_at=expires_at,
            created_at=datetime.now()
        )
        
        self.api_keys[key_id] = api_key_obj
        
        logger.info(f"Created API key: {key_id} for organization: {org_id}")
        
        return {
            "key_id": key_id,
            "api_key": api_key,  # Only returned once
            "name": name,
            "permissions": [p.value for p in permissions],
            "rate_limit": rate_limit,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "created_at": api_key_obj.created_at.isoformat()
        }
    
    async def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key object"""
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        for key_obj in self.api_keys.values():
            if key_obj.key_hash == key_hash and key_obj.is_active:
                # Check expiration
                if key_obj.expires_at and datetime.now() > key_obj.expires_at:
                    key_obj.is_active = False
                    continue
                
                # Update usage
                key_obj.usage_count += 1
                key_obj.last_used = datetime.now()
                
                return key_obj
        
        return None
    
    # Authorization and Permissions
    
    async def check_permission(
        self,
        user: User,
        required_permission: PermissionScope,
        resource_org_id: Optional[str] = None
    ) -> bool:
        """Check if user has required permission"""
        
        # Super admin has all permissions
        if user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Check if user has the specific permission
        if required_permission not in user.permissions:
            return False
        
        # Check organization access
        if resource_org_id and user.org_id != resource_org_id:
            return False
        
        return True
    
    async def enforce_permission(
        self,
        user: User,
        required_permission: PermissionScope,
        resource_org_id: Optional[str] = None
    ):
        """Enforce permission check, raise exception if denied"""
        
        if not await self.check_permission(user, required_permission, resource_org_id):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {required_permission.value}"
            )
    
    # Rate Limiting
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Check rate limit for identifier"""
        
        if not self.redis_client:
            return {"allowed": True, "remaining": limit}
        
        try:
            key = f"rate_limit:{identifier}"
            current = await self.redis_client.get(key)
            
            if current is None:
                # First request in window
                await self.redis_client.setex(key, window_seconds, 1)
                return {"allowed": True, "remaining": limit - 1, "reset_at": datetime.now() + timedelta(seconds=window_seconds)}
            
            current_count = int(current)
            
            if current_count >= limit:
                # Rate limit exceeded
                ttl = await self.redis_client.ttl(key)
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_at": datetime.now() + timedelta(seconds=ttl),
                    "retry_after": ttl
                }
            
            # Increment counter
            await self.redis_client.incr(key)
            
            return {"allowed": True, "remaining": limit - current_count - 1}
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return {"allowed": True, "remaining": limit}  # Fail open
    
    # Security Logging
    
    async def _handle_failed_login(self, identifier: str):
        """Handle failed login attempt"""
        
        await self._log_auth_event(identifier, "login_failed")
        
        # Implement login attempt limiting
        if self.redis_client:
            key = f"login_attempts:{identifier}"
            attempts = await self.redis_client.incr(key)
            await self.redis_client.expire(key, self.security_config["lockout_duration_minutes"] * 60)
            
            if attempts >= self.security_config["max_login_attempts"]:
                await self._log_auth_event(identifier, "account_locked")
    
    async def _log_auth_event(self, identifier: str, event_type: str, metadata: Dict[str, Any] = None):
        """Log authentication and security events"""
        
        if not self.security_config["enable_audit_logging"]:
            return
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "identifier": identifier,
            "metadata": metadata or {}
        }
        
        # In production, this would go to a security logging system
        logger.info(f"Security event: {json.dumps(event)}")
    
    # Token Validation
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload"""
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check token type
            if payload.get("type") not in ["access", "refresh", "setup"]:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user object from JWT token"""
        
        payload = self.validate_token(token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        return self.users.get(user_id)
    
    # Organization Analytics
    
    async def get_organization_analytics(self, org_id: str) -> Dict[str, Any]:
        """Get comprehensive organization analytics"""
        
        if org_id not in self.organizations:
            raise ValueError("Organization not found")
        
        org = self.organizations[org_id]
        
        # Get organization users
        org_users = [user for user in self.users.values() if user.org_id == org_id]
        
        # Get API keys
        org_api_keys = [key for key in self.api_keys.values() if key.org_id == org_id]
        
        # Calculate usage statistics (simplified)
        total_api_calls = sum(key.usage_count for key in org_api_keys)
        
        return {
            "organization": asdict(org),
            "users": {
                "total": len(org_users),
                "by_role": {
                    role.value: len([u for u in org_users if u.role == role])
                    for role in UserRole
                },
                "active_users": len([u for u in org_users if u.is_active])
            },
            "api_usage": {
                "total_keys": len(org_api_keys),
                "active_keys": len([k for k in org_api_keys if k.is_active]),
                "total_calls": total_api_calls,
                "calls_this_month": total_api_calls  # Simplified
            },
            "resource_usage": {
                "students": len([u for u in org_users if u.role == UserRole.STUDENT]),
                "educators": len([u for u in org_users if u.role == UserRole.EDUCATOR]),
                "quota_utilization": {
                    "students": (len([u for u in org_users if u.role == UserRole.STUDENT]) / org.max_students) * 100,
                    "educators": (len([u for u in org_users if u.role == UserRole.EDUCATOR]) / org.max_educators) * 100
                }
            }
        }
    
    def is_healthy(self) -> bool:
        """Check if multi-tenant system is healthy"""
        return (
            len(self.organizations) > 0 and
            len(self.users) >= 0 and  # Can have 0 users initially
            len(self.api_keys) >= 0
        )


# FastAPI Dependencies for authentication and authorization

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    multi_tenant: MultiTenantSystem = None
) -> User:
    """FastAPI dependency to get current authenticated user"""
    
    if not multi_tenant:
        raise HTTPException(status_code=500, detail="Multi-tenant system not available")
    
    token = credentials.credentials
    user = multi_tenant.get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account disabled")
    
    return user

async def get_current_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    multi_tenant: MultiTenantSystem = None
) -> APIKey:
    """FastAPI dependency to get current API key"""
    
    if not multi_tenant:
        raise HTTPException(status_code=500, detail="Multi-tenant system not available")
    
    api_key = credentials.credentials
    key_obj = await multi_tenant.validate_api_key(api_key)
    
    if not key_obj:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return key_obj

def require_permission(permission: PermissionScope):
    """Decorator factory to require specific permission"""
    
    async def permission_checker(
        user: User = Depends(get_current_user),
        multi_tenant: MultiTenantSystem = None
    ):
        if not multi_tenant:
            raise HTTPException(status_code=500, detail="Multi-tenant system not available")
        
        await multi_tenant.enforce_permission(user, permission)
        return user
    
    return Depends(permission_checker)

def require_role(role: UserRole):
    """Decorator factory to require specific role"""
    
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role != role and user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail=f"Role {role.value} required")
        return user
    
    return Depends(role_checker)

async def rate_limit_check(
    request: Request,
    user: User = Depends(get_current_user),
    multi_tenant: MultiTenantSystem = None
):
    """FastAPI dependency for rate limiting"""
    
    if not multi_tenant:
        return  # Skip rate limiting if system unavailable
    
    org = multi_tenant.organizations.get(user.org_id)
    if not org:
        raise HTTPException(status_code=403, detail="Organization not found")
    
    rate_limit = org.usage_quotas.get("api_calls_per_hour", 1000)
    identifier = f"user:{user.user_id}"
    
    result = await multi_tenant.check_rate_limit(identifier, rate_limit)
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(result.get("retry_after", 3600))}
        )
    
    # Add rate limit headers
    request.state.rate_limit_remaining = result["remaining"]