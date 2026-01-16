/**
 * Sample Java Code for Testing Documentation Generator
 */

import java.util.HashMap;
import java.util.Map;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Manages user accounts and authentication
 */
public class UserManager {
    private DatabaseConnection db;
    private Map<String, User> cache;

    /**
     * Initialize UserManager with database connection
     * 
     * @param databaseConnection Active database connection
     */
    public UserManager(DatabaseConnection databaseConnection) {
        this.db = databaseConnection;
        this.cache = new HashMap<>();
    }

    /**
     * Create a new user account
     * 
     * @param username Unique username for the account
     * @param email User's email address
     * @param password Account password (will be hashed)
     * @return Created user object with id, username, and email
     * @throws UserExistsException If username or email already exists
     */
    public User createUser(String username, String email, String password) 
            throws UserExistsException {
        if (userExists(username, email)) {
            throw new UserExistsException("User already exists");
        }

        String hashedPassword = hashPassword(password);
        User user = new User(username, email, hashedPassword);

        int userId = db.insert("users", user);
        user.setId(userId);

        cache.put(username, user);
        return user;
    }

    /**
     * Authenticate user with username and password
     * 
     * @param username Username to authenticate
     * @param password Password to verify
     * @return true if authentication successful, false otherwise
     */
    public boolean authenticate(String username, String password) {
        User user = getUser(username);
        if (user == null) {
            return false;
        }

        return verifyPassword(password, user.getPassword());
    }

    /**
     * Retrieve user by username
     * 
     * @param username Username to lookup
     * @return User object if found, null otherwise
     */
    public User getUser(String username) {
        if (cache.containsKey(username)) {
            return cache.get(username);
        }

        User user = db.query("SELECT * FROM users WHERE username = ?", username);
        if (user != null) {
            cache.put(username, user);
        }

        return user;
    }

    /**
     * Check if user with username or email already exists
     */
    private boolean userExists(String username, String email) {
        return db.exists("users", "username", username) || 
               db.exists("users", "email", email);
    }

    /**
     * Hash password using SHA-256
     */
    private String hashPassword(String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(password.getBytes());
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Verify password against hash
     */
    private boolean verifyPassword(String password, String hashed) {
        return hashPassword(password).equals(hashed);
    }
}

/**
 * User data model
 */
class User {
    private Integer id;
    private String username;
    private String email;
    private String password;

    public User(String username, String email, String password) {
        this.username = username;
        this.email = email;
        this.password = password;
    }

    // Getters and setters
    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    public String getPassword() { return password; }
}

class UserExistsException extends Exception {
    public UserExistsException(String message) {
        super(message);
    }
}
