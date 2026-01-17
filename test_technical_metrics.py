#!/usr/bin/env python3
"""
Test technical documentation metrics with real examples
"""

from technical_doc_metrics import TechnicalDocumentationEvaluator

# Example 1: Poor quality documentation (from your uploaded file)
poor_doc = """
__init__(self: Self, temp_dir: Optional[str]):
    ...

Initialize Git handler.

Args:
    temp_dir: Directory for temporary clones (None for system temp)

:param self: Parameter for self: Self
:type self: Self: Any
:param temp_dir: Text or string content
:type temp_dir: Optional[str]: Any

**Example:**

```python
__init__(self: Self_value, "example text")
```
"""

# Example 2: Good quality documentation
good_doc = """
.. method:: __init__(temp_dir=None)

   Initialize the Git handler with a temporary directory for cloning repositories.

   :param temp_dir: Directory path where cloned repositories will be stored. If None, uses system temp directory.
   :type temp_dir: str or None
   :raises OSError: If the temp directory cannot be created
"""

# Example 3: Excellent quality documentation  
excellent_doc = """
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
"""

def test_documentation(doc: str, title: str, params: list):
    """Test documentation and print results"""
    print("\n" + "=" * 80)
    print(f"Testing: {title}")
    print("=" * 80)
    
    evaluator = TechnicalDocumentationEvaluator()
    results = evaluator.evaluate_comprehensive(
        doc,
        function_name="__init__",
        actual_params=params
    )
    
    print(evaluator.format_report(results))
    
    # Show key metrics
    print("\n📈 KEY METRICS SUMMARY:")
    print(f"   Overall Quality: {results['overall_technical_quality']:.1%}")
    print(f"   Structure: {results['structure']['score']:.1%}")
    print(f"   Parameters: {results['parameters']['quality_score']:.1%}")
    print(f"   Type Quality: {results['types']['quality_score']:.1%}")
    print(f"   Description: {results['description']['score']:.1%}")
    print(f"   Sphinx Compliance: {results['sphinx_compliance']['score']:.1%}")
    print()


if __name__ == "__main__":
    print("\n🧪 TECHNICAL DOCUMENTATION METRICS TEST SUITE")
    print("=" * 80)
    
    # Test poor documentation
    test_documentation(
        poor_doc,
        "Poor Quality (Original - with issues)",
        params=['self', 'temp_dir']
    )
    
    # Test good documentation
    test_documentation(
        good_doc,
        "Good Quality (Improved format)",
        params=['self', 'temp_dir']
    )
    
    # Test excellent documentation
    test_documentation(
        excellent_doc,
        "Excellent Quality (Best practices)",
        params=['self', 'repo_url', 'branch']
    )
    
    print("\n" + "=" * 80)
    print("✅ Test suite completed!")
    print("=" * 80)
