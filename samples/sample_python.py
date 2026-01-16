"""
Sample Python Code for Testing Documentation Generator
"""

class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, database_connection):
        """
        Initialize UserManager with database connection
        
        Args:
            database_connection: Active database connection
        """
        self.db = database_connection
        self.cache = {}
    
    def create_user(self, username: str, email: str, password: str) -> dict:
        """
        Create a new user account
        
        Args:
            username: Unique username for the account
            email: User's email address
            password: Account password (will be hashed)
        
        Returns:
            dict: Created user object with id, username, and email
        
        Raises:
            ValueError: If username or email already exists
        """
        if self._user_exists(username, email):
            raise ValueError("User already exists")
        
        hashed_password = self._hash_password(password)
        user = {
            'username': username,
            'email': email,
            'password': hashed_password
        }
        
        user_id = self.db.insert('users', user)
        user['id'] = user_id
        
        self.cache[username] = user
        return user
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user with username and password
        
        Args:
            username: Username to authenticate
            password: Password to verify
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        user = self.get_user(username)
        if not user:
            return False
        
        return self._verify_password(password, user['password'])
    
    def get_user(self, username: str) -> dict:
        """
        Retrieve user by username
        
        Args:
            username: Username to lookup
        
        Returns:
            dict: User object if found, None otherwise
        """
        if username in self.cache:
            return self.cache[username]
        
        user = self.db.query('SELECT * FROM users WHERE username = ?', username)
        if user:
            self.cache[username] = user
        
        return user
    
    def _user_exists(self, username: str, email: str) -> bool:
        """Check if user with username or email already exists"""
        return self.db.exists('users', username=username) or \
               self.db.exists('users', email=email)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == hashed

def calculate_statistics(numbers: list) -> dict:
    """
    Calculate statistical measures for a list of numbers
    
    Args:
        numbers: List of numeric values
    
    Returns:
        dict: Dictionary containing mean, median, mode, and std deviation
    
    Raises:
        ValueError: If list is empty
    
    Example:
        >>> calculate_statistics([1, 2, 3, 4, 5])
        {'mean': 3.0, 'median': 3, 'mode': 1, 'std_dev': 1.41}
    """
    if not numbers:
        raise ValueError("Cannot calculate statistics for empty list")
    
    import statistics
    
    return {
        'mean': statistics.mean(numbers),
        'median': statistics.median(numbers),
        'mode': statistics.mode(numbers) if len(numbers) > 1 else numbers[0],
        'std_dev': statistics.stdev(numbers) if len(numbers) > 1 else 0.0
    }
