#!/usr/bin/env python3
"""Sample B+ Tree implementation for testing documentation generation"""

class BPlusTreeNode:
    def __init__(self, keys, values, is_leaf=False):
        self.keys = keys
        self.values = values 
        self.is_leaf = is_leaf
        self.children = []
        
    def insert(self, key, value):
        if key in self.keys:
            idx = self.keys.index(key)
            self.values[idx] = value
        else:
            self.keys.append(key)
            self.values.append(value)
            self._balance_node()
        return True
    
    def search(self, key):
        if key in self.keys:
            idx = self.keys.index(key)
            return self.values[idx]
        return None
    
    def _balance_node(self):
        if len(self.keys) > 3:
            self._split_node()
    
    def _split_node(self):
        mid = len(self.keys) // 2
        left_keys = self.keys[:mid]
        right_keys = self.keys[mid:]
        return left_keys, right_keys

def range_query(node, start_key, end_key):
    results = []
    for i, key in enumerate(node.keys):
        if start_key <= key <= end_key:
            results.append((key, node.values[i]))
    return results

def validate_schema(record, schema):
    for field, expected_type in schema.items():
        if field not in record:
            return False
        if not isinstance(record[field], expected_type):
            return False
    return True