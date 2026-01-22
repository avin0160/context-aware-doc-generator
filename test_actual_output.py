"""
Test script to see actual documentation output
"""
import sys
import io
# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Simple test - what does the tool REALLY generate?
test_code = '''
def check_collision(shape, x, y):
    """Check collision function."""
    for block in shape:
        bx, by = block
        if bx + x < 0 or bx + x >= 10 or by + y >= 20:
            return True
        if playfield[by + y][bx + x]:
            return True
    return False
'''

print("=" * 80)
print("TESTING ACTUAL DOCUMENTATION OUTPUT")
print("=" * 80)
print()

# Test 1: Try Phi-3 generator
print("Test 1: Phi-3 Documentation Generator")
print("-" * 80)
try:
    from phi3_doc_generator import Phi3DocumentationGenerator
    
    generator = Phi3DocumentationGenerator()
    print("✓ Generator initialized")
    
    result = generator.generate_function_docstring(
        function_code=test_code,
        function_name="check_collision",
        context={"description": "Tetris game collision detection"},
        style="google"
    )
    
    print("\nACTUAL OUTPUT FROM PHI-3:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Try comprehensive docs
print("\nTest 2: Comprehensive Documentation")
print("-" * 80)
try:
    from comprehensive_docs_advanced import DocumentationGenerator
    
    gen = DocumentationGenerator()
    
    # Create a fake FunctionInfo object with the test function
    from comprehensive_docs_advanced import FunctionInfo
    func_info = FunctionInfo(
        name="check_collision",
        file_path="tetris.py",
        line_start=1,
        line_end=10,
        args=["shape", "x", "y"],
        return_type="bool",
        docstring="Check collision function.",
        calls=[],
        called_by=[],
        complexity=3,
        semantic_category="validation",
        dependencies=[]
    )
    
    # Try calling the phi3 generator directly if available
    if gen.phi3_generator:
        result = gen.phi3_generator.generate_function_docstring(
            function_code=test_code,
            function_name="check_collision",
            context={"description": "Tetris game collision detection"},
            style="google"
        )
        
        print("\nACTUAL OUTPUT FROM COMPREHENSIVE:")
        print("=" * 80)
        print(result)
        print("=" * 80)
    else:
        print("✗ Phi-3 generator not available in DocumentationGenerator")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("COMPARISON WITH PRESENTATION EXAMPLE")
print("=" * 80)
print("""
PROMISED IN PRESENTATION:
```python
def check_collision(shape, x, y):
    '''Check if a tetromino shape collides with existing blocks or boundaries.
    
    This function validates piece placement by testing each block of the shape 
    against the playfield boundaries and occupied cells. It's a critical safety 
    check used during piece movement, rotation, and spawning to prevent invalid 
    game states.
    
    The collision detection algorithm:
    1. Iterates through each block in the shape's coordinate list
    2. Transforms block coordinates using the offset (current position)
    3. Checks boundary conditions (left, right, bottom walls)
    4. Tests for overlap with existing occupied cells in the playfield
    
    Args:
        shape (List[Tuple[int, int]]): List of (row, col) coordinates 
            representing the tetromino shape in its local coordinate system
        x (int): Horizontal offset position where shape is being tested
        y (int): Vertical offset position where shape is being tested
    
    Returns:
        bool: True if collision detected (invalid placement), False otherwise
    
    Example:
        >>> # Test if T-piece can be placed at position (5, 10)
        >>> if not check_collision(T_SHAPE, 5, 10):
        ...     place_piece(T_SHAPE, 5, 10)
    
    Note:
        Collision detection runs on every frame during piece movement,
        so performance is critical. Current O(n) complexity where n is
        the number of blocks in the shape (typically 4 for tetrominoes).
    
    See Also:
        place_piece(): Commits piece after collision check passes
        try_rotate(): Uses collision check to validate rotations
    '''
```
""")
