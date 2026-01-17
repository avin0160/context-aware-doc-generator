# Technical Documentation Evaluation Metrics

## Overview

Comprehensive evaluation system for measuring technical documentation quality beyond just Sphinx compliance. Focuses on practical usability and professional standards.

## Metric Categories

### 1. 📐 Structure & Organization (15% weight)

**What it measures:**
- Presence of essential sections (overview, parameters, returns)
- Proper Sphinx directives (`:param:`, `:type:`, `:return:`, `:raises:`)
- Logical organization and hierarchy

**Scoring:**
- Essential sections (parameters, returns): 70%
- Optional sections (examples, exceptions, notes): 30%

**Example:**
```rst
Good structure (77.5%):
- Has overview ✓
- Has parameters with :param and :type ✓
- Has return documentation ✓
- Has :raises for exceptions ✓
```

---

### 2. 📝 Parameter Documentation (25% weight)

**What it measures:**
- **Coverage**: What % of actual parameters are documented
- **Type coverage**: What % have type annotations
- **Description quality**: Non-tautological, meaningful descriptions

**Scoring formula:**
```python
quality_score = (coverage * 0.4) + (type_coverage * 0.3) + (description_quality * 0.3)
```

**Good vs Bad:**

❌ **Bad (70% quality):**
```rst
:param self: Parameter for self: Self
:type self: Any
```

✅ **Good (100% quality):**
```rst
:param temp_dir: Directory path where cloned repositories will be stored
:type temp_dir: str or None
```

**Key indicators:**
- Description > 10 characters
- Doesn't just repeat parameter name
- Contains contextual words (for, to, that, whether, when)

---

### 3. 🏷️ Type Quality (15% weight)

**What it measures:**
- Specificity of type annotations
- Avoidance of generic types like `Any`, `object`
- Use of precise types (`int`, `str`, `List[str]`, `Dict[str, Any]`)

**Type specificity scoring:**
- Generic types (`Any`, `object`): 0% score
- Basic types (`str`, `int`, `bool`): 50% score
- Detailed types (`List[str]`, `Dict[str, Any]`): 80% score
- Module-qualified types (`pathlib.Path`): 100% score

**Example:**

| Type Annotation | Specificity Score |
|----------------|------------------|
| `Any` | 0% |
| `str` | 50% |
| `Optional[str]` | 80% |
| `List[Dict[str, Any]]` | 100% |
| `pathlib.Path` | 100% |

---

### 4. 📖 Description Quality (15% weight)

**What it measures:**
- **Tautological check**: Not just restating the function name
- **Meaningfulness**: Contains actual technical information
- **Word overlap**: Function name vs description overlap

**Tautological detection:**
```python
# Tautological (50% score):
def clone_repository(url):
    """Clone repository"""

# Good (100% score):
def clone_repository(url):
    """Downloads a remote Git repository to local storage using git clone"""
```

**Meaningful content indicators:**
- Length > 30 characters
- More words than function name
- Contains technical detail words (by, using, through, when, if)
- Doesn't start with function name

---

### 5. 🔬 Technical Accuracy (15% weight)

**What it measures:**
- **Technical term density**: Presence of domain-specific terminology
- **Vagueness**: Absence of vague words (thing, stuff, something)
- **Concreteness**: Use of specific values, literals, operators

**Technical terminology list:**
- Actions: algorithm, process, compute, calculate, generate, parse, validate
- Objects: function, method, class, instance, parameter, argument
- Operations: initialize, execute, invoke, handle, raise, catch

**Concreteness indicators:**
- Contains numbers or measurements
- Contains literals (true, false, None)
- Contains operators (<, >, =, !=)
- Contains type parameters (List[int])

**Scoring:**
```python
accuracy_score = (
    term_density * 0.4 +        # Good: 5% density (1 term per 20 words)
    (1 - vague_ratio) * 0.3 +   # Avoid vague words
    concreteness * 0.3           # Use specific examples
)
```

---

### 6. ✨ Sphinx Compliance (15% weight)

**What it measures:**
- Proper Sphinx/reST format
- No forbidden patterns
- Consistent directive usage

**Issues (−20% each):**
- ❌ Contains `**Example:**` pattern
- ❌ Contains Markdown headers (`##`, `###`)
- ❌ Contains Markdown code blocks (` ``` `)
- ❌ Has `:type` without `:param`

**Warnings (−10% each):**
- ⚠️ Has `:param` but no `:type`
- ⚠️ Mismatched `:param` and `:type` counts
- ⚠️ Has `:return` but no `:rtype`

---

## Overall Scoring

### Formula
```python
overall_score = (
    structure * 0.15 +
    parameters * 0.25 +
    types * 0.15 +
    description * 0.15 +
    technical_accuracy * 0.15 +
    sphinx_compliance * 0.15
)
```

### Quality Levels

| Score | Level | Description |
|-------|-------|-------------|
| 80-100% | Excellent | Professional, publication-ready documentation |
| 60-79% | Good | Solid documentation with minor improvements needed |
| 40-59% | Fair | Basic documentation, needs significant work |
| 0-39% | Poor | Inadequate documentation, major issues |

---

## Usage

### Quick Evaluation

```python
from technical_doc_metrics import evaluate_technical_docs

doc = """
.. method:: process_data(input_file, validate=True)

   Process input data from file with optional validation.

   :param input_file: Path to input data file
   :type input_file: str
   :param validate: Enable input validation, defaults to True
   :type validate: bool
   :return: Processed data structure
   :rtype: dict
"""

report = evaluate_technical_docs(
    doc,
    function_name="process_data",
    parameters=['self', 'input_file', 'validate']
)

print(report)
```

### Comprehensive Evaluation

```python
from technical_doc_metrics import TechnicalDocumentationEvaluator

evaluator = TechnicalDocumentationEvaluator()
results = evaluator.evaluate_comprehensive(
    doc=documentation_string,
    function_name="my_function",
    actual_params=['self', 'arg1', 'arg2']
)

# Access individual metrics
print(f"Overall: {results['overall_technical_quality']:.1%}")
print(f"Parameters: {results['parameters']['quality_score']:.1%}")
print(f"Sphinx: {results['sphinx_compliance']['score']:.1%}")

# Get formatted report
report = evaluator.format_report(results)
print(report)
```

---

## Real-World Examples

### Example 1: Poor Quality (68.1%)

**Issues:**
- Contains forbidden `**Example:**` pattern
- Uses Markdown code blocks instead of reST
- Generic descriptions
- Tautological text

```rst
__init__(self: Self, temp_dir: Optional[str]):
    ...

Initialize Git handler.

:param self: Parameter for self: Self
:type self: Self: Any
:param temp_dir: Text or string content
:type temp_dir: Optional[str]: Any

**Example:**

```python
__init__(self: Self_value, "example text")
```
```

**Metrics:**
- Structure: 42.5%
- Parameters: 91.0%
- Type Quality: 65.0%
- Description: 50.0%
- Sphinx Compliance: 60.0%

---

### Example 2: Good Quality (81.6%)

**Improvements:**
- Pure Sphinx format (no Markdown)
- Meaningful descriptions
- Proper directive syntax
- No forbidden patterns

```rst
.. method:: __init__(temp_dir=None)

   Initialize the Git handler with a temporary directory for cloning repositories.

   :param temp_dir: Directory path where cloned repositories will be stored. If None, uses system temp directory.
   :type temp_dir: str or None
   :raises OSError: If the temp directory cannot be created
```

**Metrics:**
- Structure: 42.5%
- Parameters: 100.0%
- Type Quality: 50.0%
- Description: 100.0%
- Sphinx Compliance: 100.0%

---

### Example 3: Excellent Quality (85.8%)

**Best practices:**
- Detailed technical description
- Complete parameter documentation
- Exception documentation
- Concrete implementation details

```rst
.. method:: clone_repository(repo_url, branch='main')

   Clone a remote Git repository to the configured temporary directory.
   
   Downloads the specified branch of a repository using git clone with depth=1
   for efficiency. The cloned repository is stored in a timestamped subdirectory
   to avoid conflicts.

   :param repo_url: Full URL to the Git repository (HTTPS or SSH format)
   :type repo_url: str
   :param branch: Branch name to clone, defaults to 'main'
   :type branch: str
   :return: Absolute path to the cloned repository directory
   :rtype: pathlib.Path
   :raises GitCommandError: If git clone command fails
   :raises ValueError: If repo_url format is invalid
```

**Metrics:**
- Structure: 77.5%
- Parameters: 95.5%
- Type Quality: 50.0%
- Description: 100.0%
- Sphinx Compliance: 100.0%

---

## Integration

### With Inline Injection

```python
from inject_docs import inject_docs_into_file
from technical_doc_metrics import TechnicalDocumentationEvaluator

# Generate documentation
inject_docs_into_file('input.py', 'output.py', style='sphinx')

# Evaluate quality
evaluator = TechnicalDocumentationEvaluator()
with open('output.py') as f:
    # Extract and evaluate each docstring
    # (implement docstring extraction logic)
    pass
```

### With Web Generation

```python
# In comprehensive_docs_advanced.py

from technical_doc_metrics import TechnicalDocumentationEvaluator

def generate_documentation_with_metrics(self, ...):
    # Generate docs
    doc = self._generate_sphinx_style(analysis, context, repo_name)
    
    # Evaluate quality
    evaluator = TechnicalDocumentationEvaluator()
    
    for func in functions:
        results = evaluator.evaluate_comprehensive(
            doc=func.docstring,
            function_name=func.name,
            actual_params=func.args
        )
        
        # Log or display metrics
        print(f"{func.name}: {results['overall_technical_quality']:.1%}")
```

---

## Comparison: Before vs After

| Metric | Original System | With Improvements | Gain |
|--------|----------------|-------------------|------|
| **Sphinx Compliance** | 60% | 100% | +40% |
| **Type Quality** | 65% | 50%* | N/A |
| **Parameter Quality** | 91% | 100% | +9% |
| **Description Quality** | 50% | 100% | +50% |
| **Overall Score** | 68.1% | 85.8% | +17.7% |

\* Lower score for simpler types is acceptable if they're appropriate (e.g., `str` instead of forcing `pathlib.Path` when not needed)

---

## Key Takeaways

### What Makes Quality Technical Documentation:

1. **✅ Specific over generic**
   - `str` not `Any`
   - `List[Dict[str, Any]]` not `list`

2. **✅ Meaningful over tautological**
   - "Downloads repository using git clone" not "Clone repository"

3. **✅ Complete over minimal**
   - Document all parameters with types
   - Include return types and exceptions

4. **✅ Concrete over vague**
   - Use technical terms, not "thing" or "stuff"
   - Include specific implementation details

5. **✅ Proper format over mixed**
   - Pure Sphinx/reST, not Markdown mixing
   - No forbidden patterns (`**Example:**`)

### Common Issues to Avoid:

1. ❌ Generic types everywhere (`Any`, `object`)
2. ❌ Tautological descriptions ("Parameter for X")
3. ❌ Missing parameter documentation
4. ❌ Markdown headers in Sphinx docs
5. ❌ Example sections (forbidden pattern)
6. ❌ Vague language ("various", "stuff", "somehow")

---

## Files

- `technical_doc_metrics.py` - Main metrics implementation
- `test_technical_metrics.py` - Test suite with examples
- This document - Complete guide

## Testing

```bash
# Run test suite
python test_technical_metrics.py

# Expected output:
# Poor Quality: 68.1%
# Good Quality: 81.6%
# Excellent Quality: 85.8%
```
