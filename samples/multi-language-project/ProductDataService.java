/**
 * Data Access Service - Java
 * Database operations for e-commerce platform
 */

package com.ecommerce.service;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.logging.Logger;

/**
 * Product data access service
 * Handles all database operations for products
 */
public class ProductDataService {
    private static final Logger logger = Logger.getLogger(ProductDataService.class.getName());
    private final Connection connection;

    /**
     * Initialize data service with database connection
     * 
     * @param connection Active database connection
     */
    public ProductDataService(Connection connection) {
        this.connection = connection;
    }

    /**
     * Retrieve product by ID
     * 
     * @param productId Product identifier
     * @return Optional containing product if found
     * @throws SQLException If database error occurs
     */
    public Optional<Product> getProductById(int productId) throws SQLException {
        String query = "SELECT * FROM products WHERE id = ?";
        
        try (PreparedStatement stmt = connection.prepareStatement(query)) {
            stmt.setInt(1, productId);
            
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    Product product = mapResultSetToProduct(rs);
                    return Optional.of(product);
                }
            }
        }
        
        return Optional.empty();
    }

    /**
     * Search products by category
     * 
     * @param category Product category name
     * @param limit Maximum number of results
     * @return List of matching products
     * @throws SQLException If database error occurs
     */
    public List<Product> searchByCategory(String category, int limit) throws SQLException {
        List<Product> products = new ArrayList<>();
        String query = "SELECT * FROM products WHERE category = ? LIMIT ?";
        
        try (PreparedStatement stmt = connection.prepareStatement(query)) {
            stmt.setString(1, category);
            stmt.setInt(2, limit);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    products.add(mapResultSetToProduct(rs));
                }
            }
        }
        
        logger.info(String.format("Found %d products in category: %s", products.size(), category));
        return products;
    }

    /**
     * Update product inventory
     * 
     * @param productId Product identifier
     * @param quantityChange Change in stock quantity (positive or negative)
     * @return True if update successful
     * @throws SQLException If database error occurs
     */
    public boolean updateInventory(int productId, int quantityChange) throws SQLException {
        String query = "UPDATE products SET stock = stock + ? WHERE id = ?";
        
        try (PreparedStatement stmt = connection.prepareStatement(query)) {
            stmt.setInt(1, quantityChange);
            stmt.setInt(2, productId);
            
            int rowsAffected = stmt.executeUpdate();
            
            if (rowsAffected > 0) {
                logger.info(String.format("Updated inventory for product %d: %+d", productId, quantityChange));
                return true;
            }
        }
        
        return false;
    }

    /**
     * Create new product
     * 
     * @param name Product name
     * @param description Product description
     * @param price Product price
     * @param stock Initial stock quantity
     * @param category Product category
     * @return Generated product ID
     * @throws SQLException If database error occurs
     */
    public int createProduct(String name, String description, double price, int stock, String category) 
            throws SQLException {
        String query = "INSERT INTO products (name, description, price, stock, category) VALUES (?, ?, ?, ?, ?)";
        
        try (PreparedStatement stmt = connection.prepareStatement(query, Statement.RETURN_GENERATED_KEYS)) {
            stmt.setString(1, name);
            stmt.setString(2, description);
            stmt.setDouble(3, price);
            stmt.setInt(4, stock);
            stmt.setString(5, category);
            
            stmt.executeUpdate();
            
            try (ResultSet generatedKeys = stmt.getGeneratedKeys()) {
                if (generatedKeys.next()) {
                    int productId = generatedKeys.getInt(1);
                    logger.info(String.format("Created product: %s (ID: %d)", name, productId));
                    return productId;
                }
            }
        }
        
        throw new SQLException("Failed to create product, no ID obtained");
    }

    /**
     * Delete product from database
     * 
     * @param productId Product identifier
     * @return True if deleted successfully
     * @throws SQLException If database error occurs
     */
    public boolean deleteProduct(int productId) throws SQLException {
        String query = "DELETE FROM products WHERE id = ?";
        
        try (PreparedStatement stmt = connection.prepareStatement(query)) {
            stmt.setInt(1, productId);
            int rowsAffected = stmt.executeUpdate();
            
            if (rowsAffected > 0) {
                logger.info(String.format("Deleted product: %d", productId));
                return true;
            }
        }
        
        return false;
    }

    /**
     * Map database result set to Product object
     * 
     * @param rs Result set from query
     * @return Product instance
     * @throws SQLException If column access fails
     */
    private Product mapResultSetToProduct(ResultSet rs) throws SQLException {
        return new Product(
            rs.getInt("id"),
            rs.getString("name"),
            rs.getString("description"),
            rs.getDouble("price"),
            rs.getInt("stock"),
            rs.getString("category")
        );
    }
}

/**
 * Product entity class
 */
class Product {
    private final int id;
    private final String name;
    private final String description;
    private final double price;
    private final int stock;
    private final String category;

    public Product(int id, String name, String description, double price, int stock, String category) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.price = price;
        this.stock = stock;
        this.category = category;
    }

    // Getters
    public int getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public double getPrice() { return price; }
    public int getStock() { return stock; }
    public String getCategory() { return category; }
}
