# Build Time Optimization for Railway

## Current Build Time: ~13 minutes

### What's Taking So Long?

1. **faiss-cpu** (3-5 min) - Compiles C++ code from source
2. **chromadb** (2-3 min) - Compiles native extensions
3. **sentence-transformers** (1-2 min) - Downloads ~80MB embedding model
4. **LangChain packages** (1-2 min) - Large dependency tree
5. **Dataset files** (if committed) - Adds to build context

## Optimization Strategies

### Option 1: Use Pre-built Wheels (Fastest)

Replace `faiss-cpu` with pre-built wheels when available, or use a lighter alternative.

### Option 2: Lazy Load Embeddings

Download the embedding model on first use, not during build.

### Option 3: Use Railway Build Cache

Railway caches Docker layers. Ensure `requirements.txt` changes infrequently.

### Option 4: Remove Unused Dependencies

Only install what you need.

### Option 5: Use Dockerfile with Multi-stage Build

Better caching and optimization.

## Recommended: Optimize Requirements

Consider these changes:

1. **Pin versions** for better caching
2. **Remove pytest** from production (only needed for local dev)
3. **Use specific versions** to avoid re-downloading

