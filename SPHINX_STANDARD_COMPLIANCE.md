# Sphinx Standard Compliance

## Official Reference
This system follows the official Sphinx/reST docstring format from:
**https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html**

## Sphinx Docstring Format

### Template
```python
"""[Summary]

:param [ParamName]: [ParamDescription], defaults to [DefaultParamVal]
:type [ParamName]: [ParamType], optional
:raises [ErrorType]: [ErrorDescription]
:return: [ReturnDescription]
:rtype: [ReturnType]
"""
```

### Complete Example (from Official Docs)

```python
class SimpleBleDevice:
    """Represents a BLE device
    
    :param name: The name of the device, defaults to None
    :type name: str, optional
    :param address: The MAC address of the device, defaults to None
    :type address: str, optional
    :ivar name: The name of the device
    :vartype name: str
    :ivar address: The MAC address of the device
    :vartype address: str
    """
    
    def __init__(self, name=None, address=None):
        """Constructor method
        """
        self.name = name
        self.address = address
    
    def getServices(self):
        """Get available services
        
        :return: List of available services
        :rtype: list
        """
        pass
    
    def setNotificationCallback(self, service_uuid, char_uuid, callback):
        """Set notification callback for characteristic
        
        :param service_uuid: Service UUID string
        :type service_uuid: str
        :param char_uuid: Characteristic UUID string
        :type char_uuid: str
        :param callback: Callback function to invoke on notification
        :type callback: function
        :raises BleDeviceError: If device is not connected or characteristic not found
        """
        pass
    
    def connect(self):
        """Connect to device
        
        :return: True if connection successful
        :rtype: bool
        :raises BleDeviceError: If connection fails
        """
        pass
```

## System Compliance

### ✅ Inline Injection Tool (inject_docs.py)

**Implementation:** [inline_doc_injector.py](inline_doc_injector.py#L97-L145)

**Format Generated:**
```python
"""Function purpose.

:param arg_name: Arg name description, defaults to None
:type arg_name: str, optional
:return: Computed result
:rtype: Any
"""
```

**Matches Official Standard:** ✅ YES
- Uses `:param:` and `:type:` fields
- Uses `:return:` and `:rtype:` fields
- Includes `, optional` notation for optional parameters
- Includes `defaults to` clause

### ✅ Web Documentation Generator

**Implementation:** [comprehensive_docs_advanced.py](comprehensive_docs_advanced.py#L1410-L1450)

**Format Generated:**
```python
"""Function documentation.

:param parameter: Parameter description
:type parameter: str
:return: Return value description
:rtype: Any
"""
```

**Matches Official Standard:** ✅ YES
- Uses proper Sphinx/reST directives
- Proper parameter and return documentation
- Follows official format structure

## Key Features of Proper Sphinx Format

### 1. Parameter Documentation
```python
:param service_uuid: Service UUID string
:type service_uuid: str
```

### 2. Optional Parameters
```python
:param name: The name of the device, defaults to None
:type name: str, optional
```

### 3. Return Values
```python
:return: True if connection successful
:rtype: bool
```

### 4. Exception Documentation
```python
:raises BleDeviceError: If connection fails
```

### 5. Class Attributes
```python
:ivar name: The name of the device
:vartype name: str
```

## Usage

### Command Line (Inline Injection)
```bash
# Inject Sphinx docstrings into Python file
python inject_docs.py input.py -o output.py -s sphinx

# With validation
python inject_docs.py input.py -o output.py -s sphinx --no-validate
```

### Web Interface
1. Open http://localhost:8000
2. **Select "Sphinx/reST API"** style (first box on left)
3. Upload code or provide repository URL
4. Optional: Add context for better quality metrics
5. Generate documentation

**Common Mistake:** Selecting "Technical Comprehensive" or "Open Source" styles instead of "Sphinx/reST API"

## Quality Metrics

When context is provided (reference documentation), the system displays:
- **BLEU Score**: N-gram precision
- **METEOR Score**: Semantic similarity
- **ROUGE-L Score**: Longest common subsequence
- **Overall Quality**: Composite percentage

See [METRICS_VIEWING_GUIDE.md](METRICS_VIEWING_GUIDE.md) for details.

## VS Code Integration

The official Sphinx tutorial recommends the Python Docstring Generator extension:

**Extension:** autoDocstring - Python Docstring Generator
**Setting:**
```json
{
  "autoDocstring.docstringFormat": "sphinx"
}
```

This matches our system's output format exactly.

## Validation

The system includes [sphinx_compliance_metrics.py](sphinx_compliance_metrics.py) for validation:

```python
from sphinx_compliance_metrics import validate_sphinx_docstrings

# Validate file
results = validate_sphinx_docstrings('output.py')
print(f"Passed: {results['passed']}/{results['total']}")
```

## References

1. **Official Sphinx Docstring Tutorial**
   https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html

2. **Sphinx Documentation**
   https://www.sphinx-doc.org/

3. **reStructuredText (reST) Primer**
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

4. **Example Project (SimpleBLE)**
   http://simpleble.readthedocs.io/en/latest/simpleble.html

## Comparison: Sphinx vs Other Styles

| Feature | Sphinx/reST | Google | NumPy |
|---------|-------------|--------|-------|
| Param format | `:param name:` | `Args:` section | `Parameters` section |
| Type format | `:type name:` | Inline `name (type):` | `name : type` |
| Return format | `:return:` / `:rtype:` | `Returns:` section | `Returns` section |
| Sphinx compatible | ✅ Native | ⚠️ With extension | ⚠️ With extension |
| VS Code support | ✅ Yes | ✅ Yes | ✅ Yes |
| Best for | API docs, libraries | General use | Scientific computing |

## Why Sphinx/reST?

1. **Native Sphinx support** - No extensions needed
2. **Rich formatting** - Cross-references, links, math equations
3. **Industry standard** - Used by major Python projects (Flask, Django, Requests)
4. **Tooling support** - VS Code, PyCharm, Sphinx-doc
5. **Documentation generation** - Direct HTML/PDF/ePub output via Sphinx

## Next Steps

1. ✅ System already compliant with official standard
2. ✅ Both inline injection and web generation work correctly
3. ⏳ User needs to select **"Sphinx/reST API"** style in web UI
4. ⏳ Optional: Add `:raises:` exception documentation
5. ⏳ Optional: Build full Sphinx project with `sphinx-quickstart`
