/**
 * Frontend UI Components - JavaScript
 * E-commerce user interface and API integration
 */

/**
 * Product catalog manager
 */
class ProductCatalog {
    constructor(apiBaseUrl) {
        this.apiUrl = apiBaseUrl;
        this.products = [];
        this.cart = [];
    }

    /**
     * Fetch products from backend API
     * @param {string} category - Product category filter
     * @param {number} limit - Maximum number of products
     * @returns {Promise<Array>} List of products
     */
    async fetchProducts(category = 'all', limit = 20) {
        try {
            const response = await fetch(`${this.apiUrl}/products?category=${category}&limit=${limit}`);
            const data = await response.json();
            
            this.products = data.products;
            return this.products;
        } catch (error) {
            console.error('Failed to fetch products:', error);
            return [];
        }
    }

    /**
     * Add product to shopping cart
     * @param {number} productId - Product identifier
     * @param {number} quantity - Number of items to add
     * @returns {boolean} True if added successfully
     */
    addToCart(productId, quantity = 1) {
        const product = this.products.find(p => p.id === productId);
        
        if (!product) {
            console.warn(`Product ${productId} not found`);
            return false;
        }

        if (product.stock < quantity) {
            console.warn(`Insufficient stock for product ${productId}`);
            return false;
        }

        const existingItem = this.cart.find(item => item.productId === productId);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.cart.push({
                productId,
                name: product.name,
                price: product.price,
                quantity
            });
        }

        this._saveCart();
        return true;
    }

    /**
     * Calculate total cart value
     * @param {boolean} includeTax - Whether to include sales tax
     * @returns {number} Total cart value
     */
    calculateCartTotal(includeTax = true) {
        const subtotal = this.cart.reduce((total, item) => {
            return total + (item.price * item.quantity);
        }, 0);

        if (includeTax) {
            const taxRate = 0.08; // 8% tax
            return subtotal * (1 + taxRate);
        }

        return subtotal;
    }

    /**
     * Remove item from cart
     * @param {number} productId - Product identifier
     */
    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.productId !== productId);
        this._saveCart();
    }

    /**
     * Clear entire cart
     */
    clearCart() {
        this.cart = [];
        this._saveCart();
    }

    /**
     * Save cart to local storage
     * @private
     */
    _saveCart() {
        localStorage.setItem('shopping_cart', JSON.stringify(this.cart));
    }

    /**
     * Load cart from local storage
     * @private
     */
    _loadCart() {
        const savedCart = localStorage.getItem('shopping_cart');
        if (savedCart) {
            this.cart = JSON.parse(savedCart);
        }
    }
}

/**
 * Submit order to backend
 * @param {Object} orderData - Order details including items and customer info
 * @returns {Promise<Object>} Order confirmation with order ID
 */
async function submitOrder(orderData) {
    const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
    });

    if (!response.ok) {
        throw new Error(`Order submission failed: ${response.statusText}`);
    }

    return await response.json();
}

/**
 * Track order status
 * @param {string} orderId - Order identifier
 * @returns {Promise<string>} Current order status
 */
async function trackOrder(orderId) {
    const response = await fetch(`/api/orders/${orderId}/status`);
    const data = await response.json();
    return data.status;
}

/**
 * Format price for display
 * @param {number} amount - Price amount
 * @param {string} currency - Currency code (USD, EUR, etc.)
 * @returns {string} Formatted price string
 */
function formatPrice(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ProductCatalog,
        submitOrder,
        trackOrder,
        formatPrice
    };
}
