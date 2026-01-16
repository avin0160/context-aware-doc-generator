/**
 * Sample TypeScript Code for Testing Documentation Generator
 */

interface DatabaseConnection {
  insert(table: string, data: any): Promise<number>;
  query(sql: string, ...params: any[]): Promise<any>;
  exists(table: string, conditions: any): Promise<boolean>;
}

interface User {
  id?: number;
  username: string;
  email: string;
  password: string;
}

interface Statistics {
  mean: number;
  median: number;
  stdDev: number;
}

/**
 * Manages user accounts and authentication
 */
class UserManager {
  private db: DatabaseConnection;
  private cache: Map<string, User>;

  /**
   * Initialize UserManager with database connection
   * @param databaseConnection - Active database connection
   */
  constructor(databaseConnection: DatabaseConnection) {
    this.db = databaseConnection;
    this.cache = new Map<string, User>();
  }

  /**
   * Create a new user account
   * @param username - Unique username for the account
   * @param email - User's email address
   * @param password - Account password (will be hashed)
   * @returns Created user object with id, username, and email
   * @throws {Error} If username or email already exists
   */
  async createUser(
    username: string,
    email: string,
    password: string
  ): Promise<User> {
    if (await this._userExists(username, email)) {
      throw new Error('User already exists');
    }

    const hashedPassword = await this._hashPassword(password);
    const user: User = {
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
   * @param username - Username to authenticate
   * @param password - Password to verify
   * @returns True if authentication successful, false otherwise
   */
  async authenticate(username: string, password: string): Promise<boolean> {
    const user = await this.getUser(username);
    if (!user) {
      return false;
    }

    return await this._verifyPassword(password, user.password);
  }

  /**
   * Retrieve user by username
   * @param username - Username to lookup
   * @returns User object if found, null otherwise
   */
  async getUser(username: string): Promise<User | null> {
    if (this.cache.has(username)) {
      return this.cache.get(username)!;
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
  private async _userExists(username: string, email: string): Promise<boolean> {
    return (
      (await this.db.exists('users', { username })) ||
      (await this.db.exists('users', { email }))
    );
  }

  /**
   * Hash password using SHA-256
   * @private
   */
  private async _hashPassword(password: string): Promise<string> {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(password).digest('hex');
  }

  /**
   * Verify password against hash
   * @private
   */
  private async _verifyPassword(
    password: string,
    hashed: string
  ): Promise<boolean> {
    const passwordHash = await this._hashPassword(password);
    return passwordHash === hashed;
  }
}

/**
 * Calculate statistical measures for an array of numbers
 * @param numbers - Array of numeric values
 * @returns Object containing mean, median, and std deviation
 * @throws {Error} If array is empty
 * @example
 * ```typescript
 * calculateStatistics([1, 2, 3, 4, 5])
 * // Returns: { mean: 3.0, median: 3, stdDev: 1.41 }
 * ```
 */
function calculateStatistics(numbers: number[]): Statistics {
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

export { UserManager, calculateStatistics, User, Statistics };
