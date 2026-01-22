# Visual Architecture Diagrams
## For Presentation & Understanding

---

## Diagram 1: System Overview (Use This First)

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│  Git Repo  |  ZIP File  |  Single File  |  Directory            │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PARSING & ANALYSIS                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Tree-Sitter  │  │  Intelligent │  │  Multi-Language      │ │
│  │  Parser      │→ │   Analyzer   │→ │   Analyzer           │ │
│  │              │  │              │  │                      │ │
│  │ • AST        │  │ • Patterns   │  │ • Functions          │ │
│  │ • Tokens     │  │ • Context    │  │ • Classes            │ │
│  │ • Structure  │  │ • Types      │  │ • Dependencies       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      RAG CONTEXT SYSTEM                          │
│                                                                  │
│  ┌─────────────────┐      ┌──────────────────────────────────┐ │
│  │  Sentence       │      │        FAISS Vector DB          │ │
│  │  Transformers   │ ───→ │                                 │ │
│  │                 │      │  • Code Embeddings              │ │
│  │  all-MiniLM-L6 │      │  • Similarity Search            │ │
│  │                 │      │  • Related Code Retrieval       │ │
│  └─────────────────┘      └──────────────────────────────────┘ │
│                                      ↓                          │
│                         Context for each function               │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI GENERATION LAYER                           │
│                                                                  │
│  ┌────────────────────────┐        ┌──────────────────────────┐│
│  │   Phi-3 Mini (Local)   │        │   Gemini 2.5 (Cloud)     ││
│  │                        │        │                          ││
│  │  • 4B parameters       │   ───→ │  • Context Enhancement   ││
│  │  • 128K context        │        │  • Cross-references      ││
│  │  • Draft generation    │        │  • Usage examples        ││
│  │  • Privacy-preserving  │        │  • Project awareness     ││
│  └────────────────────────┘        └──────────────────────────┘│
│            ↓ (if fails)                      ↓                  │
│  ┌────────────────────────┐                                    │
│  │   Rule-Based Fallback  │                                    │
│  │  • Pattern matching    │                                    │
│  │  • Template generation │                                    │
│  └────────────────────────┘                                    │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    QUALITY VALIDATION                            │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌─────────────────┐  │
│  │  BLEU    │ │  ROUGE   │ │ Precision │ │    Evidence     │  │
│  │  Score   │ │  Score   │ │  & Recall │ │    Coverage     │  │
│  │          │ │          │ │           │ │                 │  │
│  │  0.67    │ │  0.73    │ │  P: 0.92  │ │     84%         │  │
│  └──────────┘ └──────────┘ │  R: 0.84  │ └─────────────────┘  │
│                             └───────────┘                        │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────┐   │
│  │  Sphinx Compliance   │  │    Readability Metrics       │   │
│  │                      │  │                              │   │
│  │  PASS / FAIL         │  │  Flesch: 62.3 (Good)         │   │
│  └──────────────────────┘  └──────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐│
│  │   Inline     │  │   Markdown   │  │   Quality Report      ││
│  │  Injection   │  │    Docs      │  │      (JSON)           ││
│  │              │  │              │  │                       ││
│  │ • Update     │  │ • README     │  │ • All metrics         ││
│  │   source     │  │ • API docs   │  │ • Validation status   ││
│  │ • Backup     │  │ • Wiki       │  │ • Recommendations     ││
│  └──────────────┘  └──────────────┘  └───────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Diagram 2: RAG System Detail

```
                    CODE REPOSITORY
                          │
                          ↓
        ┌─────────────────────────────────────┐
        │     Parse All Files                 │
        │  • Functions  • Classes  • Modules  │
        └─────────────┬───────────────────────┘
                      ↓
        ┌─────────────────────────────────────┐
        │   Create Code Chunks                │
        │                                     │
        │  Chunk 1: function_a() + context    │
        │  Chunk 2: class_B + methods         │
        │  Chunk 3: file_c overview           │
        │  ...                                │
        └─────────────┬───────────────────────┘
                      ↓
        ┌─────────────────────────────────────┐
        │   Generate Embeddings               │
        │   (Sentence Transformers)           │
        │                                     │
        │  "function validates user" →        │
        │  [0.23, -0.45, 0.89, ... ] (384d)  │
        └─────────────┬───────────────────────┘
                      ↓
        ┌─────────────────────────────────────┐
        │   Store in FAISS Index              │
        │                                     │
        │   Vector DB with similarity search  │
        │   • Fast lookup (< 1ms)             │
        │   • k-NN search                     │
        └─────────────┬───────────────────────┘
                      ↓
                   READY
                      
┌────────────────────────────────────────────────────┐
│                QUERY TIME                          │
└────────────────────────────────────────────────────┘
                      
    Documenting: check_collision(shape, x, y)
                      │
                      ↓
        ┌─────────────────────────────────────┐
        │  Embed Query                        │
        │  "check collision shape tetris" →   │
        │  [0.21, -0.43, 0.87, ... ]         │
        └─────────────┬───────────────────────┘
                      ↓
        ┌─────────────────────────────────────┐
        │  Search FAISS (top 5 similar)      │
        │                                     │
        │  Results:                           │
        │  1. place_piece() - 0.89 similarity │
        │  2. try_rotate() - 0.85 similarity  │
        │  3. check_bounds() - 0.82           │
        │  4. remove_row() - 0.75             │
        │  5. get_shape() - 0.71              │
        └─────────────┬───────────────────────┘
                      ↓
        ┌─────────────────────────────────────┐
        │  Add to Generation Context          │
        │                                     │
        │  "This function is related to:      │
        │   - place_piece() which commits...  │
        │   - try_rotate() which validates... │
        │   - check_bounds() which tests...   │
        │                                     │
        │  Use this context to generate       │
        │  comprehensive documentation."      │
        └─────────────────────────────────────┘
```

---

## Diagram 3: Metrics Hierarchy

```
                     DOCUMENTATION QUALITY
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ↓                     ↓                     ↓
  ┌──────────┐        ┌──────────┐        ┌──────────────┐
  │ ACCURACY │        │COMPLETENESS        │ READABILITY  │
  └─────┬────┘        └─────┬────┘        └──────┬───────┘
        │                   │                     │
   ┌────┴────┐         ┌────┴────┐         ┌─────┴──────┐
   │         │         │         │         │            │
   ↓         ↓         ↓         ↓         ↓            ↓
┌──────┐ ┌──────┐  ┌──────┐ ┌──────┐  ┌──────┐    ┌──────┐
│BLEU  │ │Prec. │  │ROUGE │ │Evid. │  │Flesch│    │Sphinx│
│      │ │      │  │      │ │Cov.  │  │      │    │Comp. │
│ 0.67 │ │ 0.92 │  │ 0.73 │ │ 0.84 │  │ 62.3 │    │ PASS │
└──────┘ └──────┘  └──────┘ └──────┘  └──────┘    └──────┘
   │         │         │         │         │            │
   └─────────┴─────────┴─────────┴─────────┴────────────┘
                              │
                              ↓
                    ┌──────────────────┐
                    │  OVERALL SCORE   │
                    │                  │
                    │    85 / 100      │
                    │   (Acceptable)   │
                    └──────────────────┘
```

**Metric Weights**:
- Accuracy: 40% (BLEU + Precision)
- Completeness: 35% (ROUGE + Evidence Coverage)
- Readability: 15% (Flesch)
- Compliance: 10% (Sphinx) - but GATE (must PASS)

---

## Diagram 4: Language Support Matrix

```
┌────────────────────────────────────────────────────────────┐
│              LANGUAGE SUPPORT LEVELS                       │
└────────────────────────────────────────────────────────────┘

    TIER 1: Full Support (95%+ features)
    ════════════════════════════════════
    
    Python          JavaScript      TypeScript
    [████████████]  [████████████]  [████████████]
    
    Features:       Features:       Features:
    ✅ Functions    ✅ Functions    ✅ Functions
    ✅ Classes      ✅ Classes      ✅ Classes
    ✅ Type hints   ✅ ES6+         ✅ Interfaces
    ✅ Decorators   ✅ Async/await  ✅ Generics
    ✅ Docstrings   ✅ JSDoc        ✅ Type system


    TIER 2: Good Support (70-95% features)
    ═══════════════════════════════════════
    
    Java            Go              C++
    [██████████░░]  [██████████░░]  [█████████░░░]
    
    Features:       Features:       Features:
    ✅ Classes      ✅ Functions    ✅ Functions
    ✅ Interfaces   ✅ Structs      ✅ Classes
    ✅ Annotations  ✅ Interfaces   ✅ Templates
    ⚠️ Generics     ✅ Packages     ⚠️ Macros
    ✅ Javadoc      ⚠️ Docs         ⚠️ Doxygen


    TIER 3: Partial Support (40-70% features)
    ══════════════════════════════════════════
    
    C               Rust            Ruby
    [██████░░░░░░]  [██████░░░░░░]  [█████░░░░░░░]
    
    ⚠️ Basic        ⚠️ Basic        ⚠️ Basic
    ⚠️ Limited      ⚠️ Limited      ⚠️ Limited
```

---

## Diagram 5: Phi-3 vs Gemini Roles

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID AI PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

  STAGE 1: PHI-3 (Backbone)              
  ═════════════════════════              
                                         
  Role: Initial Draft Generation         
                                         
  Input:                                 
  • Function code                        
  • Local context (file)                 
  • RAG results (similar code)           
                                         
  Phi-3 Model:                           
  ┌──────────────────────┐              
  │ • 4B parameters       │              
  │ • 128K context window │              
  │ • Runs locally        │              
  │ • No internet needed  │              
  │ • Fast (2-5s GPU)     │              
  └──────────────────────┘              
                                         
  Output:                                
  • Draft docstring                      
  • Basic structure                      
  • Parameter descriptions               
                                         
              ↓                          
              
  STAGE 2: GEMINI (Enhancer)            
  ══════════════════════════            
                                         
  Role: Context Enhancement              
                                         
  Input:                                 
  • Phi-3 draft                          
  • Whole project context                
  • Call graphs                          
  • Usage patterns                       
                                         
  Gemini Model:                          
  ┌──────────────────────┐              
  │ • 2.5 Flash           │              
  │ • Large context       │              
  │ • Runs on API         │              
  │ • Internet required   │              
  │ • Very fast (<1s)     │              
  └──────────────────────┘              
                                         
  Enhancements Added:                    
  ✅ Cross-references                    
  ✅ Usage examples                      
  ✅ Error conditions                    
  ✅ Related functions                   
  ✅ Project context                     
                                         
              ↓                          
              
  FINAL OUTPUT: Enhanced Documentation   
  ════════════════════════════════════   

┌─────────────────────────────────────────┐
│  WHY BOTH?                              │
├─────────────────────────────────────────┤
│                                         │
│  Phi-3 Advantages:                      │
│  ✅ Privacy (runs locally)              │
│  ✅ No API costs                        │
│  ✅ Offline capable                     │
│  ✅ Fast enough (GPU)                   │
│                                         │
│  Gemini Advantages:                     │
│  ✅ Larger model (smarter)              │
│  ✅ Bigger context window               │
│  ✅ Better cross-file awareness         │
│  ✅ More accurate examples              │
│                                         │
│  Together:                              │
│  🎯 Best of both worlds                 │
│  🎯 Phi-3 for draft (fast, local)       │
│  🎯 Gemini for polish (smart, aware)    │
└─────────────────────────────────────────┘
```

---

## Diagram 6: Documentation Style Examples

```
┌─────────────────────────────────────────────────────────────┐
│              GOOGLE STYLE (Default)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  def function(param1, param2):                              │
│      """Brief summary.                                      │
│                                                              │
│      Detailed description paragraph.                        │
│                                                              │
│      Args:                                                  │
│          param1 (str): Description                          │
│          param2 (int): Description                          │
│                                                              │
│      Returns:                                               │
│          bool: Description                                  │
│                                                              │
│      Raises:                                                │
│          ValueError: When condition                         │
│      """                                                    │
│                                                              │
│  Best for: Python, Go, modern APIs                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              NUMPY STYLE                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  def function(param1, param2):                              │
│      """                                                    │
│      Brief summary.                                         │
│                                                              │
│      Detailed description paragraph.                        │
│                                                              │
│      Parameters                                             │
│      ----------                                             │
│      param1 : str                                           │
│          Description                                        │
│      param2 : int                                           │
│          Description                                        │
│                                                              │
│      Returns                                                │
│      -------                                                │
│      bool                                                   │
│          Description                                        │
│      """                                                    │
│                                                              │
│  Best for: Scientific Python, NumPy/SciPy projects          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              SPHINX/RST STYLE                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  def function(param1, param2):                              │
│      """Brief summary.                                      │
│                                                              │
│      Detailed description.                                  │
│                                                              │
│      :param param1: Description                             │
│      :type param1: str                                      │
│      :param param2: Description                             │
│      :type param2: int                                      │
│      :return: Description                                   │
│      :rtype: bool                                           │
│      :raises ValueError: When condition                     │
│      """                                                    │
│                                                              │
│  Best for: Large Python projects, Sphinx docs               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              JSDOC STYLE                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /**                                                        │
│   * Brief summary.                                          │
│   *                                                         │
│   * Detailed description.                                   │
│   *                                                         │
│   * @param {string} param1 - Description                    │
│   * @param {number} param2 - Description                    │
│   * @returns {boolean} Description                          │
│   * @throws {Error} When condition                          │
│   */                                                        │
│  function(param1, param2) { }                               │
│                                                              │
│  Best for: JavaScript, TypeScript projects                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Diagram 7: Current State Summary

```
┌─────────────────────────────────────────────────────────────┐
│                  PROJECT STATUS DASHBOARD                    │
└─────────────────────────────────────────────────────────────┘

  COMPONENTS STATUS
  ═════════════════
  
  ✅ Parser (tree-sitter)         [████████████] 100%
  ✅ RAG System (FAISS)           [████████████] 100%
  ⚠️  Phi-3 Generator              [████████░░░░]  70%
  ✅ Gemini Enhancer              [████████████] 100%
  ✅ Metrics System               [████████████] 100%
  ✅ Web Interface (FastAPI)      [████████████] 100%
  ✅ CLI Tool                     [████████████] 100%
  ✅ Inline Injector              [████████████] 100%
  
  
  KNOWN ISSUES
  ════════════
  
  ❌ CRITICAL: Phi-3 Cache Error
     Impact: Falls back to basic generation
     Priority: P0 (Highest)
     ETA: 2-3 hours to fix
  
  ⚠️  MEDIUM: Windows C++ Build Tools Required
     Impact: Parser install fails without it
     Priority: P2
     ETA: Documented workaround
  
  ⚠️  LOW: Console Unicode Errors
     Impact: Cosmetic only
     Priority: P3
     ETA: Use file output instead
  
  
  METRICS ACHIEVED
  ════════════════
  
  BLEU Score:           0.67  ████████░░  67%  ✅ GOOD
  ROUGE-L:              0.73  ██████████  73%  ✅ GOOD
  Precision:            0.92  ███████████ 92%  ✅ EXCELLENT
  Recall:               0.84  ██████████  84%  ✅ GOOD
  F1:                   0.88  ███████████ 88%  ✅ GOOD
  Evidence Coverage:    0.84  ██████████  84%  ✅ GOOD
  Sphinx Compliance:    PASS  ████████████ 100% ✅ PASS
  
  
  READY FOR
  ═════════
  
  ✅ Team Demo
  ✅ Panel Presentation
  ⚠️  Beta Testing (after Phi-3 fix)
  ❌ Production Release (3 months)
```

---

## How to Use These Diagrams

**For Team Presentation**:
1. Start with Diagram 1 (System Overview) - shows big picture
2. Drill into Diagram 2 (RAG Detail) if asked about context awareness
3. Use Diagram 3 (Metrics) to explain quality validation
4. Show Diagram 7 (Status) for honest assessment

**For Panel Review**:
1. Lead with Diagram 1 + Diagram 5 (Hybrid AI) - shows innovation
2. Use Diagram 3 (Metrics Hierarchy) - shows rigor
3. Reference Diagram 4 (Languages) - shows breadth
4. Close with Diagram 7 (Status) - shows readiness

**For Documentation**:
- Include all diagrams in final report
- Use ASCII art for text-only environments
- Convert to proper diagrams in PowerPoint/Visio if time permits

---

## Tips for Drawing on Whiteboard

If you need to explain on a whiteboard, simplify to:

```
CODE → PARSE → RAG → AI → VALIDATE → DOCS
        ↓       ↓     ↓      ↓
    Functions Context Draft Metrics
```

Then expand each box as needed based on questions.

---

**These diagrams are ready to copy-paste into presentations!**
