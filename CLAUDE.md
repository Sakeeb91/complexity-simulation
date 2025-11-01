# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a computational life simulator exploring self-replicating programs in a primordial soup environment. Inspired by *Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction* (Agüera y Arcas et al., 2024), the project implements Brainfuck-Fusion (BFF) interpreter with token tracking to study emergent complexity.

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_interpreter.py

# Run specific test class or function
pytest tests/test_tokens.py::TestTokenIntegration::test_mixed_operations_token_tracking

# Run with verbose output
pytest -v
```

### Installation
```bash
# Install in editable mode for development
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

### BFF (Brainfuck-Fusion) Core System

The BFF system implements a **Von Neumann architecture** where code and data share the same tape memory. This is critical to understand for writing tests and debugging.

#### Key Components

1. **BFFTape** (`src/bff/tape.py`)
   - Circular tape with NumPy uint8 array backing
   - Wrapping indexing: `tape[i]` automatically wraps at boundaries
   - Uses `_data` for internal storage, accessible via `.data` property

2. **BFFInterpreter** (`src/bff/interpreter.py`)
   - State: `pc` (program counter), `head0`, `head1`, `steps_executed`
   - Instruction set (10 operations):
     - `<` `>` - Move head0 left/right
     - `{` `}` - Move head1 left/right
     - `+` `-` - Increment/decrement at head0
     - `.` `,` - Copy operations between heads
     - `[` `]` - Conditional jumps (Brainfuck-style loops)
   - Bracket matching precomputed in `__init__` for O(1) jumps
   - Execution terminates on: max_steps, unmatched brackets, or PC out of bounds

3. **Token Tracking System** (`src/bff/tokens.py`)
   - **Purpose**: "Radioactive tracer" to track byte origins through the soup
   - **Token structure**: (epoch, position, char) packed into uint64
     - 20 bits: epoch (when created/mutated)
     - 24 bits: position (global position in soup)
     - 20 bits: char (current value, only 8 bits used)

   - **TokenTape**: Extends BFFTape with parallel `tokens` array
   - **TokenInterpreter**: Extends BFFInterpreter with token-aware execution
     - Copy operations (`.` and `,`): propagate tokens via `copy_with_token()`
     - Increment/decrement (`+`/`-`): preserve epoch/position, update char only
     - Other operations: don't affect tokens

   - **TokenAnalyzer**: Statistical analysis for emergence detection
     - `count_unique_tokens()`: Total unique tokens across soup
     - `top_tokens()`: Most replicated tokens
     - `token_diversity()`: Ratio unique/total (drops when replicators dominate)

4. **Metrics** (`src/bff/metrics.py`)
   - `shannon_entropy()`: Base-2 entropy of byte distribution
   - `kolmogorov_complexity_approx()`: Brotli compression size
   - `high_order_entropy()`: Normalized complexity metric
   - `aggregate_soup_complexity()`: Soup-wide complexity statistics

### Critical Implementation Details

#### NumPy Type Conversions
When doing arithmetic with NumPy types in the interpreter:
```python
# CORRECT - convert to Python int first
current_value = int(self.tape._data[idx])
new_value = (current_value + 1) % 256
self.tape._data[idx] = np.uint8(new_value)

# WRONG - causes overflow
current_value = self.tape._data[idx]  # numpy.uint8
new_value = (current_value + 1) % 256  # OverflowError!
```

#### Token Zero Values
Token value 0 has special meaning:
- Indicates uninitialized/no token
- TokenInterpreter skips updates when `tokens[idx] == 0`
- Tests must use non-zero epochs to ensure tokens get updated

#### Code vs Data Locations in Tests
BFF uses unified code/data memory. When writing interpreter tests:
```python
# CORRECT - separate code and data locations
tape[10] = ord('+')      # Program at position 10
tape._data[0] = 0        # Data at position 0
interpreter.pc = 10      # Execute from program location
interpreter.head0 = 0    # Operate on data location

# WRONG - overwrites instruction with data
tape[0] = ord('+')       # Instruction at position 0
tape.data[0] = 0         # Overwrites the '+' instruction!
interpreter.head0 = 0    # Now executing data, not code
```

#### Direct Field Access in Interpreters
Use `self.tape._data` directly (not through `.data` property) for mutations:
```python
# Preferred in interpreter implementations
self.tape._data[idx] = np.uint8(new_value)

# Also acceptable but less clear
self.tape.data[idx] = np.uint8(new_value)
```

## Common Pitfalls

See `DEBUGGING_NOTES.md` for detailed case studies of common issues:
- NumPy overflow in arithmetic operations
- Token tracking semantics (when tokens update vs. don't)
- Code/data separation in Von Neumann architecture tests
- Zero-packed tokens being skipped by interpreter

## Issue Tracking

Development follows GitHub issues in numerical order. Check issue labels:
- `core` - BFF interpreter fundamentals
- `bff` - BFF-specific features
- `metrics` - Complexity and entropy tracking
- `feature` - New capabilities
- `P0`, `P1`, `P2` - Priority levels

## Commit Conventions

When committing, follow the pattern from recent commits:
- Prefix with issue number when applicable: `Issue #6 Stage 3/8: ...`
- For multi-stage implementations, commit each stage separately
- For bug fixes, explain the root cause in the commit message
- Use imperative mood: "Add feature" not "Added feature"
