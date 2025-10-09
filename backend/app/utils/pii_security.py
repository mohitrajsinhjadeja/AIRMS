"""
🔐 PII Tokenization and Security Module
Provides secure handling of Personally Identifiable Information (PII)
"""

import hashlib
import uuid
import logging
from typing import Any, Dict, List, Optional, Union
from cryptography.fernet import Fernet
import os
import base64

logger = logging.getLogger(__name__)

class PIITokenizer:
    """Handles secure tokenization and encryption of PII data"""
    
    def __init__(self):
        # Generate or load encryption key
        self.fernet_key = self._get_or_generate_key()
        self.fernet = Fernet(self.fernet_key)
        
    def _get_or_generate_key(self) -> bytes:
        """Get encryption key from environment or generate new one"""
        # Try to get key from environment variable
        key_b64 = os.getenv('AIRMS_PII_ENCRYPTION_KEY')
        
        if key_b64:
            try:
                return base64.urlsafe_b64decode(key_b64)
            except Exception as e:
                logger.warning(f"Invalid encryption key in environment: {e}")
        
        # Generate new key if not found
        key = Fernet.generate_key()
        key_b64 = base64.urlsafe_b64encode(key).decode()
        logger.warning(
            f"Generated new encryption key. Set AIRMS_PII_ENCRYPTION_KEY={key_b64} "
            "in environment for production use."
        )
        return key
    
    def hash_pii(self, value: str, include_salt: bool = True) -> str:
        """
        Generate a one-way hash token for sensitive info
        
        Args:
            value: The sensitive value to hash
            include_salt: Whether to include random salt (recommended)
            
        Returns:
            Hashed token string
        """
        if not value or not isinstance(value, str):
            return ""
        
        # Generate random salt per value to prevent rainbow table attacks
        if include_salt:
            salt = uuid.uuid4().hex
            salted_value = f"{value}:{salt}"
        else:
            salted_value = value
            
        # Create SHA-256 hash
        hash_object = hashlib.sha256(salted_value.encode())
        return hash_object.hexdigest()
    
    def encrypt_pii(self, value: str) -> str:
        """
        Encrypt PII data (reversible)
        
        Args:
            value: The sensitive value to encrypt
            
        Returns:
            Encrypted token string
        """
        if not value or not isinstance(value, str):
            return ""
            
        try:
            encrypted_bytes = self.fernet.encrypt(value.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt PII: {e}")
            return self.hash_pii(value)  # Fallback to hashing
    
    def decrypt_pii(self, token: str) -> Optional[str]:
        """
        Decrypt PII data (only works with encrypt_pii tokens)
        
        Args:
            token: The encrypted token to decrypt
            
        Returns:
            Decrypted original value or None if failed
        """
        if not token or not isinstance(token, str):
            return None
            
        try:
            decrypted_bytes = self.fernet.decrypt(token.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.warning(f"Failed to decrypt PII token: {e}")
            return None
    
    def mask_pii(self, value: str, mask_char: str = "X", keep_start: int = 2, keep_end: int = 2) -> str:
        """
        Create a masked version of PII for display purposes
        
        Args:
            value: The value to mask
            mask_char: Character to use for masking
            keep_start: Number of characters to keep at start
            keep_end: Number of characters to keep at end
            
        Returns:
            Masked string for display
        """
        if not value or len(value) <= (keep_start + keep_end):
            return mask_char * len(value) if value else ""
        
        start = value[:keep_start]
        end = value[-keep_end:] if keep_end > 0 else ""
        middle_length = len(value) - keep_start - keep_end
        middle = mask_char * middle_length
        
        return f"{start}{middle}{end}"
    
    def tokenize_risk_findings(self, risk_details: Dict[str, Any], use_encryption: bool = True) -> Dict[str, Any]:
        """
        Tokenize PII found in risk analysis results
        
        Args:
            risk_details: The risk analysis results containing PII findings
            use_encryption: Whether to use reversible encryption (True) or hashing (False)
            
        Returns:
            Risk details with tokenized PII values
        """
        tokenized_details = {}
        
        for risk_type, details in risk_details.items():
            if risk_type == "pii_leak" and "findings" in details:
                tokenized_details[risk_type] = self._tokenize_pii_findings(
                    details, use_encryption
                )
            else:
                # Copy non-PII risk details as-is
                tokenized_details[risk_type] = details.copy()
        
        return tokenized_details
    
    def _tokenize_pii_findings(self, pii_details: Dict[str, Any], use_encryption: bool) -> Dict[str, Any]:
        """Tokenize PII findings specifically"""
        tokenized = pii_details.copy()
        
        if "findings" in tokenized:
            for finding in tokenized["findings"]:
                if "matches" in finding:
                    original_matches = finding["matches"]
                    tokenized_matches = []
                    masked_matches = []
                    
                    for match in original_matches:
                        if isinstance(match, (list, tuple)):
                            # Handle nested matches
                            tokenized_match = []
                            masked_match = []
                            for item in match:
                                if isinstance(item, str):
                                    if use_encryption:
                                        token = self.encrypt_pii(item)
                                    else:
                                        token = self.hash_pii(item)
                                    mask = self.mask_pii(item)
                                    tokenized_match.append(token)
                                    masked_match.append(mask)
                                else:
                                    tokenized_match.append(item)
                                    masked_match.append(str(item))
                            tokenized_matches.append(tokenized_match)
                            masked_matches.append(masked_match)
                        elif isinstance(match, str):
                            # Handle string matches
                            if use_encryption:
                                token = self.encrypt_pii(match)
                            else:
                                token = self.hash_pii(match)
                            mask = self.mask_pii(match)
                            tokenized_matches.append(token)
                            masked_matches.append(mask)
                        else:
                            tokenized_matches.append(match)
                            masked_matches.append(str(match))
                    
                    # Store both tokenized (for database) and masked (for display)
                    finding["matches"] = tokenized_matches
                    finding["masked_matches"] = masked_matches
        
        return tokenized
    
    def create_safe_log_entry(self, 
                            message: str, 
                            risk_score: int, 
                            risk_flags: List[str],
                            conversation_id: str,
                            risk_details: Dict[str, Any],
                            use_encryption: bool = True) -> Dict[str, Any]:
        """
        Create a safe log entry with tokenized PII
        
        Args:
            message: Original message (will be hashed for storage)
            risk_score: Risk analysis score
            risk_flags: Risk categories detected
            conversation_id: Chat conversation ID
            risk_details: Detailed risk analysis results
            use_encryption: Whether to use encryption vs hashing
            
        Returns:
            Safe log entry with no raw PII
        """
        # Hash the original message for audit purposes (one-way)
        message_hash = self.hash_pii(message, include_salt=False)
        
        # Tokenize PII in risk details
        safe_risk_details = self.tokenize_risk_findings(risk_details, use_encryption)
        
        # Create safe log entry
        safe_entry = {
            "conversation_id": conversation_id,
            "message_hash": message_hash,  # Hashed original message
            "message_length": len(message),
            "risk_score": risk_score,
            "risk_flags": risk_flags,
            "risk_details": safe_risk_details,  # Tokenized PII
            "pii_detected": "PII Detected" in risk_flags,
            "token_method": "encryption" if use_encryption else "hashing",
            "timestamp": None  # Will be set by database
        }
        
        return safe_entry


# Global tokenizer instance
pii_tokenizer = PIITokenizer()

# Convenience functions
def hash_pii(value: str) -> str:
    """Quick hash function for PII"""
    return pii_tokenizer.hash_pii(value)

def encrypt_pii(value: str) -> str:
    """Quick encrypt function for PII"""
    return pii_tokenizer.encrypt_pii(value)

def decrypt_pii(token: str) -> Optional[str]:
    """Quick decrypt function for PII"""
    return pii_tokenizer.decrypt_pii(token)

def mask_pii_for_display(value: str) -> str:
    """Quick mask function for display"""
    return pii_tokenizer.mask_pii(value)

def create_safe_log(message: str, risk_score: int, risk_flags: List[str], 
                   conversation_id: str, risk_details: Dict[str, Any]) -> Dict[str, Any]:
    """Quick function to create safe log entry"""
    return pii_tokenizer.create_safe_log_entry(
        message, risk_score, risk_flags, conversation_id, risk_details
    )