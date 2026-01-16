"""
Backend API Server - Python
E-commerce order processing service
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderProcessor:
    """Process and manage customer orders"""
    
    def __init__(self, database_url: str):
        """
        Initialize order processor
        
        Args:
            database_url: Connection string for database
        """
        self.db_url = database_url
        self.orders = {}
    
    def create_order(self, customer_id: int, items: List[Dict], total: float) -> str:
        """
        Create a new order in the system
        
        Args:
            customer_id: Unique customer identifier
            items: List of order items with product_id and quantity
            total: Total order amount
            
        Returns:
            Order ID string
        """
        order_id = f"ORD-{datetime.now().timestamp()}"
        
        order = {
            'order_id': order_id,
            'customer_id': customer_id,
            'items': items,
            'total': total,
            'status': 'pending',
            'created_at': datetime.now()
        }
        
        self.orders[order_id] = order
        logger.info(f"Created order {order_id} for customer {customer_id}")
        
        return order_id
    
    def get_order_status(self, order_id: str) -> Optional[str]:
        """
        Retrieve current order status
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order status or None if not found
        """
        order = self.orders.get(order_id)
        return order['status'] if order else None
    
    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """
        Update order status (pending -> processing -> shipped -> delivered)
        
        Args:
            order_id: Order identifier
            new_status: New status value
            
        Returns:
            True if updated successfully, False otherwise
        """
        if order_id not in self.orders:
            return False
        
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            logger.warning(f"Invalid status: {new_status}")
            return False
        
        self.orders[order_id]['status'] = new_status
        logger.info(f"Updated order {order_id} status to {new_status}")
        return True
    
    def calculate_shipping_cost(self, items: List[Dict], destination: str) -> float:
        """
        Calculate shipping cost based on items and destination
        
        Args:
            items: List of items with weight and dimensions
            destination: Shipping destination code
            
        Returns:
            Calculated shipping cost
        """
        base_cost = 5.99
        total_weight = sum(item.get('weight', 0) for item in items)
        
        # Weight-based pricing
        weight_cost = total_weight * 0.5
        
        # Destination-based pricing
        destination_multiplier = 1.0
        if destination.startswith('INT'):
            destination_multiplier = 2.5
        elif destination.startswith('REMOTE'):
            destination_multiplier = 1.8
        
        return round((base_cost + weight_cost) * destination_multiplier, 2)


def validate_payment(amount: float, payment_method: str, card_number: str) -> bool:
    """
    Validate payment information
    
    Args:
        amount: Payment amount
        payment_method: Type of payment (credit, debit, paypal)
        card_number: Card number or payment account
        
    Returns:
        True if payment is valid, False otherwise
    """
    if amount <= 0:
        return False
    
    if payment_method not in ['credit', 'debit', 'paypal']:
        return False
    
    # Basic card validation (Luhn algorithm would go here)
    if payment_method in ['credit', 'debit']:
        if len(card_number) not in [15, 16]:
            return False
    
    return True


async def send_order_notification(customer_email: str, order_id: str, status: str):
    """
    Send email notification to customer about order status
    
    Args:
        customer_email: Customer's email address
        order_id: Order identifier
        status: Current order status
    """
    message = f"Your order {order_id} is now {status}"
    # Email sending logic would go here
    logger.info(f"Sent notification to {customer_email}: {message}")
