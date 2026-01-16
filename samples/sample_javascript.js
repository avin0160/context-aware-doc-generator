/**
 * Sample JavaScript Code for Testing Documentation Generator
 */

class UserManager {
  /**
   * Manages user accounts and authentication
   * @param {Object} databaseConnection - Active database connection
   */
  constructor(databaseConnection) {
    this.db = databaseConnection;
    this.cache = new Map();
  }

  /**
   * Create a new user account
   * @param {string} username - Unique username for the account
   * @param {string} email - User's email address
   * @param {string} password - Account password (will be hashed)
   * @returns {Promise<Object>} Created user object with id, username, and email
   * @throws {Error} If username or email already exists
   */
  async createUser(username, email, password) {
    if (await this._userExists(username, email)) {
      throw new Error('User already exists');
    }

    const hashedPassword = await this._hashPassword(password);
    const user = {
      username,
      email,
      password: hashedPassword
    };

    const userId = await this.db.insert('users', user);
    user.id = userId;

    this.cache.set(username, user);
    return user;
  }

  /**
   * Authenticate user with username and password
   * @param {string} username - Username to authenticate
   * @param {string} password - Password to verify
   * @returns {Promise<boolean>} True if authentication successful, false otherwise
   */
  async authenticate(username, password) {
    const user = await this.getUser(username);
    if (!user) {
      return false;
    }

    return await this._verifyPassword(password, user.password);
  }

  /**
   * Retrieve user by username
   * @param {string} username - Username to lookup
   * @returns {Promise<Object|null>} User object if found, null otherwise
   */
  async getUser(username) {
    if (this.cache.has(username)) {
      return this.cache.get(username);
    }

    const user = await this.db.query(
      'SELECT * FROM users WHERE username = ?',
      username
    );

    if (user) {
      this.cache.set(username, user);
    }

    return user;
  }

  /**
   * Check if user with username or email already exists
   * @private
   */
  async _userExists(username, email) {
    return (
      (await this.db.exists('users', { username })) ||
      (await this.db.exists('users', { email }))
    );
  }

  /**
   * Hash password using SHA-256
   * @private
   */
  async _hashPassword(password) {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(password).digest('hex');
  }

  /**
   * Verify password against hash
   * @private
   */
  async _verifyPassword(password, hashed) {
    const passwordHash = await this._hashPassword(password);
    return passwordHash === hashed;
  }
}

/**
 * Calculate statistical measures for an array of numbers
 * @param {number[]} numbers - Array of numeric values
 * @returns {Object} Object containing mean, median, and std deviation
 * @throws {Error} If array is empty
 * @example
 * calculateStatistics([1, 2, 3, 4, 5])
 * // Returns: { mean: 3.0, median: 3, stdDev: 1.41 }
 */
function calculateStatistics(numbers) {
  if (!numbers || numbers.length === 0) {
    throw new Error('Cannot calculate statistics for empty array');
  }

  const sum = numbers.reduce((a, b) => a + b, 0);
  const mean = sum / numbers.length;

  const sorted = [...numbers].sort((a, b) => a - b);
  const median =
    sorted.length % 2 === 0
      ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
      : sorted[Math.floor(sorted.length / 2)];

  const variance =
    numbers.reduce((sum, num) => sum + Math.pow(num - mean, 2), 0) /
    numbers.length;
  const stdDev = Math.sqrt(variance);

  return {
    mean,
    median,
    stdDev
  };
}

module.exports = { UserManager, calculateStatistics };
