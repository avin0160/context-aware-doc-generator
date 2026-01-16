# Gemini API Integration - Setup Guide

## Overview

This project now uses **Gemini API** to enhance documentation quality with whole-codebase context awareness, while keeping **Phi-3 Mini** as the backbone for local processing.

### Architecture

```
┌─────────────────────────────────────────────┐
│         Documentation Generation            │
├─────────────────────────────────────────────┤
│                                             │
│  1. Phi-3 Mini (Backbone)                   │
│     - Local processing                      │
│     - Initial documentation generation      │
│     - Fast, private, offline-capable        │
│                                             │
│  2. Gemini API (Context Validator)          │
│     - Whole-codebase understanding          │
│     - Cross-module validation               │
│     - Project-wide insights                 │
│     - Architecture analysis                 │
│                                             │
└─────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Get Your Gemini API Key

1. Visit: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### 2. Configure API Key

Open [`config.py`](config.py) and replace the placeholder:

```python
# Gemini API Configuration
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # 👈 Replace this with your actual key
```

**Example:**
```python
GEMINI_API_KEY = "AIzaSyB_Cx8ZJh3aVz_example_key_here"
```

### 3. Install Dependencies

```bash
pip install google-generativeai
# or
pip install -r requirements.txt
```

### 4. Verify Installation

Run a test to verify Gemini integration:

```bash
python -c "from gemini_context_enhancer import get_gemini_enhancer; e = get_gemini_enhancer(); print('✅ Gemini ready' if e.available else '⚠️ Check API key')"
```

## How It Works

### Step 1: Phi-3 Generates Initial Documentation

```python
# Phi-3 analyzes local code context
docstring = phi3_generator.generate_function_docstring(
    function_code=code,
    function_name="check_collision",
    context={
        'calls': ['range', 'len'],
        'called_by': ['spawn_piece', 'try_rotate'],
        'complexity': 5
    }
)
```

### Step 2: Gemini Enhances with Project Context

```python
# Gemini receives FULL project structure
project_context = """
=== PROJECT OVERVIEW ===
Total Files: 2
Total Functions: 10
Imports: pygame, random, pieces

=== CODE STRUCTURE ===
[FILE: main.py]
Functions:
  - draw_block(x, y, color)
  - check_collision(shape, x, y) [complexity: 5]
    Calls: range, len
  - spawn_piece() -> calls check_collision

=== CALL GRAPH ===
spawn_piece -> check_collision
try_rotate -> check_collision
"""

# Gemini validates and enhances
enhanced_doc = gemini.enhance_documentation(
    phi3_output=docstring,
    function_info={'name': 'check_collision', 'calls': [...]},
    project_context=project_context
)
```

### Step 3: Output Combines Best of Both

**Phi-3 Output (Local):**
```
Checks if a shape collides with the playfield boundaries or other blocks.

Args:
    shape: The shape to check
    x: X position
    y: Y position

Returns:
    bool: True if collision detected
```

**Gemini Enhancement (Global Context):**
```
**Project Context:** Core collision detection system for Pygame Tetris game.
Called by spawn_piece() during piece generation and try_rotate() during
player input handling. This function is critical for game physics validation.

**Cross-Module Dependencies:**
- Reads global `playfield` array (20x10 grid)
- Interacts with piece rotation system (try_rotate)
- Validates spawn positioning (spawn_piece)

**Execution Flow:**
1. Validates boundaries (0-9 horizontal, 0-19 vertical)
2. Checks playfield collision using nested iteration
3. Returns boolean for game state validation
```

## Features

### 1. Whole-Codebase Understanding
- Gemini sees the entire project structure
- Validates relationships between modules
- Identifies execution patterns (game loops, APIs, CLI tools)

### 2. Evidence-Based Validation
- Corrects inaccurate classifications
- No hallucination - only verifiable facts
- Honest about limitations

### 3. Academic Rigor
- Project-wide architecture analysis
- Cross-module dependency mapping
- Design pattern identification

## Cost & Performance

### Gemini API Usage
- **Free Tier**: 60 requests/minute
- **Cost**: Generally free for development
- **Latency**: ~1-2 seconds per function

### Fallback Behavior
If Gemini is unavailable (API key missing, quota exceeded, network error):
- System falls back to **Phi-3 only** mode
- All documentation still generates successfully
- No errors or crashes

## Configuration Options

Edit [`config.py`](config.py):

```python
# Gemini Model Selection
GEMINI_MODEL = "gemini-1.5-pro-latest"  # or "gemini-1.5-flash" for faster/cheaper

# Generation Parameters
GEMINI_TEMPERATURE = 0.3  # Lower = more deterministic (0.0 - 1.0)
GEMINI_MAX_TOKENS = 2048  # Maximum response length
```

## Troubleshooting

### Error: "Gemini API key not configured"
**Solution:** Set `GEMINI_API_KEY` in [`config.py`](config.py)

### Error: "Gemini initialization failed"
**Possible causes:**
1. Invalid API key → Check for typos
2. No internet connection → Verify network
3. Quota exceeded → Wait or upgrade plan

### Documentation still generates without Gemini
**This is expected behavior!** Phi-3 continues working as the backbone. Gemini only enhances quality when available.

## Privacy & Security

### What Data is Sent to Gemini?
- Project structure (file names, function names, import statements)
- Function signatures and call graphs
- **NO** actual implementation code (unless explicitly configured)

### What Stays Local?
- Full source code (processed by Phi-3)
- User credentials
- File system paths
- Git repository data

### Best Practices
1. Don't commit API keys to Git (add `config.py` to `.gitignore`)
2. Use environment variables for production:
   ```python
   import os
   GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'default_value')
   ```
3. Rotate API keys periodically

## Advanced: Custom Prompts

Edit [`gemini_context_enhancer.py`](gemini_context_enhancer.py) to customize prompts:

```python
def _build_enhancement_prompt(self, phi3_output, function_info, project_context):
    prompt = f"""
    YOUR CUSTOM INSTRUCTIONS HERE
    
    Project: {project_context}
    Function: {function_info['name']}
    
    Enhance this documentation with [your specific requirements]
    """
    return prompt
```

## Example: Before and After

### Without Gemini (Phi-3 Only)
```
draw_block function.

Calls: rect, rect.
```

### With Gemini Enhancement
```
**draw_block(x, y, color)**

Renders a single Tetris block at grid coordinates (x, y) with the specified color.

**Project Context:** Part of the Pygame Tetris game's rendering system. Called by
draw_playfield() for static blocks and draw_current_piece() for active piece.

**Execution Model:** Invoked during render phase of game loop (~60 FPS). Transforms
grid coordinates to pixel coordinates using BLOCK_SIZE constant.

**Cross-Module Dependencies:**
- Uses global `screen` surface (pygame display)
- Coordinates with draw_playfield() and draw_current_piece()

**Implementation Details:**
1. Converts grid position (x, y) to pixels: (x * BLOCK_SIZE, y * BLOCK_SIZE)
2. Draws filled rectangle using pygame.draw.rect()
3. Adds border rect for visual separation
```

## Support

- **Gemini API Docs**: https://ai.google.dev/docs
- **API Key Issues**: https://makersuite.google.com/app/apikey
- **Pricing**: https://ai.google.dev/pricing

---

**Status:** ✅ Gemini integration complete. Remember to add your API key to [`config.py`](config.py)!
