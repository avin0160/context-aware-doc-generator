"""Test file with undocumented code"""


class DataProcessor:
    
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.data = []
    
    def load_config(self, path):
        with open(path, 'r') as f:
            return f.read()
    
    def process_data(self, input_data, filter_enabled=True):
        results = []
        for item in input_data:
            if filter_enabled and self.should_filter(item):
                continue
            processed = self.transform_item(item)
            results.append(processed)
        return results
    
    def should_filter(self, item):
        return item.get('active', False)
    
    def transform_item(self, item):
        return {
            'id': item['id'],
            'value': item['value'] * 2,
            'processed': True
        }


def calculate_metrics(data_points, metric_type='average'):
    if metric_type == 'average':
        return sum(data_points) / len(data_points)
    elif metric_type == 'sum':
        return sum(data_points)
    elif metric_type == 'max':
        return max(data_points)
    return None


def validate_input(user_input, required_fields):
    missing = []
    for field in required_fields:
        if field not in user_input:
            missing.append(field)
    
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    
    return True
