"""
Password Utility Functions.
"""
import bcrypt
import logging

logger = logging.getLogger(__name__)


class PasswordHandler:
    """
    Handles password hashing and verification using bcrypt.
    """
    
    @staticmethod
    def hash_password(password):
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password, hashed_password):
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            Boolean indicating if password matches
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
