# Models and Evaluation Metrics Guide

## Current Model Status

### [NOT ACTIVE] Models NOT Currently Downloaded
The system is designed to use AI models, but they are **NOT currently being used** because:

1. **Transformers/PEFT dependencies are optional** - System runs without them
2. **Models download on first AI generation attempt** - Haven't been triggered yet
3. **System falls back to rule-based analysis** - Currently using pattern matching

### Models That Should Download (When Enabled)

#### 1. **Language Model**: Microsoft Phi-3-mini-4k-instruct
- **Size**: ~7 GB
- **Purpose**: Generate natural language documentation
- **Location**: Will download to `models/` or HuggingFace cache
- **Config**: `config.py` → `DEFAULT_MODEL = "microsoft/Phi-3-mini-4k-instruct"`

#### 2. **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Size**: ~90 MB
- **Purpose**: Semantic code understanding for RAG
- **Location**: HuggingFace cache
- **Config**: `config.py` → `EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"`

### Why Models Aren't Being Used

Check `repo_fastapi_server.py` output at startup. You'll see:
```
Advanced features (transformers, datasets) not available
```

This means the system is using:
- [ACTIVE] **Tree-sitter** for code parsing
- [ACTIVE] **Rule-based analysis** for documentation generation
- [ACTIVE] **Intelligent analyzer** for context-aware descriptions
- [NOT ACTIVE] **NOT using LLM** for text generation
- [NOT ACTIVE] **NOT using embeddings** for RAG

### How to Enable Model Downloads

1. **Make sure dependencies are installed**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install transformers>=4.35.0 torch>=2.0.0 peft>=0.6.0 datasets>=2.15.0
   ```

2. **Models will auto-download on first use** when you:
   - Generate documentation with AI features enabled
   - First run can take 10-30 minutes depending on internet speed

3. **Check if models are working**:
   ```python
   python -c "import transformers, torch; print('[SUCCESS] Models will download')"
   ```

## Evaluation Metrics - ALREADY IMPLEMENTED!

### Available Metrics in `evaluation_metrics.py`:

#### 1. **BLEU Score** [IMPLEMENTED]
- **What**: Measures similarity between generated and reference docs
- **Range**: 0.0 to 1.0 (higher is better)
- **Implementation**: 
  ```python
  from evaluation_metrics import BLEUScore
  
  score = BLEUScore.calculate(reference_doc, generated_doc)
  print(f"BLEU Score: {score:.4f}")
  ```

#### 2. **ROUGE Scores** [IMPLEMENTED]
- **ROUGE-1**: Unigram overlap
- **ROUGE-2**: Bigram overlap
- **ROUGE-L**: Longest common subsequence
- **Implementation**:
  ```python
  from evaluation_metrics import ROUGEScore
  
  scores = ROUGEScore.calculate(reference_doc, generated_doc)
  print(f"ROUGE-1: {scores['rouge-1']:.4f}")
  print(f"ROUGE-2: {scores['rouge-2']:.4f}")
  print(f"ROUGE-L: {scores['rouge-l']:.4f}")
  ```

#### 3. **Readability Metrics** [IMPLEMENTED]
- **Flesch Reading Ease**: 0-100 (higher = easier to read)
- **Flesch-Kincaid Grade**: US grade level
- **Implementation**:
  ```python
  from evaluation_metrics import ReadabilityMetrics
  
  metrics = ReadabilityMetrics.calculate(generated_doc)
  print(f"Reading Ease: {metrics['flesch_reading_ease']:.2f}")
  print(f"Grade Level: {metrics['flesch_kincaid_grade']:.2f}")
  ```

#### 4. **Documentation Quality Metrics** [IMPLEMENTED]
- Completeness score
- Coverage metrics
- Consistency checks
- **Implementation**:
  ```python
  from evaluation_metrics import DocumentationQualityMetrics
  
  quality = DocumentationQualityMetrics.evaluate(generated_doc, code_analysis)
  print(f"Completeness: {quality['completeness']:.2f}")
  print(f"Coverage: {quality['coverage']:.2f}")
  ```

## How to Add Evaluation Metrics to Your Output

### Option 1: Add to Existing Generation

Update `repo_fastapi_server.py` to include metrics in response:

```python
from evaluation_metrics import BLEUScore, ROUGEScore, ReadabilityMetrics

# After generating documentation
result = doc_generator.generate_documentation(...)

# Calculate metrics (if reference available)
if reference_doc:
    bleu = BLEUScore.calculate(reference_doc, result)
    rouge = ROUGEScore.calculate(reference_doc, result)
else:
    bleu = None
    rouge = None

# Always calculate readability
readability = ReadabilityMetrics.calculate(result)

return {
    "documentation": result,
    "metrics": {
        "bleu": bleu,
        "rouge": rouge,
        "readability": readability
    }
}
```

### Option 2: Create Evaluation Endpoint

Add new endpoint in `repo_fastapi_server.py`:

```python
@app.post("/evaluate")
async def evaluate_documentation(
    reference: str = Form(...),
    generated: str = Form(...)
):
    """Evaluate documentation quality"""
    from evaluation_metrics import BLEUScore, ROUGEScore, ReadabilityMetrics
    
    metrics = {
        "bleu": BLEUScore.calculate(reference, generated),
        "rouge": ROUGEScore.calculate(reference, generated),
        "readability": ReadabilityMetrics.calculate(generated)
    }
    
    return JSONResponse(metrics)
```

## Quick Test Script

Create `test_metrics.py`:

```python
from evaluation_metrics import BLEUScore, ROUGEScore, ReadabilityMetrics

# Sample documentation
reference = \"\"\"
This function calculates the factorial of a number.
It uses recursion to compute the result.
\"\"\"

generated = \"\"\"
Calculates factorial using recursive algorithm.
Returns the factorial result for the given number.
\"\"\"

# Calculate metrics
print("=" * 50)
print("DOCUMENTATION QUALITY METRICS")
print("=" * 50)

bleu = BLEUScore.calculate(reference, generated)
print(f"\\nBLEU Score: {bleu:.4f}")
print("  (0.0 = poor, 1.0 = perfect match)")

rouge = ROUGEScore.calculate(reference, generated)
print(f"\\nROUGE Scores:")
print(f"  ROUGE-1: {rouge['rouge-1']:.4f}")
print(f"  ROUGE-2: {rouge['rouge-2']:.4f}")
print(f"  ROUGE-L: {rouge['rouge-l']:.4f}")

readability = ReadabilityMetrics.calculate(generated)
print(f"\\nReadability:")
print(f"  Flesch Reading Ease: {readability['flesch_reading_ease']:.2f}")
print(f"  Grade Level: {readability['flesch_kincaid_grade']:.2f}")
```

Run it:
```powershell
.\venv\Scripts\Activate.ps1
python test_metrics.py
```

## Summary

### Current Status:
- [NOT ACTIVE] **AI Models**: NOT downloaded (system using rule-based)
- [IMPLEMENTED] **Evaluation Metrics**: FULLY IMPLEMENTED (BLEU, ROUGE, Readability)
- [IMPLEMENTED] **Intelligent Analyzer**: Working (context-aware descriptions)
- [IMPLEMENTED] **Tree-sitter Parser**: Working (multi-language support)

### To Enable AI Models:
1. Install: `pip install transformers torch peft datasets`
2. First generation will download ~7GB
3. Subsequent runs will be faster

### To Use Evaluation Metrics:
1. Already in `evaluation_metrics.py` [IMPLEMENTED]
2. Import and use in your code
3. Can be added to API responses
4. Can create separate evaluation endpoint

### Recommendation for College Project:
**You don't necessarily need the large models!** The current system with:
- Intelligent analyzer
- Pattern-based generation  
- BLEU/ROUGE metrics
- Tree-sitter parsing

Is already quite sophisticated and will work faster. The AI models would improve naturalness but aren't essential.

Show the metrics alongside your generated documentation to demonstrate quality evaluation!
