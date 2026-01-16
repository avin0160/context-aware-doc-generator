"""
E-Commerce Product Management System
A comprehensive system for managing products, orders, and inventory.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime


class Product:
    """Represents a product in the e-commerce system"""
    
    def __init__(self, product_id: str, name: str, price: float, stock: int):
        """
        Initialize a new product.
        
        Args:
            product_id: Unique identifier for the product
            name: Product name
            price: Product price in USD
            stock: Available quantity in stock
        """
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.created_at = datetime.now()
    
    def update_stock(self, quantity: int) -> bool:
        """
        Update product stock quantity.
        
        Args:
            quantity: Quantity to add (positive) or remove (negative)
            
        Returns:
            True if update successful, False if insufficient stock
        """
        if self.stock + quantity < 0:
            return False
        self.stock += quantity
        return True
    
    def to_dict(self) -> Dict:
        """Convert product to dictionary representation"""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'created_at': self.created_at.isoformat()
        }


class Order:
    """Represents a customer order"""
    
    def __init__(self, order_id: str, customer_id: str):
        """
        Initialize a new order.
        
        Args:
            order_id: Unique order identifier
            customer_id: Customer placing the order
        """
        self.order_id = order_id
        self.customer_id = customer_id
        self.items: List[Dict] = []
        self.status = 'pending'
        self.total = 0.0
        self.created_at = datetime.now()
    
    def add_item(self, product: Product, quantity: int) -> bool:
        """
        Add a product to the order.
        
        Args:
            product: Product to add
            quantity: Quantity to order
            
        Returns:
            True if item added successfully
        """
        if quantity <= 0 or quantity > product.stock:
            return False
        
        item = {
            'product_id': product.product_id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'subtotal': product.price * quantity
        }
        self.items.append(item)
        self.total += item['subtotal']
        return True
    
    def calculate_total(self) -> float:
        """Calculate order total including tax"""
        tax_rate = 0.08
        subtotal = sum(item['subtotal'] for item in self.items)
        return subtotal * (1 + tax_rate)
    
    def confirm_order(self) -> bool:
        """Confirm and process the order"""
        if not self.items:
            return False
        self.status = 'confirmed'
        return True


class InventoryManager:
    """Manages product inventory and stock levels"""
    
    def __init__(self):
        """Initialize the inventory manager"""
        self.products: Dict[str, Product] = {}
        self.low_stock_threshold = 10
    
    def add_product(self, product: Product) -> bool:
        """
        Add a new product to inventory.
        
        Args:
            product: Product to add
            
        Returns:
            True if added successfully
        """
        if product.product_id in self.products:
            return False
        self.products[product.product_id] = product
        return True
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """
        Retrieve a product by ID.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product if found, None otherwise
        """
        return self.products.get(product_id)
    
    def check_low_stock(self) -> List[Product]:
        """
        Get list of products with low stock.
        
        Returns:
            List of products below threshold
        """
        return [
            product for product in self.products.values()
            if product.stock < self.low_stock_threshold
        ]
    
    def restock_product(self, product_id: str, quantity: int) -> bool:
        """
        Restock a product.
        
        Args:
            product_id: Product to restock
            quantity: Quantity to add
            
        Returns:
            True if restock successful
        """
        product = self.get_product(product_id)
        if not product:
            return False
        return product.update_stock(quantity)
    
    def export_inventory(self, filepath: str) -> bool:
        """
        Export inventory to JSON file.
        
        Args:
            filepath: Path to save inventory data
            
        Returns:
            True if export successful
        """
        try:
            data = {
                pid: product.to_dict()
                for pid, product in self.products.items()
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False


class OrderProcessor:
    """Processes and manages customer orders"""
    
    def __init__(self, inventory: InventoryManager):
        """
        Initialize order processor.
        
        Args:
            inventory: Inventory manager instance
        """
        self.inventory = inventory
        self.orders: Dict[str, Order] = {}
        self.order_counter = 0
    
    def create_order(self, customer_id: str) -> Order:
        """
        Create a new order for a customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            New Order instance
        """
        self.order_counter += 1
        order_id = f"ORD-{self.order_counter:05d}"
        order = Order(order_id, customer_id)
        self.orders[order_id] = order
        return order
    
    def process_order(self, order: Order) -> bool:
        """
        Process an order and update inventory.
        
        Args:
            order: Order to process
            
        Returns:
            True if order processed successfully
        """
        if not order.confirm_order():
            return False
        
        # Update inventory for each item
        for item in order.items:
            product = self.inventory.get_product(item['product_id'])
            if not product or not product.update_stock(-item['quantity']):
                order.status = 'failed'
                return False
        
        order.status = 'completed'
        return True
    
    def get_order_status(self, order_id: str) -> Optional[str]:
        """
        Get status of an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order status or None if not found
        """
        order = self.orders.get(order_id)
        return order.status if order else None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order and restore inventory.
        
        Args:
            order_id: Order to cancel
            
        Returns:
            True if cancellation successful
        """
        order = self.orders.get(order_id)
        if not order or order.status == 'completed':
            return False
        
        # Restore inventory if order was confirmed
        if order.status == 'confirmed':
            for item in order.items:
                product = self.inventory.get_product(item['product_id'])
                if product:
                    product.update_stock(item['quantity'])
        
        order.status = 'cancelled'
        return True


def demo_usage():
    """Demonstrate the e-commerce system"""
    # Initialize system
    inventory = InventoryManager()
    processor = OrderProcessor(inventory)
    
    # Add products
    product1 = Product("P001", "Laptop", 999.99, 50)
    product2 = Product("P002", "Mouse", 29.99, 200)
    product3 = Product("P003", "Keyboard", 79.99, 5)
    
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.add_product(product3)
    
    # Create and process order
    order = processor.create_order("CUST001")
    order.add_item(product1, 2)
    order.add_item(product2, 3)
    
    processor.process_order(order)
    
    # Check low stock
    low_stock = inventory.check_low_stock()
    print(f"Low stock items: {len(low_stock)}")
    
    # Export inventory
    inventory.export_inventory("inventory.json")


if __name__ == "__main__":
    demo_usage()
