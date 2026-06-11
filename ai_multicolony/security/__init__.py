"""Security module for AI-MultiColony.

Provides code security analysis, audit logging with hash-chain integrity,
a permission engine with RBAC, ABAC, dynamic escalation, and approval gates,
and a Fernet-encrypted credential vault.
"""

from .analyzer import SecurityAnalyzer, SecurityFinding, SEVERITY_WEIGHTS
from .audit import AuditTrail, MemoryAuditStorage, FileAuditStorage, AuditStorage
from .credential_vault import CredentialVault, VaultLockedError, CredentialNotFoundError
from .permissions import PermissionEngine, DEFAULT_ROLES, DEFAULT_PERMISSIONS

# Alias for convenience
AuditLogger = AuditTrail

__all__ = [
    # Analyzer
    "SecurityAnalyzer",
    "SecurityFinding",
    "SEVERITY_WEIGHTS",
    # Audit
    "AuditTrail",
    "AuditLogger",
    "MemoryAuditStorage",
    "FileAuditStorage",
    "AuditStorage",
    # Credential Vault
    "CredentialVault",
    "VaultLockedError",
    "CredentialNotFoundError",
    # Permissions
    "PermissionEngine",
    "DEFAULT_ROLES",
    "DEFAULT_PERMISSIONS",
]
