"""
Test Sphinx Compliance Metrics
===============================

Demonstrates the gate-based validation system.
"""

from sphinx_compliance_metrics import DocumentationEvaluator

def test_good_sphinx_documentation():
    """Test case: Perfect Sphinx/reST documentation"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    good_doc = '''
"""
Advances the game state by one frame.

:param delta_time: Time elapsed since the previous frame, in seconds
:type delta_time: float
:param force_update: Whether to force state update regardless of timing
:type force_update: bool
:return: None
:rtype: None
"""
'''
    
    # Gold standard reference for BLEU
    reference = '''
"""
Updates the game state for one frame.

:param delta_time: Time since last frame in seconds
:type delta_time: float
:param force_update: Forces update when true
:type force_update: bool
:return: None
:rtype: None
"""
'''
    
    observed_info = {
        'parameters': ['delta_time', 'force_update'],
        'has_return': True,  # Even if returns None
        'attributes': []
    }
    
    report = evaluator.evaluate(good_doc, observed_info, 'update', reference_doc=reference)
    
    print("="*60)
    print("TEST 1: GOOD SPHINX DOCUMENTATION (WITH BLEU)")
    print("="*60)
    print(report)
    print(f"\n✅ RESULT: {'ACCEPTED' if report.accepted else 'REJECTED'}")
    
    assert report.accepted, "Good documentation should pass compliance"
    assert report.quality.evidence_coverage == 1.0, "Should have 100% coverage"
    assert report.quality.non_tautology >= 0.9, "Should be non-tautological"
    assert report.quality.bleu_score is not None, "Should have BLEU score"
    assert report.quality.bleu_score > 0.4, "Should have reasonable BLEU score (paraphrase)"
    
    return report


def test_bad_documentation_quality_judgments():
    """Test case: Documentation with forbidden quality judgments"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    bad_doc = '''
"""
This function is used to update the game state efficiently.
Well-designed method that handles frame updates robustly.

Example:
    >>> update(0.016)
    
Args:
    delta_time: Time in seconds
"""
'''
    
    observed_info = {
        'parameters': ['delta_time'],
        'has_return': False,
        'attributes': []
    }
    
    report = evaluator.evaluate(bad_doc, observed_info, 'update')
    
    print("\n" + "="*60)
    print("TEST 2: BAD DOCUMENTATION (Quality Judgments)")
    print("="*60)
    print(report)
    print(f"\n❌ RESULT: {'ACCEPTED' if report.accepted else 'REJECTED'}")
    
    assert not report.accepted, "Bad documentation should fail compliance"
    assert len(report.details['language_violations']) > 0, "Should detect forbidden language"
    
    return report


def test_tautological_documentation():
    """Test case: Tautological documentation (restates function name)"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    tautology_doc = '''
"""
Draw the cube. This function draws a cube.

:param cube: The cube to draw
:type cube: Cube
:return: None
:rtype: None
"""
'''
    
    observed_info = {
        'parameters': ['cube'],
        'has_return': True,
        'attributes': []
    }
    
    report = evaluator.evaluate(tautology_doc, observed_info, 'draw_cube')
    
    print("\n" + "="*60)
    print("TEST 3: TAUTOLOGICAL DOCUMENTATION")
    print("="*60)
    print(report)
    print(f"\n⚠️ RESULT: {'ACCEPTED' if report.accepted else 'REJECTED'}")
    
    # Tautology passes compliance (format is correct) but scores LOW on quality
    assert report.accepted, "Tautology should pass compliance gates"
    assert report.quality.non_tautology <= 0.5, "Should detect tautology (50% tautological)"
    assert report.quality.overall_quality < 0.9, "Overall quality should be penalized"
    
    return report


def test_incomplete_documentation():
    """Test case: Missing parameters (low evidence coverage)"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    incomplete_doc = '''
"""
Processes user authentication.

:param username: User identifier
:type username: str
:return: Authentication result
:rtype: bool
"""
'''
    
    observed_info = {
        'parameters': ['username', 'password', 'remember_me'],  # 3 params
        'has_return': True,
        'attributes': []
    }
    
    report = evaluator.evaluate(incomplete_doc, observed_info, 'authenticate_user')
    
    print("\n" + "="*60)
    print("TEST 4: INCOMPLETE DOCUMENTATION (Missing Params)")
    print("="*60)
    print(report)
    print(f"\n⚠️ RESULT: {'ACCEPTED' if report.accepted else 'REJECTED'}")
    
    # Passes compliance but low evidence coverage
    assert report.accepted, "Format is correct, should pass compliance"
    assert report.quality.evidence_coverage == 0.5, "Should have 50% coverage (2/4: username + return)"
    assert report.quality.overall_quality < 0.75, "Overall quality should be penalized for missing params"
    
    return report


def test_speculation_documentation():
    """Test case: Speculative language (epistemic violation)"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    speculation_doc = '''
"""
Probably validates the input data.

:param data: Data to validate (likely a dict)
:type data: dict
:return: Might return True if valid
:rtype: bool
"""
'''
    
    observed_info = {
        'parameters': ['data'],
        'has_return': True,
        'attributes': []
    }
    
    report = evaluator.evaluate(speculation_doc, observed_info, 'validate_data')
    
    print("\n" + "="*60)
    print("TEST 5: SPECULATIVE DOCUMENTATION (Epistemic Violation)")
    print("="*60)
    print(report)
    print(f"\n❌ RESULT: {'ACCEPTED' if report.accepted else 'REJECTED'}")
    
    assert not report.accepted, "Speculation should fail epistemic discipline gate"
    assert len(report.details['epistemic_violations']) > 0, "Should detect speculation"
    
    return report


def test_markdown_formatting():
    """Test case: Markdown formatting (format violation)"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    markdown_doc = '''
## Update Function

**Description:** Updates the game state

### Parameters
- delta_time: Time elapsed
- force: Force update flag

### Returns
Nothing
'''
    
    observed_info = {
        'parameters': ['delta_time', 'force'],
        'has_return': False,
        'attributes': []
    }
    
    report = evaluator.evaluate(markdown_doc, observed_info, 'update')
    
    print("\n" + "="*60)
    print("TEST 6: MARKDOWN FORMATTING (Format Violation)")
    print("="*60)
    print(report)
    print(f"\n❌ RESULT: {'ACCEPTED' if report.accepted else 'REJECTED'}")
    
    assert not report.accepted, "Markdown should fail format compliance"
    assert len(report.details['sphinx_violations']) > 0, "Should detect Markdown"
    
    return report


def test_batch_evaluation():
    """Test batch evaluation and aggregation"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    # Create test suite
    test_docs = [
        # (doc, observed_info, symbol_name)
        (
            '"""\nValid function.\n\n:param x: Value\n:type x: int\n:return: Result\n:rtype: int\n"""',
            {'parameters': ['x'], 'has_return': True, 'attributes': []},
            'process'
        ),
        (
            '"""\nThis function is used to handle data efficiently.\n"""',  # BAD
            {'parameters': ['data'], 'has_return': False, 'attributes': []},
            'handle_data'
        ),
        (
            '"""\nComputes sum.\n\n:param a: First number\n:type a: int\n:param b: Second number\n:type b: int\n:return: Sum\n:rtype: int\n"""',
            {'parameters': ['a', 'b'], 'has_return': True, 'attributes': []},
            'add'
        ),
    ]
    
    reports = evaluator.batch_evaluate(test_docs)
    aggregate = evaluator.aggregate_results(reports)
    
    print("\n" + "="*60)
    print("TEST 7: BATCH EVALUATION")
    print("="*60)
    print(f"Total: {aggregate['total']}")
    print(f"Passed: {aggregate['passed']}")
    print(f"Failed: {aggregate['failed']}")
    print(f"Pass Rate: {aggregate['pass_rate']:.1%}")
    print(f"\nAverage Quality (for passed): {aggregate['avg_quality']:.2%}")
    print(f"  - Evidence Coverage: {aggregate['quality_breakdown']['evidence_coverage']:.2%}")
    print(f"  - Consistency: {aggregate['quality_breakdown']['consistency']:.2%}")
    print(f"  - Non-Tautology: {aggregate['quality_breakdown']['non_tautology']:.2%}")
    print(f"  - Brevity: {aggregate['quality_breakdown']['brevity_efficiency']:.2%}")
    
    assert aggregate['pass_rate'] == 2/3, "Should have 66.7% pass rate"
    
    return aggregate


def test_bleu_optimization():
    """Test BLEU-optimized documentation generation"""
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    # Gold standard (what we want to match)
    gold_standard = '''
"""
Renders the current frame to the display surface.

:param surface: Target rendering surface
:type surface: pygame.Surface
:param camera: Camera viewport for rendering
:type camera: Camera
:return: Number of objects rendered
:rtype: int
"""
'''
    
    # Test different documentation styles
    test_cases = [
        ("EXACT MATCH", gold_standard),
        ("GOOD PARAPHRASE", '''
"""
Draws the current frame to display surface.

:param surface: Display surface for rendering
:type surface: pygame.Surface
:param camera: Viewport camera for rendering
:type camera: Camera
:return: Count of rendered objects
:rtype: int
"""
'''),
        ("POOR MATCH", '''
"""
Renders graphics to target.

:param surface: A rendering surface
:type surface: pygame.Surface
:param camera: A viewing camera
:type camera: Camera
:return: Some value
:rtype: int
"""
'''),
    ]
    
    observed_info = {
        'parameters': ['surface', 'camera'],
        'has_return': True,
        'attributes': []
    }
    
    print("\n" + "="*60)
    print("TEST 8: BLEU OPTIMIZATION ASSESSMENT")
    print("="*60)
    
    results = []
    for name, candidate in test_cases:
        report = evaluator.evaluate(candidate, observed_info, 'render', reference_doc=gold_standard)
        
        if report.quality:
            print(f"\n{name}:")
            print(f"  BLEU: {report.quality.bleu_score:.2%}" if report.quality.bleu_score else "  BLEU: N/A")
            print(f"  Evidence Coverage: {report.quality.evidence_coverage:.2%}")
            print(f"  Non-Tautology: {report.quality.non_tautology:.2%}")
            print(f"  Overall Quality: {report.quality.overall_quality:.2%}")
            print(f"  Status: {'✅ PASS' if report.accepted else '❌ FAIL'}")
            
            if report.quality.bleu_score:
                details = report.details.get('bleu', {})
                print(f"  BLEU Details:")
                print(f"    - Brevity Penalty: {details.get('brevity_penalty', 0):.3f}")
                print(f"    - 1-gram: {details.get('precisions', [0])[0]:.3f}")
                print(f"    - 2-gram: {details.get('precisions', [0,0])[1]:.3f}")
                print(f"    - 3-gram: {details.get('precisions', [0,0,0])[2]:.3f}")
                print(f"    - 4-gram: {details.get('precisions', [0,0,0,0])[3]:.3f}")
            
            results.append((name, report.quality.bleu_score if report.quality.bleu_score else 0))
    
    # Verify BLEU distinguishes quality
    assert results[0][1] > 0.9, "Exact match should have BLEU > 0.9"
    assert results[1][1] > 0.4, "Good paraphrase should have BLEU > 0.4"
    assert results[0][1] > results[1][1] > results[2][1], "BLEU should decrease: exact > paraphrase > poor"
    
    print(f"\nBLEU correctly ranks: {results[0][0]} ({results[0][1]:.2%}) > {results[1][0]} ({results[1][1]:.2%}) > {results[2][0]} ({results[2][1]:.2%})")
    
    return results


if __name__ == '__main__':
    print("\n" + "SPHINX COMPLIANCE + BLEU METRICS TEST SUITE" + "\n")
    print("Gate-based validation with objective quality scoring + BLEU reference\n")
    
    try:
        test_good_sphinx_documentation()
        test_bad_documentation_quality_judgments()
        test_tautological_documentation()
        test_incomplete_documentation()
        test_speculation_documentation()
        test_markdown_formatting()
        test_batch_evaluation()
        test_bleu_optimization()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nMetrics System Ready for Production Use")
        print("BLEU integration successful - reference-based optimization enabled\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
