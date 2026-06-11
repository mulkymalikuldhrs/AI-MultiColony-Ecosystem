"""Fernet-encrypted credential vault for AI-MultiColony.

Provides secure storage and retrieval of credentials using
AES-128-CBC + HMAC-SHA256 via Fernet symmetric encryption.
The Fernet key is derived from a master password using
PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP recommendation).

Features:
  - Encrypt-at-rest for all stored credentials
  - Master password rotation with re-encryption
  - Encrypted vault export/import for backup
  - Full audit logging via structlog
  - Salt stored in plaintext (not secret); only the derived key is secret
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List, Optional

import structlog
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = structlog.get_logger(__name__)

# OWASP 2023 recommendation: 600,000 iterations for PBKDF2-HMAC-SHA256
_PBKDF2_ITERATIONS = 600_000
# Fernet requires 32-byte keys (URL-safe base64 encoded)
_KEY_LENGTH = 32


class VaultLockedError(Exception):
    """Raised when vault operations are attempted without a valid key."""


class CredentialNotFoundError(KeyError):
    """Raised when a requested credential key is not found in the vault."""


class CredentialVault:
    """Fernet-encrypted credential vault.

    Stores credentials encrypted at rest using Fernet symmetric encryption
    (AES-128-CBC + HMAC-SHA256). The Fernet key is derived from a master
    password using PBKDF2-HMAC-SHA256 with 600,000 iterations.

    The salt is stored in plaintext (it is not secret). Only the derived
    Fernet key is kept in memory and never persisted.

    Example::

        vault = CredentialVault("my-master-password")
        vault.store("api_key", "sk-test-123")
        assert vault.retrieve("api_key") == "sk-test-123"
        vault.delete("api_key")
    """

    def __init__(self, master_password: str, salt: Optional[bytes] = None) -> None:
        """Initialize the credential vault.

        Args:
            master_password: Master password used to derive the Fernet key.
            salt: Optional salt for key derivation. If None, a random
                  16-byte salt is generated.

        Raises:
            ValueError: If master_password is empty.
        """
        if not master_password:
            raise ValueError("Master password must not be empty")

        self._salt: bytes = salt if salt is not None else os.urandom(16)
        self._fernet: Fernet = self._build_fernet(master_password)
        self._vault: Dict[str, str] = {}

        logger.info(
            "credential_vault.initialized",
            salt_provided=salt is not None,
        )

    # ------------------------------------------------------------------
    # Key derivation
    # ------------------------------------------------------------------

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive a Fernet-compatible key using PBKDF2-HMAC-SHA256.

        Args:
            password: Master password string.
            salt: Cryptographic salt bytes.

        Returns:
            URL-safe base64-encoded 32-byte key suitable for Fernet.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=_KEY_LENGTH,
            salt=salt,
            iterations=_PBKDF2_ITERATIONS,
        )
        raw_key: bytes = kdf.derive(password.encode("utf-8"))
        return base64.urlsafe_b64encode(raw_key)

    def _build_fernet(self, password: str) -> Fernet:
        """Build a Fernet instance from a password and the current salt.

        Args:
            password: Master password string.

        Returns:
            Configured Fernet instance.
        """
        key = self._derive_key(password, self._salt)
        return Fernet(key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store(self, key: str, value: str) -> None:
        """Encrypt and store a credential.

        Args:
            key: Credential key/name.
            value: Plaintext credential value to encrypt and store.
        """
        encrypted = self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")
        self._vault[key] = encrypted

        logger.info(
            "credential_vault.stored",
            key=key,
        )

    def retrieve(self, key: str) -> str:
        """Decrypt and retrieve a stored credential.

        Args:
            key: Credential key/name to look up.

        Returns:
            Decrypted plaintext credential value.

        Raises:
            CredentialNotFoundError: If the key does not exist in the vault.
            VaultLockedError: If decryption fails (wrong master password).
        """
        encrypted = self._vault.get(key)
        if encrypted is None:
            logger.warning("credential_vault.key_not_found", key=key)
            raise CredentialNotFoundError(key)

        try:
            plaintext_bytes = self._fernet.decrypt(encrypted.encode("utf-8"))
            logger.info("credential_vault.retrieved", key=key)
            return plaintext_bytes.decode("utf-8")
        except InvalidToken as exc:
            logger.error("credential_vault.decrypt_failed", key=key)
            raise VaultLockedError(
                "Decryption failed — the master password may be incorrect"
            ) from exc

    def delete(self, key: str) -> bool:
        """Delete a stored credential.

        Args:
            key: Credential key/name to delete.

        Returns:
            True if the credential was found and deleted, False otherwise.
        """
        if key in self._vault:
            del self._vault[key]
            logger.info("credential_vault.deleted", key=key)
            return True

        logger.warning("credential_vault.delete_key_not_found", key=key)
        return False

    def list_keys(self) -> List[str]:
        """List all stored credential keys.

        Returns:
            List of credential key names. Values are never exposed.
        """
        keys = list(self._vault.keys())
        logger.info("credential_vault.list_keys", count=len(keys))
        return keys

    def rotate_master_password(self, old_password: str, new_password: str) -> None:
        """Rotate the master password, re-encrypting all stored credentials.

        Validates the old password by attempting decryption, then
        re-encrypts every credential under the new password.

        Args:
            old_password: Current master password.
            new_password: New master password to use going forward.

        Raises:
            VaultLockedError: If the old password is incorrect.
            ValueError: If new_password is empty.
        """
        if not new_password:
            raise ValueError("New master password must not be empty")

        # Validate old password by trying to build a Fernet and decrypt one entry
        old_fernet = self._build_fernet(old_password)
        for key, encrypted in self._vault.items():
            try:
                old_fernet.decrypt(encrypted.encode("utf-8"))
            except InvalidToken as exc:
                logger.error("credential_vault.rotation_failed_bad_password")
                raise VaultLockedError(
                    "Old password is incorrect — cannot rotate"
                ) from exc

        # Decrypt all values with old key
        decrypted_entries: Dict[str, str] = {}
        for key, encrypted in self._vault.items():
            plaintext_bytes = old_fernet.decrypt(encrypted.encode("utf-8"))
            decrypted_entries[key] = plaintext_bytes.decode("utf-8")

        # Generate new salt and Fernet for the new password
        self._salt = os.urandom(16)
        self._fernet = self._build_fernet(new_password)

        # Re-encrypt all values with the new key
        self._vault.clear()
        for key, value in decrypted_entries.items():
            encrypted = self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")
            self._vault[key] = encrypted

        logger.info(
            "credential_vault.password_rotated",
            re_encrypted_count=len(decrypted_entries),
        )

    def export_vault(self, password: str) -> Dict[str, Any]:
        """Export the encrypted vault for backup.

        The exported data includes the salt and all encrypted entries.
        The caller must provide the correct master password to verify
        identity before export is allowed.

        Args:
            password: Master password for verification.

        Returns:
            Dictionary with 'salt' (base64-encoded) and 'entries'
            (dict of encrypted values).

        Raises:
            VaultLockedError: If the password is incorrect.
        """
        # Verify the password
        try:
            test_fernet = self._build_fernet(password)
            # Try decrypting one entry if any exist to fully validate
            if self._vault:
                first_key = next(iter(self._vault))
                test_fernet.decrypt(self._vault[first_key].encode("utf-8"))
        except InvalidToken as exc:
            logger.error("credential_vault.export_failed_bad_password")
            raise VaultLockedError(
                "Export failed — incorrect master password"
            ) from exc

        export_data: Dict[str, Any] = {
            "salt": base64.urlsafe_b64encode(self._salt).decode("utf-8"),
            "entries": dict(self._vault),
        }

        logger.info(
            "credential_vault.exported",
            entry_count=len(self._vault),
        )
        return export_data

    def import_vault(self, data: Dict[str, Any], password: str) -> None:
        """Import an encrypted vault from a backup.

        Replaces all current vault contents with the imported data.
        The password must match the one used when the vault was exported.

        Args:
            data: Dictionary with 'salt' (base64-encoded) and 'entries'
                  (dict of encrypted values).
            password: Master password that was used for the exported vault.

        Raises:
            VaultLockedError: If the password cannot decrypt the imported data.
            ValueError: If the import data is malformed.
        """
        if "salt" not in data or "entries" not in data:
            raise ValueError(
                "Import data must contain 'salt' and 'entries' keys"
            )

        # Restore the salt from the backup
        imported_salt = base64.urlsafe_b64decode(data["salt"].encode("utf-8"))
        imported_fernet = self._build_fernet_with_salt(password, imported_salt)

        # Validate by trying to decrypt one entry
        imported_entries: Dict[str, str] = data["entries"]
        if imported_entries:
            first_key = next(iter(imported_entries))
            try:
                imported_fernet.decrypt(
                    imported_entries[first_key].encode("utf-8")
                )
            except InvalidToken as exc:
                logger.error("credential_vault.import_failed_bad_password")
                raise VaultLockedError(
                    "Import failed — password does not match exported vault"
                ) from exc

        # Apply the imported vault
        self._salt = imported_salt
        self._fernet = imported_fernet
        self._vault = dict(imported_entries)

        logger.info(
            "credential_vault.imported",
            entry_count=len(self._vault),
        )

    def _build_fernet_with_salt(self, password: str, salt: bytes) -> Fernet:
        """Build a Fernet instance with an explicit salt.

        Used during import when we need to construct a Fernet with
        the backup's salt rather than self._salt.

        Args:
            password: Master password string.
            salt: Salt bytes to use for key derivation.

        Returns:
            Configured Fernet instance.
        """
        key = self._derive_key(password, salt)
        return Fernet(key)

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of stored credentials."""
        return len(self._vault)

    def __contains__(self, key: str) -> bool:
        """Check if a credential key exists in the vault."""
        return key in self._vault

    def __repr__(self) -> str:
        """Return a safe string representation (no secrets exposed)."""
        return (
            f"{self.__class__.__name__}("
            f"entries={len(self._vault)}, "
            f"salt={self._salt.hex()[:8]}...)"
        )
