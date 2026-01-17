# How to View Documentation Quality Metrics

## Overview

The FastAPI server generates comprehensive quality metrics (BLEU, METEOR, ROUGE-L) for documentation generated when you provide **context** (reference documentation).

## 3 Ways to View Metrics

### 1. 🌐 **Web Browser UI** (Easiest)

**Start the server:**
```bash
python repo_fastapi_server.py
```

**Open in browser:**
```
http://localhost:8000
```

**To see metrics:**
1. Enter your code/repository URL
2. **IMPORTANT:** Enter documentation context in the "Documentation Context" field
   - Example: *"Academic research project focusing on algorithmic efficiency"*
3. Click "Generate Repository Documentation"
4. **Metrics appear in a purple gradient box** showing:
   - 📊 BLEU Score
   - 📊 METEOR Score  
   - 📊 ROUGE-L Score
   - 📊 Overall Quality %

**Visual Layout:**
```
┌─────────────────────────────────────┐
│ 📊 Quality Metrics                  │
├─────────┬─────────┬─────────┬───────┤
│  BLEU   │ METEOR  │ ROUGE-L │Overall│
│  0.7234 │ 0.6891  │ 0.7456  │ 72.5% │
└─────────┴─────────┴─────────┴───────┘
```

---

### 2. 📟 **Terminal/Console Output** (Most Detailed)

When the server generates documentation with context, it prints a comprehensive report to the terminal:

**Terminal Output Example:**
```
======================================================================
                    COMPREHENSIVE EVALUATION REPORT                    
======================================================================

📊 INDIVIDUAL METRICS
----------------------------------------------------------------------
BLEU Score:           0.7234  (Precision-focused n-gram overlap)
METEOR Score:         0.6891  (Accounts for synonyms & stemming)
ROUGE-L (F-measure):  0.7456  (Longest common subsequence)
CodeBLEU:             N/A     (Requires code structure)

📈 AGGREGATE SCORE:   72.5%
   Weighted average: 40% BLEU + 30% METEOR + 30% ROUGE

✅ QUALITY ASSESSMENT: Good
   ✓ Documentation quality is solid
   ✓ Metrics show strong alignment with reference

======================================================================
```

**Where to see it:**
- In the PowerShell/terminal where you ran `python repo_fastapi_server.py`
- Appears immediately after documentation generation
- Scrolls by, so watch the terminal output

---

### 3. 🔌 **API Response** (For Programmatic Access)

**Endpoint:** `POST /generate`

**Request:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -F "repo_url=https://github.com/user/repo.git" \
  -F "context=Academic research focusing on optimization" \
  -F "doc_style=sphinx"
```

**Response JSON:**
```json
{
  "documentation": "...",
  "status": "✅ Generated via full AI system with Phi-3 Mini",
  "method": "context-aware AI with RAG + Phi-3",
  "style": "sphinx",
  "metrics": {
    "bleu": "0.7234",
    "meteor": "0.6891",
    "rouge_l": "0.7456",
    "overall": "72.50%"
  }
}
```

**Python example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    data={
        "repo_url": "https://github.com/user/repo.git",
        "context": "Academic research project",
        "doc_style": "sphinx"
    }
)

result = response.json()
if "metrics" in result:
    print(f"BLEU: {result['metrics']['bleu']}")
    print(f"Overall Quality: {result['metrics']['overall']}")
```

---

## When Do Metrics Appear?

✅ **Metrics ARE calculated when:**
- You provide **context** (reference documentation)
- Documentation is successfully generated
- Server is running with evaluation modules installed

❌ **Metrics NOT calculated when:**
- Context field is empty
- Only code snippet provided without context
- Evaluation module fails to load

---

## Metrics Explanation

| Metric | What It Measures | Range | Good Score |
|--------|-----------------|-------|------------|
| **BLEU** | Word overlap precision | 0.0-1.0 | > 0.6 |
| **METEOR** | Synonym-aware match | 0.0-1.0 | > 0.5 |
| **ROUGE-L** | Longest common sequences | 0.0-1.0 | > 0.6 |
| **Overall** | Weighted average | 0-100% | > 70% |

**Formula:**
```
Overall = 40% × BLEU + 30% × METEOR + 30% × ROUGE-L
```

---

## Testing Metrics

**Quick test with demo endpoint:**
```bash
# Start server
python repo_fastapi_server.py

# Visit in browser
http://localhost:8000/demo

# Or test quality endpoint
http://localhost:8000/quality-check
```

---

## Troubleshooting

**"No metrics shown in browser"**
- ✅ Make sure you filled the "Documentation Context" field
- ✅ Check terminal output for evaluation errors
- ✅ Verify evaluation_metrics.py is present

**"Evaluation failed" in terminal**
- ✅ Check if required packages installed: `rouge-score`, `nltk`
- ✅ Install: `pip install rouge-score nltk`

**"Metrics always 0.0000"**
- ✅ Context too different from generated docs
- ✅ Try more detailed context matching your code

---

## Summary

**Best Method:** 🌐 **Web Browser** - Visual, easy to read, automatic  
**Most Detail:** 📟 **Terminal Output** - Full report with assessments  
**Programmatic:** 🔌 **API Response** - For automation/integration

**Remember:** Metrics only appear when you provide reference context!
