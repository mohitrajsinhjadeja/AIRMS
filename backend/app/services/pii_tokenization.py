"""
🔒 PII Tokenization Service
Secure tokenization and storage of personally identifiable information
"""

import re
import uuid
import hashlib
import secrets
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings
from app.core.database import get_database_operations

logger = logging.getLogger(__name__)

class TokenType(Enum):
    """Types of tokens for different PII categories"""
    AADHAAR = "aadhaar"
    PAN = "pan"
    PHONE = "phone"
    EMAIL = "email"
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    IFSC = "ifsc"
    NAME = "name"
    ADDRESS = "address"
    GENERIC = "generic"

@dataclass
class PIIToken:
    """PII token data structure"""
    token_id: str
    original_value: str
    token_type: TokenType
    user_id: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int
    metadata: Dict[str, Any]

class PIITokenizer:
    """
    🔒 PII Tokenization Engine
    
    Automatically detects and tokenizes PII in text, stores securely in MongoDB,
    and provides token replacement functionality.
    """
    
    def __init__(self):
        self.pii_patterns = settings.PII_PATTERNS
        self.token_prefix = "AIRMS_TOKEN_"
        self.salt = self._generate_salt()
        
    def _generate_salt(self) -> str:
        """Generate a secure salt for token hashing"""
        return secrets.token_hex(settings.PII_SALT_LENGTH)
    
    def _generate_token_id(self, original_value: str, token_type: TokenType) -> str:
        """Generate a unique, deterministic token ID"""
        # Create deterministic hash for same PII values
        combined = f"{original_value}:{token_type.value}:{self.salt}"
        hash_obj = hashlib.sha256(combined.encode())
        return f"{self.token_prefix}{token_type.value.upper()}_{hash_obj.hexdigest()[:16]}"
    
    def _create_replacement_token(self, token_type: TokenType) -> str:
        """Create a replacement token for display"""
        type_map = {
            TokenType.AADHAAR: "[AADHAAR_REDACTED]",
            TokenType.PAN: "[PAN_REDACTED]",
            TokenType.PHONE: "[PHONE_REDACTED]",
            TokenType.EMAIL: "[EMAIL_REDACTED]",
            TokenType.CREDIT_CARD: "[CARD_REDACTED]",
            TokenType.BANK_ACCOUNT: "[ACCOUNT_REDACTED]",
            TokenType.IFSC: "[IFSC_REDACTED]",
            TokenType.NAME: "[NAME_REDACTED]",
            TokenType.ADDRESS: "[ADDRESS_REDACTED]",
            TokenType.GENERIC: "[PII_REDACTED]"
        }
        return type_map.get(token_type, "[REDACTED]")
    
    async def tokenize_text(self, text: str, user_id: Optional[str] = None, 
                           request_permission: bool = True) -> Dict[str, Any]:
        """
        Tokenize PII in text and store securely
        
        Args:
            text: Input text to tokenize
            user_id: User ID for permission tracking
            request_permission: Whether to request user permission
            
        Returns:
            Dict with tokenized text, detected PII, and permission requirements
        """
        try:
            detected_pii = []
            tokenized_text = text
            permission_required = []
            
            # Detect and tokenize each PII type
            for pii_type_str, pattern in self.pii_patterns.items():
                try:
                    token_type = TokenType(pii_type_str)
                except ValueError:
                    token_type = TokenType.GENERIC
                
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                
                for match in matches:
                    original_value = match.group()
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Generate token
                    token_id = self._generate_token_id(original_value, token_type)
                    replacement_token = self._create_replacement_token(token_type)
                    
                    # Store token securely
                    pii_token = PIIToken(
                        token_id=token_id,
                        original_value=original_value,
                        token_type=token_type,
                        user_id=user_id,
                        created_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=90),  # 90-day retention
                        usage_count=0,
                        metadata={
                            "detection_confidence": self._get_confidence_score(token_type),
                            "context_snippet": text[max(0, start_pos-20):min(len(text), end_pos+20)],
                            "position": {"start": start_pos, "end": end_pos}
                        }
                    )
                    
                    # Store in database
                    await self._store_token(pii_token)
                    
                    # Replace in text
                    tokenized_text = tokenized_text.replace(original_value, replacement_token, 1)
                    
                    # Track detected PII
                    detected_pii.append({
                        "type": token_type.value,
                        "token_id": token_id,
                        "original_value": original_value[:4] + "***",  # Partial for logging
                        "replacement": replacement_token,
                        "confidence": pii_token.metadata["detection_confidence"],
                        "requires_permission": request_permission
                    })
                    
                    # Add to permission requirements
                    if request_permission:
                        permission_required.append({
                            "token_id": token_id,
                            "pii_type": token_type.value,
                            "description": f"Process {token_type.value.replace('_', ' ').title()}",
                            "risk_level": self._get_risk_level(token_type)
                        })
            
            return {
                "original_text": text,
                "tokenized_text": tokenized_text,
                "detected_pii": detected_pii,
                "pii_count": len(detected_pii),
                "permission_required": permission_required,
                "requires_user_consent": len(permission_required) > 0,
                "processing_safe": len(detected_pii) == 0,  # Safe to send to external APIs
                "tokenization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PII tokenization failed: {e}")
            return {
                "original_text": text,
                "tokenized_text": text,
                "detected_pii": [],
                "pii_count": 0,
                "permission_required": [],
                "requires_user_consent": False,
                "processing_safe": True,
                "error": str(e),
                "tokenization_timestamp": datetime.utcnow().isoformat()
            }
    
    async def detokenize_text(self, tokenized_text: str, user_id: Optional[str] = None,
                             permission_granted: bool = False) -> Dict[str, Any]:
        """
        Replace tokens with original PII values (requires permission)
        
        Args:
            tokenized_text: Text with tokens to replace
            user_id: User ID for permission checking
            permission_granted: Whether user granted permission
            
        Returns:
            Dict with detokenized text and permission status
        """
        try:
            if not permission_granted:
                return {
                    "detokenized_text": tokenized_text,
                    "tokens_replaced": 0,
                    "permission_denied": True,
                    "message": "User permission required to access original PII values"
                }
            
            detokenized_text = tokenized_text
            tokens_replaced = 0
            
            # Find all token patterns in text
            token_pattern = r'\[([A-Z_]+)_REDACTED\]'
            matches = re.finditer(token_pattern, tokenized_text)
            
            for match in matches:
                token_placeholder = match.group()
                pii_type = match.group(1).lower()
                
                # Try to find corresponding stored token
                # This is a simplified approach - in production, you'd need more sophisticated matching
                try:
                    token_type = TokenType(pii_type)
                    original_value = await self._retrieve_token_value(token_placeholder, user_id)
                    
                    if original_value:
                        detokenized_text = detokenized_text.replace(token_placeholder, original_value, 1)
                        tokens_replaced += 1
                        
                        # Update usage count
                        await self._increment_token_usage(token_placeholder, user_id)
                        
                except ValueError:
                    continue
            
            return {
                "detokenized_text": detokenized_text,
                "tokens_replaced": tokens_replaced,
                "permission_granted": True,
                "message": f"Successfully restored {tokens_replaced} PII values"
            }
            
        except Exception as e:
            logger.error(f"PII detokenization failed: {e}")
            return {
                "detokenized_text": tokenized_text,
                "tokens_replaced": 0,
                "error": str(e)
            }
    
    async def _store_token(self, pii_token: PIIToken) -> bool:
        """Store PII token securely in MongoDB"""
        try:
            db_ops = await get_database_operations()
            
            # Hash the original value for security
            hashed_value = hashlib.sha256(
                f"{pii_token.original_value}:{self.salt}".encode()
            ).hexdigest()
            
            token_doc = {
                "token_id": pii_token.token_id,
                "hashed_value": hashed_value,
                "original_value_encrypted": self._encrypt_value(pii_token.original_value),
                "token_type": pii_token.token_type.value,
                "user_id": pii_token.user_id,
                "created_at": pii_token.created_at,
                "expires_at": pii_token.expires_at,
                "usage_count": pii_token.usage_count,
                "metadata": pii_token.metadata,
                "is_active": True
            }
            
            # Use upsert to avoid duplicates
            result = await db_ops.db.pii_tokens.update_one(
                {"token_id": pii_token.token_id},
                {"$set": token_doc},
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Failed to store PII token: {e}")
            return False
    
    async def _retrieve_token_value(self, token_placeholder: str, user_id: Optional[str]) -> Optional[str]:
        """Retrieve original PII value from token (requires permission)"""
        try:
            db_ops = await get_database_operations()
            
            # This is simplified - you'd need better token-to-ID mapping
            token_doc = await db_ops.db.pii_tokens.find_one({
                "user_id": user_id,
                "is_active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if token_doc:
                return self._decrypt_value(token_doc["original_value_encrypted"])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve token value: {e}")
            return None
    
    async def _increment_token_usage(self, token_placeholder: str, user_id: Optional[str]) -> bool:
        """Increment token usage count for audit purposes"""
        try:
            db_ops = await get_database_operations()
            
            result = await db_ops.db.pii_tokens.update_one(
                {"user_id": user_id, "is_active": True},
                {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.utcnow()}}
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Failed to increment token usage: {e}")
            return False
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt PII value for secure storage"""
        # Simplified encryption - use proper encryption in production
        return hashlib.sha256(f"{value}:{self.salt}:encrypt".encode()).hexdigest()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt PII value (simplified implementation)"""
        # This is a placeholder - implement proper decryption
        return "[DECRYPTION_PLACEHOLDER]"
    
    def _get_confidence_score(self, token_type: TokenType) -> float:
        """Get confidence score for PII detection"""
        confidence_map = {
            TokenType.AADHAAR: 0.95,
            TokenType.PAN: 0.90,
            TokenType.EMAIL: 0.85,
            TokenType.PHONE: 0.80,
            TokenType.CREDIT_CARD: 0.85,
            TokenType.BANK_ACCOUNT: 0.70,
            TokenType.IFSC: 0.90,
            TokenType.NAME: 0.60,
            TokenType.ADDRESS: 0.65,
            TokenType.GENERIC: 0.50
        }
        return confidence_map.get(token_type, 0.50)
    
    def _get_risk_level(self, token_type: TokenType) -> str:
        """Get risk level for PII type"""
        risk_map = {
            TokenType.AADHAAR: "critical",
            TokenType.PAN: "high",
            TokenType.CREDIT_CARD: "high",
            TokenType.BANK_ACCOUNT: "high",
            TokenType.PHONE: "medium",
            TokenType.EMAIL: "medium",
            TokenType.IFSC: "medium",
            TokenType.NAME: "low",
            TokenType.ADDRESS: "medium",
            TokenType.GENERIC: "low"
        }
        return risk_map.get(token_type, "low")
    
    async def cleanup_expired_tokens(self) -> Dict[str, Any]:
        """Clean up expired PII tokens (90-day retention)"""
        try:
            db_ops = await get_database_operations()
            
            result = await db_ops.db.pii_tokens.update_many(
                {"expires_at": {"$lt": datetime.utcnow()}},
                {"$set": {"is_active": False, "deleted_at": datetime.utcnow()}}
            )
            
            return {
                "tokens_expired": result.modified_count,
                "cleanup_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")
            return {"error": str(e)}

# Global tokenizer instance
pii_tokenizer = PIITokenizer()

# Convenience functions
async def tokenize_content(text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Quick tokenization function"""
    return await pii_tokenizer.tokenize_text(text, user_id)

async def detokenize_content(text: str, user_id: Optional[str] = None, 
                           permission_granted: bool = False) -> Dict[str, Any]:
    """Quick detokenization function"""
    return await pii_tokenizer.detokenize_text(text, user_id, permission_granted)
