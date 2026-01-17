"""Test file with undocumented code"""


class DataProcessor:
    """
    DataProcessor class.
    
    :ivar config: Config
    :vartype config: Any
    :ivar data: Data
    :vartype data: Dict
    """
    
    def __init__(self, config_path):
        """
          init  .
        
        :param config_path: Config path
        :type config_path: Any
        """
        self.config = self.load_config(config_path)
        self.data = []
    
    def load_config(self, path):
        """
        Load config.
        
        :param path: Path
        :type path: str
        :return: Computed result
        :rtype: Any
        """
        with open(path, 'r') as f:
            return f.read()
    
    def process_data(self, input_data, filter_enabled=True):
        """
        Process data.
        
        :param input_data: Input data
        :type input_data: Any
        :param filter_enabled: Filter enabled
        :type filter_enabled: Any
        :return: Computed result
        :rtype: Any
        """
        results = []
        for item in input_data:
            if filter_enabled and self.should_filter(item):
                continue
            processed = self.transform_item(item)
            results.append(processed)
        return results
    
    def should_filter(self, item):
        """
        Should filter.
        
        :param item: Item
        :type item: Any
        :return: Computed result
        :rtype: Any
        """
        return item.get('active', False)
    
    def transform_item(self, item):
        """
        Transform item.
        
        :param item: Item
        :type item: Any
        :return: Computed result
        :rtype: Any
        """
        return {
            'id': item['id'],
            'value': item['value'] * 2,
            'processed': True
        }


def calculate_metrics(data_points, metric_type='average'):
    """
    Calculate metrics.
    
    :param data_points: Data points
    :type data_points: List
    :param metric_type: Metric type
    :type metric_type: Any
    :return: Computed result
    :rtype: Any
    """
    if metric_type == 'average':
        return sum(data_points) / len(data_points)
    elif metric_type == 'sum':
        return sum(data_points)
    elif metric_type == 'max':
        return max(data_points)
    return None


def validate_input(user_input, required_fields):
    """
    Validate input.
    
    :param user_input: User input
    :type user_input: Any
    :param required_fields: Required fields
    :type required_fields: List
    :return: Computed result
    :rtype: Any
    """
    missing = []
    for field in required_fields:
        if field not in user_input:
            missing.append(field)
    
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    
    return True
