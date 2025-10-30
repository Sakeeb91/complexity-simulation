# Python Implementation of Computational Life Simulator

I'll create a comprehensive set of GitHub issues for implementing the BFF (Brainfuck-Fusion) simulator from the paper. Each issue is structured as a Software Engineering work item with clear acceptance criteria.

---

## Repository Setup Issue

### Issue #0: Repository Initialization and Project Structure

**Priority:** P0 (Blocker)  
**Labels:** `setup`, `infrastructure`  
**Estimated Effort:** 2 hours

#### Description
Set up the initial repository structure for the Computational Life simulator based on the paper "Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction" (Agüera y Arcas et al., 2024).

#### Acceptance Criteria
- [ ] Repository created with appropriate name (e.g., `computational-life-simulator`)
- [ ] README.md with project overview and paper citation
- [ ] LICENSE file (suggest MIT or Apache 2.0)
- [ ] `.gitignore` for Python projects
- [ ] Directory structure established:
  ```
  computational-life-simulator/
  ├── src/
  │   ├── bff/
  │   │   ├── __init__.py
  │   │   ├── interpreter.py
  │   │   ├── soup.py
  │   │   └── metrics.py
  │   ├── forth/
  │   ├── z80/
  │   └── utils/
  ├── tests/
  ├── notebooks/
  ├── data/
  ├── visualizations/
  ├── requirements.txt
  ├── setup.py
  └── README.md
  ```
- [ ] `requirements.txt` with initial dependencies:
  ```
  numpy>=1.21.0
  scipy>=1.7.0
  matplotlib>=3.4.0
  seaborn>=0.11.0
  pytest>=7.0.0
  tqdm>=4.62.0
  ```
- [ ] `setup.py` for package installation
- [ ] GitHub Actions workflow for CI/CD (optional but recommended)

#### Technical Notes
- Use Python 3.8+ for compatibility
- Follow PEP 8 style guidelines
- Set up pre-commit hooks for code quality

#### References
- Paper: arXiv:2406.19108v2

---

## Core BFF Implementation Issues

### Issue #1: Implement BFF Tape Data Structure

**Priority:** P0 (Blocker)  
**Labels:** `core`, `bff`, `data-structure`  
**Estimated Effort:** 4 hours  
**Depends On:** #0

#### Description
Implement the fundamental tape data structure that serves as both instruction memory and data memory in the BFF language. This is a core component that all other BFF functionality depends on.

#### Requirements from Paper
From Section 2, page 3:
- Tape consists of single-byte characters
- Default tape length: 64 bytes
- Instructions and data share the same memory space
- Initial values: all zeros or random initialization
- 256 possible byte values (only 10 are valid instructions)

#### Implementation Details

**File:** `src/bff/tape.py`

```python
class BFFTape:
    """
    Represents a BFF program/data tape.
    
    The tape is both instruction memory and data memory, following
    the Von Neumann architecture principle.
    """
    
    def __init__(self, length: int = 64, data: Optional[np.ndarray] = None):
        """
        Initialize a BFF tape.
        
        Args:
            length: Length of the tape in bytes (default: 64)
            data: Optional initial data (numpy array of uint8)
        """
        pass
    
    def __getitem__(self, index: int) -> int:
        """Get byte at index with wrapping."""
        pass
    
    def __setitem__(self, index: int, value: int):
        """Set byte at index with wrapping."""
        pass
    
    def copy(self) -> 'BFFTape':
        """Create a deep copy of the tape."""
        pass
    
    def to_string(self) -> str:
        """Convert tape to string representation."""
        pass
    
    @classmethod
    def random(cls, length: int = 64, seed: Optional[int] = None) -> 'BFFTape':
        """Create a tape with random byte values."""
        pass
```

#### Acceptance Criteria
- [ ] `BFFTape` class implemented with proper docstrings
- [ ] Constructor accepts length and optional initial data
- [ ] Indexing with `[]` operator works correctly
- [ ] Index wrapping implemented (negative and out-of-bounds indices)
- [ ] `copy()` method creates independent copies
- [ ] `random()` class method generates uniformly distributed bytes
- [ ] All values stored as `np.uint8` (0-255 range)
- [ ] Unit tests cover:
  - [ ] Creation with default parameters
  - [ ] Creation with custom data
  - [ ] Index wrapping (positive, negative, out-of-bounds)
  - [ ] Copy independence
  - [ ] Random generation with seed reproducibility
- [ ] Test coverage ≥ 95%

#### Testing Requirements

**File:** `tests/test_tape.py`

```python
def test_tape_creation():
    """Test basic tape creation."""
    tape = BFFTape(length=64)
    assert len(tape) == 64
    assert all(tape[i] == 0 for i in range(64))

def test_tape_indexing():
    """Test tape indexing with wrapping."""
    tape = BFFTape(length=10)
    tape[0] = 42
    assert tape[0] == 42
    assert tape[10] == 42  # Wrapping
    assert tape[-10] == 42  # Negative wrapping

def test_tape_copy_independence():
    """Ensure copies are independent."""
    tape1 = BFFTape.random(64, seed=42)
    tape2 = tape1.copy()
    tape2[0] = 255
    assert tape1[0] != tape2[0]
```

#### Technical Notes
- Use NumPy arrays for performance
- Implement modulo arithmetic for index wrapping
- Consider memory efficiency for large-scale simulations

#### References
- Paper Section 2: "BFF: Extending Brainfuck", page 3

---

### Issue #2: Implement BFF Instruction Set

**Priority:** P0 (Blocker)  
**Labels:** `core`, `bff`, `interpreter`  
**Estimated Effort:** 8 hours  
**Depends On:** #1

#### Description
Implement the complete BFF instruction set interpreter. BFF extends Brainfuck by removing I/O streams and adding head operations for self-modification.

#### Requirements from Paper
From Section 2, page 3, the complete instruction set:

| Instruction | Operation |
|-------------|-----------|
| `<` | `head0 = head0 - 1` |
| `>` | `head0 = head0 + 1` |
| `{` | `head1 = head1 - 1` |
| `}` | `head1 = head1 + 1` |
| `-` | `tape[head0] = tape[head0] - 1` |
| `+` | `tape[head0] = tape[head0] + 1` |
| `.` | `tape[head1] = tape[head0]` |
| `,` | `tape[head0] = tape[head1]` |
| `[` | `if (tape[head0] == 0): jump to matching ]` |
| `]` | `if (tape[head0] != 0): jump to matching [` |

#### Implementation Details

**File:** `src/bff/interpreter.py`

```python
class BFFInterpreter:
    """
    Interpreter for BFF (Brainfuck-Fusion) programs.
    
    Executes BFF programs on a tape that serves as both
    instruction and data memory.
    """
    
    def __init__(self, tape: BFFTape, max_steps: int = 2**13):
        """
        Initialize the BFF interpreter.
        
        Args:
            tape: The BFF tape to execute on
            max_steps: Maximum number of instructions to execute (default: 8192)
        """
        self.tape = tape
        self.max_steps = max_steps
        self.pc = 0  # Program counter (instruction pointer)
        self.head0 = 0  # Read/write head 0
        self.head1 = 0  # Read/write head 1
        self.steps_executed = 0
        self.terminated = False
        self.bracket_map = self._build_bracket_map()
    
    def _build_bracket_map(self) -> Dict[int, int]:
        """
        Build a mapping of bracket positions for O(1) jumps.
        
        Returns:
            Dictionary mapping [ positions to ] positions and vice versa
        """
        pass
    
    def step(self) -> bool:
        """
        Execute a single instruction.
        
        Returns:
            True if execution should continue, False if terminated
        """
        pass
    
    def execute(self) -> BFFTape:
        """
        Execute the program until termination or max_steps.
        
        Returns:
            The modified tape after execution
        """
        pass
    
    def _execute_instruction(self, instruction: int):
        """Execute a single instruction byte."""
        pass
```

#### Acceptance Criteria
- [ ] `BFFInterpreter` class implemented
- [ ] All 10 instructions correctly implemented:
  - [ ] `<` and `>` for head0 movement
  - [ ] `{` and `}` for head1 movement
  - [ ] `-` and `+` for tape value modification
  - [ ] `.` and `,` for copy operations
  - [ ] `[` and `]` for conditional jumps
- [ ] Bracket matching implemented with preprocessing (O(1) jump time)
- [ ] Program counter advances correctly
- [ ] Execution terminates on:
  - [ ] Max steps reached
  - [ ] Unmatched bracket encountered
  - [ ] Program counter out of bounds
- [ ] Non-instruction bytes treated as no-ops
- [ ] All arithmetic wraps at byte boundaries (0-255)
- [ ] Unit tests cover:
  - [ ] Each instruction individually
  - [ ] Nested brackets
  - [ ] Unmatched brackets (error case)
  - [ ] Head wrapping
  - [ ] Value wrapping (overflow/underflow)
  - [ ] Max steps termination
  - [ ] Example self-replicator from paper (Figure 4)
- [ ] Test coverage ≥ 95%

#### Testing Requirements

**File:** `tests/test_interpreter.py`

```python
def test_head_movement():
    """Test head movement instructions."""
    tape = BFFTape(length=10)
    interpreter = BFFInterpreter(tape)
    
    # Test > instruction
    tape[0] = ord('>')
    interpreter.step()
    assert interpreter.head0 == 1
    
    # Test < instruction
    tape[1] = ord('<')
    interpreter.step()
    assert interpreter.head0 == 0

def test_value_modification():
    """Test increment and decrement."""
    tape = BFFTape(length=10)
    tape[0] = ord('+')
    tape[1] = ord('+')
    tape[2] = ord('-')
    
    interpreter = BFFInterpreter(tape)
    interpreter.execute()
    
    assert tape[0] == ord('+')  # Instructions unchanged
    assert tape.data[interpreter.head0] == 1  # Net +1

def test_copy_operations():
    """Test copy between heads."""
    tape = BFFTape(length=10)
    tape.data[0] = 42
    tape[1] = ord('.')  # Copy from head0 to head1
    
    interpreter = BFFInterpreter(tape)
    interpreter.head0 = 0
    interpreter.head1 = 5
    interpreter.step()
    
    assert tape.data[5] == 42

def test_loop_execution():
    """Test bracket loops."""
    # Simple loop: [+>] (increment and move right while non-zero)
    tape = BFFTape(length=10)
    tape[0] = ord('[')
    tape[1] = ord('+')
    tape[2] = ord('>')
    tape[3] = ord(']')
    tape.data[0] = 5  # Starting value
    
    # This should increment 5 times and move head0 to position 5
    # Actually, test a simpler case...

def test_self_replicator():
    """Test the self-replicator from Figure 4 of the paper."""
    # [[{.>]-] ]-]>.{[[
    replicator_str = "[[{.>]-] ]-]>.{[["
    tape = BFFTape(length=128)
    for i, char in enumerate(replicator_str):
        tape[i] = ord(char)
    
    # TODO: Complete this test based on expected behavior
```

#### Technical Notes
- Use a dictionary for O(1) bracket matching (preprocess in `__init__`)
- Handle wrapping for all pointer arithmetic
- Consider using `chr()` and `ord()` for instruction character conversion
- Profile performance for large step counts

#### References
- Paper Section 2: "BFF: Extending Brainfuck", page 3
- Figure 4: Example self-replicator execution, page 8

---

### Issue #3: Implement Primordial Soup Simulator

**Priority:** P0 (Blocker)  
**Labels:** `core`, `bff`, `simulation`  
**Estimated Effort:** 10 hours  
**Depends On:** #2

#### Description
Implement the "primordial soup" simulation environment where random programs interact through concatenation and execution. This is the main experimental framework from the paper.

#### Requirements from Paper
From Section 2.1, page 4:
- Default soup size: 2^17 = 131,072 programs
- Each program: 64 bytes
- Random initialization from uniform distribution
- Each epoch:
  - Select random ordered pairs of programs
  - Concatenate them (A + B)
  - Execute concatenated program
  - Split result back into two 64-byte programs
  - Return modified programs to soup
- No explicit fitness function
- Optional background mutation rate

The interaction is described as:
```
A + B --a--> split(exec(AB)) = A' + B'
```

#### Implementation Details

**File:** `src/bff/soup.py`

```python
class PrimordialSoup:
    """
    Primordial soup simulator for BFF programs.
    
    Implements the Turing gas variant from Fontana (1990) adapted
    for BFF programs as described in the paper.
    """
    
    def __init__(
        self,
        soup_size: int = 2**17,
        tape_length: int = 64,
        max_steps_per_execution: int = 2**13,
        mutation_rate: float = 0.00024,  # 0.024% default from paper
        seed: Optional[int] = None
    ):
        """
        Initialize the primordial soup.
        
        Args:
            soup_size: Number of programs in the soup (default: 131,072)
            tape_length: Length of each program in bytes (default: 64)
            max_steps_per_execution: Max steps per program execution (default: 8,192)
            mutation_rate: Probability of mutation per byte per epoch (default: 0.024%)
            seed: Random seed for reproducibility
        """
        self.soup_size = soup_size
        self.tape_length = tape_length
        self.max_steps = max_steps_per_execution
        self.mutation_rate = mutation_rate
        self.rng = np.random.default_rng(seed)
        
        # Initialize random soup
        self.programs = [
            BFFTape.random(tape_length, seed=self.rng.integers(0, 2**32))
            for _ in range(soup_size)
        ]
        
        self.epoch = 0
        self.total_executions = 0
    
    def run_epoch(self, interactions_per_epoch: Optional[int] = None):
        """
        Run one epoch of the simulation.
        
        Args:
            interactions_per_epoch: Number of random pair interactions
                                   (default: soup_size)
        """
        if interactions_per_epoch is None:
            interactions_per_epoch = self.soup_size
        
        for _ in range(interactions_per_epoch):
            # Select random ordered pair
            i, j = self.rng.choice(self.soup_size, size=2, replace=False)
            
            # Execute interaction
            self._interact(i, j)
        
        # Apply background mutations
        self._apply_mutations()
        
        self.epoch += 1
    
    def _interact(self, idx_a: int, idx_b: int):
        """
        Perform interaction between two programs.
        
        Args:
            idx_a: Index of first program
            idx_b: Index of second program
        """
        # Get programs
        prog_a = self.programs[idx_a]
        prog_b = self.programs[idx_b]
        
        # Concatenate
        concatenated = self._concatenate(prog_a, prog_b)
        
        # Execute
        interpreter = BFFInterpreter(concatenated, max_steps=self.max_steps)
        result = interpreter.execute()
        
        # Split and return
        new_a, new_b = self._split(result)
        self.programs[idx_a] = new_a
        self.programs[idx_b] = new_b
        
        self.total_executions += 1
    
    def _concatenate(self, tape_a: BFFTape, tape_b: BFFTape) -> BFFTape:
        """Concatenate two tapes."""
        pass
    
    def _split(self, tape: BFFTape) -> Tuple[BFFTape, BFFTape]:
        """Split tape into two equal parts."""
        pass
    
    def _apply_mutations(self):
        """Apply random mutations to the soup."""
        pass
    
    def run(self, num_epochs: int, callback: Optional[Callable] = None):
        """
        Run multiple epochs.
        
        Args:
            num_epochs: Number of epochs to run
            callback: Optional function called after each epoch
                     with signature: callback(soup, epoch)
        """
        for _ in tqdm(range(num_epochs), desc="Running simulation"):
            self.run_epoch()
            if callback:
                callback(self, self.epoch)
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get current state snapshot for analysis."""
        return {
            'epoch': self.epoch,
            'soup_size': self.soup_size,
            'programs': [p.copy() for p in self.programs],
            'total_executions': self.total_executions
        }
```

#### Acceptance Criteria
- [ ] `PrimordialSoup` class implemented
- [ ] Random initialization of soup with configurable size
- [ ] `run_epoch()` performs correct number of interactions
- [ ] Random pair selection without replacement within each interaction
- [ ] Concatenation creates 128-byte tape from two 64-byte tapes
- [ ] Execution uses BFFInterpreter with max_steps
- [ ] Splitting correctly divides result back into two tapes
- [ ] Background mutations applied according to mutation_rate
- [ ] Progress tracking (epoch counter, total executions)
- [ ] `run()` method with progress bar (using tqdm)
- [ ] Optional callback mechanism for metrics collection
- [ ] Snapshot functionality for checkpointing
- [ ] Unit tests cover:
  - [ ] Soup initialization
  - [ ] Pair selection (no duplicates)
  - [ ] Concatenate/split round-trip
  - [ ] Mutation rate validation
  - [ ] Epoch progression
  - [ ] Callback invocation
- [ ] Integration test: Run 100 epochs without errors
- [ ] Test coverage ≥ 90%

#### Testing Requirements

**File:** `tests/test_soup.py`

```python
def test_soup_initialization():
    """Test soup initialization."""
    soup = PrimordialSoup(soup_size=100, tape_length=64, seed=42)
    assert len(soup.programs) == 100
    assert all(len(p) == 64 for p in soup.programs)

def test_concatenate_split():
    """Test concatenate and split operations."""
    soup = PrimordialSoup(soup_size=10, seed=42)
    tape_a = soup.programs[0].copy()
    tape_b = soup.programs[1].copy()
    
    concatenated = soup._concatenate(tape_a, tape_b)
    assert len(concatenated) == 128
    
    split_a, split_b = soup._split(concatenated)
    assert len(split_a) == 64
    assert len(split_b) == 64

def test_mutation_rate():
    """Test that mutations occur at expected rate."""
    soup = PrimordialSoup(soup_size=1000, mutation_rate=0.01, seed=42)
    
    # Save initial state
    initial = [p.copy() for p in soup.programs]
    
    # Apply mutations
    soup._apply_mutations()
    
    # Count differences
    total_bytes = soup.soup_size * soup.tape_length
    differences = sum(
        np.sum(initial[i].data != soup.programs[i].data)
        for i in range(soup.soup_size)
    )
    
    # Should be approximately mutation_rate * total_bytes
    expected = 0.01 * total_bytes
    assert 0.5 * expected < differences < 1.5 * expected

def test_epoch_execution():
    """Test epoch execution."""
    soup = PrimordialSoup(soup_size=10, seed=42)
    initial_epoch = soup.epoch
    
    soup.run_epoch()
    
    assert soup.epoch == initial_epoch + 1
    assert soup.total_executions >= soup.soup_size

def test_run_with_callback():
    """Test multi-epoch run with callback."""
    soup = PrimordialSoup(soup_size=10, seed=42)
    epochs_seen = []
    
    def callback(s, epoch):
        epochs_seen.append(epoch)
    
    soup.run(num_epochs=5, callback=callback)
    
    assert epochs_seen == [1, 2, 3, 4, 5]
    assert soup.epoch == 5
```

#### Performance Requirements
- [ ] Handle 2^17 programs efficiently
- [ ] Memory usage < 16 GB for default configuration
- [ ] Epoch execution time < 30 seconds on standard hardware

#### Technical Notes
- Use NumPy for efficient array operations
- Consider multiprocessing for parallel execution (future enhancement)
- Profile memory usage for large soups
- Implement efficient mutation using NumPy's random sampling

#### References
- Paper Section 2.1: "Primordial soup simulations", page 4

---

### Issue #4: Implement High-Order Entropy Complexity Metric

**Priority:** P1 (High)  
**Labels:** `metrics`, `analysis`, `bff`  
**Estimated Effort:** 8 hours  
**Depends On:** #3

#### Description
Implement the "high-order entropy" complexity metric introduced in the paper. This metric detects state transitions when self-replicators emerge and dominate the soup.

#### Requirements from Paper
From Section 2.1, page 4-5:

**Definition:**
High-order entropy = Shannon entropy - Normalized Kolmogorov complexity

**Properties:**
1. Expected high-order entropy → 0 for random i.i.d. sequences as n → ∞
2. Expected high-order entropy → Shannon entropy of D for n copies of k i.i.d. characters

**Approximation:**
Since Kolmogorov complexity is uncomputable, approximate using compressed size via Brotli compression (quality level 2).

**Purpose:**
- Random noise has ~0 complexity
- Soup dominated by self-replicator copies has substantial non-zero complexity
- Detects state transition from pre-life to life

#### Implementation Details

**File:** `src/bff/metrics.py`

```python
import brotli
from typing import Union, List
from collections import Counter
import numpy as np

class ComplexityMetrics:
    """
    Complexity metrics for analyzing BFF soup evolution.
    
    Implements high-order entropy and related metrics from the paper.
    """
    
    @staticmethod
    def shannon_entropy(data: Union[np.ndarray, bytes, List[int]]) -> float:
        """
        Calculate Shannon entropy of a sequence.
        
        H(X) = -Σ p(x) * log2(p(x))
        
        Args:
            data: Sequence of bytes or integers
            
        Returns:
            Shannon entropy in bits
        """
        if isinstance(data, np.ndarray):
            data = data.flatten()
        
        # Count frequencies
        counts = Counter(data)
        total = len(data)
        
        # Calculate entropy
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        return entropy
    
    @staticmethod
    def kolmogorov_complexity_approx(
        data: Union[np.ndarray, bytes],
        compression_quality: int = 2
    ) -> int:
        """
        Approximate Kolmogorov complexity using Brotli compression.
        
        Uses the well-established practice of approximating Kolmogorov
        complexity with Lempel-Ziv-style compressors.
        
        Args:
            data: Data to compress
            compression_quality: Brotli quality level (0-11, default: 2)
            
        Returns:
            Compressed size in bytes
        """
        if isinstance(data, np.ndarray):
            data = data.tobytes()
        elif not isinstance(data, bytes):
            data = bytes(data)
        
        compressed = brotli.compress(data, quality=compression_quality)
        return len(compressed)
    
    @staticmethod
    def high_order_entropy(
        data: Union[np.ndarray, bytes],
        compression_quality: int = 2
    ) -> float:
        """
        Calculate high-order entropy.
        
        High-order entropy = Shannon entropy - (Kolmogorov complexity / n)
        
        This metric captures information that can only be explained by
        relations between different characters, factoring out i.i.d. noise.
        
        Args:
            data: Sequence data
            compression_quality: Brotli quality level
            
        Returns:
            High-order entropy value
        """
        if isinstance(data, np.ndarray):
            data_array = data.flatten()
        else:
            data_array = np.frombuffer(data, dtype=np.uint8)
        
        n = len(data_array)
        if n == 0:
            return 0.0
        
        # Calculate Shannon entropy
        h_shannon = ComplexityMetrics.shannon_entropy(data_array)
        
        # Calculate normalized Kolmogorov complexity
        k_compressed = ComplexityMetrics.kolmogorov_complexity_approx(
            data_array, compression_quality
        )
        k_normalized = (k_compressed * 8) / n  # Convert bytes to bits per symbol
        
        # High-order entropy
        return max(0.0, h_shannon - k_normalized)
    
    @staticmethod
    def soup_complexity(
        soup: 'PrimordialSoup',
        sample_size: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate complexity metrics for entire soup.
        
        Args:
            soup: PrimordialSoup instance
            sample_size: Optional sample size (None = use all programs)
            
        Returns:
            Dictionary with various complexity metrics
        """
        # Concatenate all programs or sample
        if sample_size is None or sample_size >= soup.soup_size:
            data = np.concatenate([p.data for p in soup.programs])
        else:
            indices = np.random.choice(soup.soup_size, sample_size, replace=False)
            data = np.concatenate([soup.programs[i].data for i in indices])
        
        return {
            'shannon_entropy': ComplexityMetrics.shannon_entropy(data),
            'kolmogorov_approx': ComplexityMetrics.kolmogorov_complexity_approx(data),
            'high_order_entropy': ComplexityMetrics.high_order_entropy(data),
            'unique_programs': len(set(tuple(p.data) for p in soup.programs)),
            'soup_size': soup.soup_size,
            'epoch': soup.epoch
        }
```

#### Acceptance Criteria
- [ ] `ComplexityMetrics` class implemented
- [ ] Shannon entropy correctly calculated
- [ ] Kolmogorov complexity approximation using Brotli
- [ ] High-order entropy formula correctly implemented
- [ ] `soup_complexity()` aggregates metrics across entire soup
- [ ] Optional sampling for large soups
- [ ] Unit tests cover:
  - [ ] Shannon entropy on uniform random data ≈ 8.0 bits
  - [ ] Shannon entropy on constant data = 0.0 bits
  - [ ] High-order entropy on random data ≈ 0
  - [ ] High-order entropy on repeated patterns > 0
  - [ ] Kolmogorov approximation is reasonable
  - [ ] Soup complexity calculation
- [ ] Performance: Calculate soup complexity in < 5 seconds for default soup size
- [ ] Test coverage ≥ 95%

#### Testing Requirements

**File:** `tests/test_metrics.py`

```python
def test_shannon_entropy_uniform():
    """Test Shannon entropy on uniform random data."""
    data = np.random.randint(0, 256, size=10000, dtype=np.uint8)
    entropy = ComplexityMetrics.shannon_entropy(data)
    # Should be close to 8.0 bits for uniform distribution
    assert 7.9 < entropy < 8.1

def test_shannon_entropy_constant():
    """Test Shannon entropy on constant data."""
    data = np.full(1000, 42, dtype=np.uint8)
    entropy = ComplexityMetrics.shannon_entropy(data)
    assert entropy == 0.0

def test_high_order_entropy_random():
    """High-order entropy should be near 0 for random data."""
    data = np.random.randint(0, 256, size=10000, dtype=np.uint8)
    hoe = ComplexityMetrics.high_order_entropy(data)
    # Random data compresses poorly, so K/n ≈ H, giving HoE ≈ 0
    assert -1.0 < hoe < 1.0

def test_high_order_entropy_repeated():
    """High-order entropy should be > 0 for repeated patterns."""
    # Repeat "ABCD" many times
    pattern = b"ABCD" * 1000
    hoe = ComplexityMetrics.high_order_entropy(pattern)
    # Pattern compresses well, so K/n << H, giving HoE > 0
    assert hoe > 1.0

def test_soup_complexity():
    """Test soup complexity calculation."""
    soup = PrimordialSoup(soup_size=100, tape_length=64, seed=42)
    metrics = ComplexityMetrics.soup_complexity(soup)
    
    assert 'shannon_entropy' in metrics
    assert 'high_order_entropy' in metrics
    assert metrics['soup_size'] == 100
    assert metrics['epoch'] == 0
```

#### Technical Notes
- Install Brotli: `pip install brotli`
- Brotli quality level 2 is fast and sufficient for approximation
- For very large soups, implement sampling to reduce computation time
- Cache compression results if recalculating frequently

#### References
- Paper Section 2.1: "Complexity metrics", pages 4-5
- Figure 1: Tracer tokens and high-order entropy, page 5

---

### Issue #5: Implement Token Tracking System

**Priority:** P2 (Medium)  
**Labels:** `metrics`, `analysis`, `debugging`  
**Estimated Effort:** 12 hours  
**Depends On:** #3

#### Description
Implement the "radioactive tracer" token tracking system for detailed analysis of soup dynamics. This allows pinpointing exactly when and where self-replicators emerge.

#### Requirements from Paper
From Section 2.1, page 5-7:

**Token Structure:**
- Each byte in the soup has an attached token: (epoch, position, char)
- Packed into 64-bit integers
- Initial tokens are unique for each byte

**Token Rules:**
- New tokens created at initialization or mutation
- Copy operations (`.` and `,`) copy tokens
- Displaced tokens are overwritten
- Increment/decrement (`+` and `-`) only affect char, preserving origin

**Analysis Capabilities:**
- Count unique tokens over time
- Identify most popular tokens
- Trace token origins back to specific epoch/position
- Detect state transitions via token diversity collapse

#### Implementation Details

**File:** `src/bff/tokens.py`

```python
@dataclass
class Token:
    """
    Represents a traceable token for a single byte.
    
    Tokens act like radioactive tracers, allowing us to track
    the origin and propagation of bytes through the soup.
    """
    epoch: int  # When this byte was created/mutated
    position: int  # Original position in soup (program_idx * tape_length + byte_idx)
    char: int  # Current character value (0-255)
    
    def to_uint64(self) -> int:
        """Pack token into 64-bit integer."""
        # Use 20 bits for epoch, 24 bits for position, 20 bits for char
        return (self.epoch << 44) | (self.position << 20) | self.char
    
    @classmethod
    def from_uint64(cls, value: int) -> 'Token':
        """Unpack token from 64-bit integer."""
        epoch = (value >> 44) & 0xFFFFF
        position = (value >> 20) & 0xFFFFFF
        char = value & 0xFFFFF
        return cls(epoch, position, char & 0xFF)  # Ensure char is 0-255
    
    def copy_with_char(self, new_char: int) -> 'Token':
        """Create copy with updated char (for +/- operations)."""
        return Token(self.epoch, self.position, new_char)


class TokenTape(BFFTape):
    """
    Extended BFF tape with token tracking.
    
    Each byte has an associated token that tracks its origin.
    """
    
    def __init__(self, length: int = 64, data: Optional[np.ndarray] = None,
                 tokens: Optional[np.ndarray] = None):
        """
        Initialize token tape.
        
        Args:
            length: Tape length
            data: Optional initial data
            tokens: Optional initial tokens (uint64 array)
        """
        super().__init__(length, data)
        
        if tokens is None:
            # Create unique tokens for initialization
            self.tokens = np.zeros(length, dtype=np.uint64)
        else:
            self.tokens = tokens.copy()
    
    def __setitem__(self, index: int, value: int):
        """Set byte and update token char only."""
        super().__setitem__(index, value)
        # Update char in token
        token = Token.from_uint64(self.tokens[index % self.length])
        token.char = value
        self.tokens[index % self.length] = token.to_uint64()
    
    def copy_with_token(self, src_idx: int, dst_idx: int):
        """Copy byte and token from src to dst."""
        src_idx = src_idx % self.length
        dst_idx = dst_idx % self.length
        self.data[dst_idx] = self.data[src_idx]
        self.tokens[dst_idx] = self.tokens[src_idx]
    
    @classmethod
    def random(cls, length: int = 64, epoch: int = 0, 
               program_idx: int = 0, seed: Optional[int] = None) -> 'TokenTape':
        """
        Create random tape with unique tokens.
        
        Args:
            length: Tape length
            epoch: Current epoch (for token creation)
            program_idx: Program index in soup (for unique positions)
            seed: Random seed
        """
        rng = np.random.default_rng(seed)
        data = rng.integers(0, 256, size=length, dtype=np.uint8)
        
        # Create unique tokens
        tokens = np.zeros(length, dtype=np.uint64)
        for i in range(length):
            position = program_idx * length + i
            token = Token(epoch, position, int(data[i]))
            tokens[i] = token.to_uint64()
        
        return cls(length, data, tokens)


class TokenInterpreter(BFFInterpreter):
    """
    BFF interpreter with token tracking.
    
    Tracks token propagation through copy operations.
    """
    
    def __init__(self, tape: TokenTape, max_steps: int = 2**13):
        """Initialize with a TokenTape."""
        if not isinstance(tape, TokenTape):
            raise TypeError("TokenInterpreter requires TokenTape")
        super().__init__(tape, max_steps)
    
    def _execute_instruction(self, instruction: int):
        """Execute instruction with token tracking."""
        instr_char = chr(instruction) if instruction < 128 else None
        
        if instr_char == '.':
            # Copy from head0 to head1 (including token)
            self.tape.copy_with_token(self.head0, self.head1)
        elif instr_char == ',':
            # Copy from head1 to head0 (including token)
            self.tape.copy_with_token(self.head1, self.head0)
        elif instr_char in ['+', '-']:
            # Only update char in token, preserve origin
            idx = self.head0 % self.tape.length
            current_value = self.tape.data[idx]
            if instr_char == '+':
                new_value = (current_value + 1) % 256
            else:
                new_value = (current_value - 1) % 256
            
            # Update value and token char
            token = Token.from_uint64(self.tape.tokens[idx])
            token.char = new_value
            self.tape.data[idx] = new_value
            self.tape.tokens[idx] = token.to_uint64()
        else:
            # Other instructions don't affect tokens
            super()._execute_instruction(instruction)


class TokenAnalyzer:
    """
    Analyze token statistics in a soup.
    """
    
    @staticmethod
    def count_unique_tokens(soup: 'TokenPrimordialSoup') -> int:
        """Count unique tokens across entire soup."""
        all_tokens = np.concatenate([p.tokens for p in soup.programs])
        return len(np.unique(all_tokens))
    
    @staticmethod
    def top_tokens(soup: 'TokenPrimordialSoup', k: int = 32) -> List[Tuple[int, int]]:
        """
        Get the k most common tokens.
        
        Returns:
            List of (token, count) tuples
        """
        all_tokens = np.concatenate([p.tokens for p in soup.programs])
        unique, counts = np.unique(all_tokens, return_counts=True)
        
        # Sort by count descending
        sorted_indices = np.argsort(-counts)
        
        return [(unique[i], counts[i]) for i in sorted_indices[:k]]
    
    @staticmethod
    def token_diversity(soup: 'TokenPrimordialSoup') -> float:
        """
        Calculate token diversity (unique tokens / total tokens).
        
        Returns value between 0 and 1.
        """
        total_tokens = soup.soup_size * soup.tape_length
        unique_tokens = TokenAnalyzer.count_unique_tokens(soup)
        return unique_tokens / total_tokens
```

#### Acceptance Criteria
- [ ] `Token` dataclass with packing/unpacking to uint64
- [ ] `TokenTape` extending `BFFTape` with token array
- [ ] Token creation with unique (epoch, position, char) tuples
- [ ] `copy_with_token()` method copies both data and tokens
- [ ] `TokenInterpreter` extending `BFFInterpreter`:
  - [ ] `.` and `,` copy tokens
  - [ ] `+` and `-` preserve token origin, update char only
  - [ ] Other operations don't affect tokens
- [ ] `TokenAnalyzer` with analysis methods:
  - [ ] `count_unique_tokens()`
  - [ ] `top_tokens()`
  - [ ] `token_diversity()`
- [ ] `TokenPrimordialSoup` variant using token system
- [ ] Unit tests cover:
  - [ ] Token packing/unpacking preserves values
  - [ ] Token creation with unique IDs
  - [ ] Copy operations propagate tokens
  - [ ] Increment/decrement preserve origin
  - [ ] Token counting and statistics
- [ ] Integration test: Track tokens through 1000 epochs
- [ ] Test coverage ≥ 90%

#### Testing Requirements

**File:** `tests/test_tokens.py`

```python
def test_token_packing():
    """Test token packing/unpacking."""
    token = Token(epoch=100, position=50000, char=42)
    packed = token.to_uint64()
    unpacked = Token.from_uint64(packed)
    
    assert unpacked.epoch == 100
    assert unpacked.position == 50000
    assert unpacked.char == 42

def test_token_tape_creation():
    """Test token tape creation with unique tokens."""
    tape = TokenTape.random(length=64, epoch=0, program_idx=5, seed=42)
    
    # All tokens should be unique
    assert len(np.unique(tape.tokens)) == 64
    
    # Check one token has correct structure
    token = Token.from_uint64(tape.tokens[0])
    assert token.epoch == 0
    assert 320 <= token.position < 384  # 5 * 64 + [0-64)

def test_copy_with_token():
    """Test token propagation through copy."""
    tape = TokenTape.random(length=10, epoch=0, program_idx=0, seed=42)
    original_token = tape.tokens[0]
    
    tape.copy_with_token(0, 5)
    
    assert tape.tokens[5] == original_token
    assert tape.data[5] == tape.data[0]

def test_token_interpreter_copy():
    """Test token interpreter handles copy operations."""
    tape = TokenTape(length=128)
    tape.data[0] = 42
    tape.tokens[0] = Token(0, 0, 42).to_uint64()
    
    # Program: . (copy from head0 to head1)
    tape[1] = ord('.')
    
    interpreter = TokenInterpreter(tape)
    interpreter.head0 = 0
    interpreter.head1 = 10
    interpreter.pc = 1
    interpreter.step()
    
    # Token should be copied
    assert tape.tokens[10] == tape.tokens[0]
```

#### Performance Requirements
- [ ] Token tracking adds < 30% overhead vs non-token simulation
- [ ] Memory usage for tokens: soup_size * tape_length * 8 bytes

#### Technical Notes
- Use NumPy uint64 arrays for efficient token storage
- Consider bit packing layout carefully (20-24-20 split)
- Profile memory usage for large-scale simulations
- Token uniqueness can be verified by checking for collisions

#### References
- Paper Section 2.1: "How self-replicators emerge: a case study", pages 5-7
- Figure 1: Tracer tokens visualization, page 5
- Figure 2: Token tracking through state transition, page 7

---

### Issue #6: Implement Visualization System

**Priority:** P2 (Medium)  
**Labels:** `visualization`, `analysis`, `ui`  
**Estimated Effort:** 10 hours  
**Depends On:** #4, #5

#### Description
Implement visualization tools to display soup evolution, complexity metrics over time, and 2D grid simulations. This enables analysis similar to Figures 1, 2, 5, 6, 7 in the paper.

#### Requirements from Paper
Multiple visualization types needed:
1. **Complexity over time** (Figure 5): High-order entropy distribution across epochs
2. **Token statistics** (Figure 1): Unique tokens, popular tokens over time
3. **Heat maps** (Figure 6): Mutation rate vs time-to-complexity grid
4. **Histograms** (Figure 7): Final complexity distribution comparisons
5. **2D grid visualization** (Figure 8): Spatial soup with color-coded programs

#### Implementation Details

**File:** `src/bff/visualization.py`

```python
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional
import numpy as np

class SoupVisualizer:
    """
    Visualization tools for BFF soup evolution.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize visualizer.
        
        Args:
            style: Matplotlib style to use
        """
        plt.style.use(style)
        sns.set_palette("husl")
    
    def plot_complexity_over_time(
        self,
        history: List[Dict[str, float]],
        save_path: Optional[str] = None
    ):
        """
        Plot high-order entropy over time.
        
        Replicates Figure 5 from the paper.
        
        Args:
            history: List of metric dictionaries from each epoch
            save_path: Optional path to save figure
        """
        epochs = [h['epoch'] for h in history]
        complexity = [h['high_order_entropy'] for h in history]
        
        plt.figure(figsize=(12, 6))
        plt.plot(epochs, complexity, linewidth=2)
        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel('High-order Entropy', fontsize=12)
        plt.title('Evolution of Complexity Over Time', fontsize=14)
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_complexity_distribution(
        self,
        runs: List[List[Dict[str, float]]],
        quantiles: List[float] = [0.1, 0.25, 0.5, 0.75, 0.9],
        save_path: Optional[str] = None
    ):
        """
        Plot complexity distribution over time across multiple runs.
        
        Replicates Figure 5 from the paper with quantile bands.
        
        Args:
            runs: List of run histories (each run is a list of metric dicts)
            quantiles: Quantiles to display as shaded regions
            save_path: Optional path to save figure
        """
        # Find common epoch range
        max_epochs = min(len(run) for run in runs)
        epochs = list(range(max_epochs))
        
        # Collect complexity values at each epoch
        complexity_matrix = np.array([
            [run[e]['high_order_entropy'] for e in epochs]
            for run in runs
        ])
        
        # Calculate quantiles
        quantile_values = {}
        for q in quantiles:
            quantile_values[q] = np.quantile(complexity_matrix, q, axis=0)
        
        # Plot
        plt.figure(figsize=(14, 7))
        
        # Median line
        plt.plot(epochs, quantile_values[0.5], 
                linewidth=2, label='Median', color='darkblue')
        
        # Quantile bands
        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(quantiles)//2))
        for i in range(len(quantiles)//2):
            lower_q = quantiles[i]
            upper_q = quantiles[-(i+1)]
            plt.fill_between(
                epochs,
                quantile_values[lower_q],
                quantile_values[upper_q],
                alpha=0.3,
                color=colors[i],
                label=f'{int(lower_q*100)}-{int(upper_q*100)}%'
            )
        
        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel('High-order Entropy', fontsize=12)
        plt.title(f'Complexity Distribution Over Time ({len(runs)} runs)', 
                 fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_mutation_rate_heatmap(
        self,
        results: Dict[Tuple[float, int], int],
        mutation_rates: List[float],
        epoch_bins: List[int],
        save_path: Optional[str] = None
    ):
        """
        Plot heat map of mutation rate vs time to complexity.
        
        Replicates Figure 6 from the paper.
        
        Args:
            results: Dict mapping (mutation_rate, epoch_bin) to count
            mutation_rates: List of mutation rates tested
            epoch_bins: List of epoch bins
            save_path: Optional path to save figure
        """
        # Create matrix
        matrix = np.zeros((len(mutation_rates), len(epoch_bins)))
        for i, mr in enumerate(mutation_rates):
            for j, eb in enumerate(epoch_bins):
                matrix[i, j] = results.get((mr, eb), 0)
        
        # Normalize rows
        row_sums = matrix.sum(axis=1, keepdims=True)
        matrix = np.divide(matrix, row_sums, where=row_sums!=0)
        
        # Plot
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            matrix,
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            xticklabels=epoch_bins,
            yticklabels=[f'{mr:.3%}' for mr in mutation_rates],
            cbar_kws={'label': 'Fraction of runs'}
        )
        plt.xlabel('Epochs', fontsize=12)
        plt.ylabel('Mutation Rate', fontsize=12)
        plt.title('Distribution of Time to ≥ 1 Complexity', fontsize=14)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_complexity_histogram(
        self,
        datasets: Dict[str, List[float]],
        bins: int = 20,
        save_path: Optional[str] = None
    ):
        """
        Plot histogram comparison of final complexity.
        
        Replicates Figure 7 from the paper.
        
        Args:
            datasets: Dict mapping label to list of complexity values
            bins: Number of histogram bins
            save_path: Optional path to save figure
        """
        plt.figure(figsize=(12, 6))
        
        for label, values in datasets.items():
            plt.hist(values, bins=bins, alpha=0.6, label=label, edgecolor='black')
        
        plt.xlabel('High-order Entropy', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.title('Final Complexity Distribution Comparison', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_2d_grid(
        self,
        grid_soup: 'Grid2DSoup',
        save_path: Optional[str] = None
    ):
        """
        Visualize 2D spatial soup.
        
        Replicates Figure 8 from the paper.
        
        Args:
            grid_soup: Grid2DSoup instance
            save_path: Optional path to save figure
        """
        # Create color map based on program content
        # Use hash of first few bytes for color
        grid = np.zeros((grid_soup.height, grid_soup.width, 3))
        
        for i in range(grid_soup.height):
            for j in range(grid_soup.width):
                idx = i * grid_soup.width + j
                prog = grid_soup.programs[idx]
                
                # Simple hash to RGB
                hash_val = hash(tuple(prog.data[:4])) % (256**3)
                r = (hash_val >> 16) & 0xFF
                g = (hash_val >> 8) & 0xFF
                b = hash_val & 0xFF
                
                grid[i, j] = [r/255, g/255, b/255]
        
        plt.figure(figsize=(12, 8))
        plt.imshow(grid, interpolation='nearest')
        plt.title(f'2D Spatial Soup (Epoch {grid_soup.epoch})', fontsize=14)
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_token_statistics(
        self,
        history: List[Dict[str, any]],
        save_path: Optional[str] = None
    ):
        """
        Plot token tracking statistics over time.
        
        Replicates Figure 1 from the paper.
        
        Args:
            history: List of dicts with token statistics per epoch
            save_path: Optional path to save figure
        """
        epochs = [h['epoch'] for h in history]
        unique_tokens = [h['unique_tokens'] for h in history]
        complexity = [h['high_order_entropy'] for h in history]
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Plot unique tokens
        color = 'tab:blue'
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Unique Tokens', color=color, fontsize=12)
        ax1.plot(epochs, unique_tokens, color=color, linewidth=2)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_yscale('log')
        
        # Plot complexity on second y-axis
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('High-order Entropy', color=color, fontsize=12)
        ax2.plot(epochs, complexity, color=color, linewidth=2, linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title('Token Statistics and Complexity Over Time', fontsize=14)
        fig.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
```

#### Acceptance Criteria
- [ ] `SoupVisualizer` class implemented
- [ ] `plot_complexity_over_time()` creates line plot
- [ ] `plot_complexity_distribution()` creates quantile band plot (Figure 5)
- [ ] `plot_mutation_rate_heatmap()` creates heat map (Figure 6)
- [ ] `plot_complexity_histogram()` creates comparison histogram (Figure 7)
- [ ] `plot_2d_grid()` visualizes spatial soup (Figure 8)
- [ ] `plot_token_statistics()` shows token tracking (Figure 1)
- [ ] All plots support saving to file
- [ ] Consistent styling and color schemes
- [ ] Clear labels and titles
- [ ] Unit tests for:
  - [ ] Data format validation
  - [ ] Plot generation (smoke tests)
- [ ] Example notebook demonstrating all visualizations
- [ ] Test coverage ≥ 80%

#### Deliverables
- [ ] Implementation of all visualization methods
- [ ] Example Jupyter notebook: `notebooks/visualization_examples.ipynb`
- [ ] Documentation with example plots

#### Technical Notes
- Use matplotlib and seaborn for plotting
- Support both inline (Jupyter) and file-based outputs
- Consider animation support for 2D grid evolution (future enhancement)
- Optimize for large datasets (sampling if needed)

#### References
- Figures 1, 5, 6, 7, 8 throughout the paper

---

### Issue #7: Implement 2D Spatial Soup Variant

**Priority:** P2 (Medium)  
**Labels:** `core`, `bff`, `spatial`, `feature`  
**Estimated Effort:** 10 hours  
**Depends On:** #3

#### Description
Implement the 2D spatial variant of the primordial soup where programs can only interact with their neighbors. This creates spatially-structured dynamics and visible replicator waves.

#### Requirements from Paper
From Section 2.2, page 9-11:
- Grid dimensions: e.g., 240 × 135 = 32,400 programs
- Locality constraint: programs interact only if distance ≤ 2 in both coordinates
- Each epoch:
  - Iterate through programs in random order
  - For each program P, select random neighbor N
  - If neither marked as "taken", mark both and execute interaction
  - Apply same execution rule as standard soup

#### Implementation Details

**File:** `src/bff/spatial_soup.py`

```python
class Grid2DSoup(PrimordialSoup):
    """
    2D spatial primordial soup with locality constraints.
    
    Programs arranged in a 2D grid can only interact with neighbors,
    creating spatially-structured evolutionary dynamics.
    """
    
    def __init__(
        self,
        width: int = 240,
        height: int = 135,
        tape_length: int = 64,
        max_steps_per_execution: int = 2**13,
        mutation_rate: float = 0.00024,
        neighborhood_radius: int = 2,
        seed: Optional[int] = None
    ):
        """
        Initialize 2D spatial soup.
        
        Args:
            width: Grid width
            height: Grid height
            tape_length: Length of each program
            max_steps_per_execution: Max steps per execution
            mutation_rate: Background mutation rate
            neighborhood_radius: Max distance for interactions (default: 2)
            seed: Random seed
        """
        self.width = width
        self.height = height
        self.neighborhood_radius = neighborhood_radius
        
        soup_size = width * height
        super().__init__(soup_size, tape_length, max_steps_per_execution, 
                        mutation_rate, seed)
    
    def _get_coordinates(self, index: int) -> Tuple[int, int]:
        """Convert linear index to (x, y) coordinates."""
        return (index % self.width, index // self.width)
    
    def _get_index(self, x: int, y: int) -> int:
        """Convert (x, y) coordinates to linear index."""
        return y * self.width + x
    
    def _get_neighbors(self, index: int) -> List[int]:
        """
        Get list of neighbor indices within radius.
        
        Args:
            index: Program index
            
        Returns:
            List of neighbor indices
        """
        x, y = self._get_coordinates(index)
        neighbors = []
        
        for dx in range(-self.neighborhood_radius, self.neighborhood_radius + 1):
            for dy in range(-self.neighborhood_radius, self.neighborhood_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(self._get_index(nx, ny))
        
        return neighbors
    
    def run_epoch(self, interactions_per_epoch: Optional[int] = None):
        """
        Run one epoch with spatial constraints.
        
        Programs interact only with neighbors within the spatial locality radius.
        """
        # Mark which programs have been used this epoch
        taken = np.zeros(self.soup_size, dtype=bool)
        
        # Randomize order of program consideration
        program_order = self.rng.permutation(self.soup_size)
        
        for idx_p in program_order:
            if taken[idx_p]:
                continue
            
            # Get neighbors
            neighbors = self._get_neighbors(idx_p)
            if not neighbors:
                continue
            
            # Select random neighbor
            available_neighbors = [n for n in neighbors if not taken[n]]
            if not available_neighbors:
                continue
            
            idx_n = self.rng.choice(available_neighbors)
            
            # Mark as taken
            taken[idx_p] = True
            taken[idx_n] = True
            
            # Execute interaction
            self._interact(idx_p, idx_n)
        
        # Apply mutations (non-taken programs still get mutated)
        self._apply_mutations()
        
        self.epoch += 1
    
    def get_grid(self) -> np.ndarray:
        """
        Get 2D grid representation.
        
        Returns:
            3D array of shape (height, width, tape_length)
        """
        grid = np.zeros((self.height, self.width, self.tape_length), dtype=np.uint8)
        
        for i in range(self.soup_size):
            x, y = self._get_coordinates(i)
            grid[y, x] = self.programs[i].data
        
        return grid
    
    def visualize(self, save_path: Optional[str] = None):
        """Visualize current grid state."""
        from .visualization import SoupVisualizer
        viz = SoupVisualizer()
        viz.plot_2d_grid(self, save_path=save_path)
```

#### Acceptance Criteria
- [ ] `Grid2DSoup` class extending `PrimordialSoup`
- [ ] 2D grid structure with width × height programs
- [ ] Coordinate conversion methods (linear ↔ 2D)
- [ ] `_get_neighbors()` respects radius constraint
- [ ] `run_epoch()` implements spatial interaction rules:
  - [ ] Random program order
  - [ ] Neighbor selection from available neighbors
  - [ ] "Taken" marking prevents double interaction
- [ ] `get_grid()` returns 3D array representation
- [ ] Integration with visualization system
- [ ] Unit tests cover:
  - [ ] Grid initialization
  - [ ] Coordinate conversion
  - [ ] Neighbor calculation (corners, edges, center)
  - [ ] Spatial interaction constraints
  - [ ] Epoch execution
- [ ] Integration test: Run 1000 epochs and verify replicator emergence
- [ ] Test coverage ≥ 90%

#### Testing Requirements

**File:** `tests/test_spatial_soup.py`

```python
def test_grid_initialization():
    """Test 2D grid initialization."""
    soup = Grid2DSoup(width=10, height=10, seed=42)
    assert soup.soup_size == 100
    assert soup.width == 10
    assert soup.height == 10

def test_coordinate_conversion():
    """Test coordinate conversion."""
    soup = Grid2DSoup(width=10, height=10)
    
    # Test corners
    assert soup._get_coordinates(0) == (0, 0)
    assert soup._get_coordinates(9) == (9, 0)
    assert soup._get_coordinates(90) == (0, 9)
    assert soup._get_coordinates(99) == (9, 9)
    
    # Test round-trip
    for i in range(100):
        x, y = soup._get_coordinates(i)
        assert soup._get_index(x, y) == i

def test_neighbor_calculation():
    """Test neighbor calculation with radius."""
    soup = Grid2DSoup(width=10, height=10, neighborhood_radius=2)
    
    # Center cell (5, 5) should have 24 neighbors (5x5 - 1)
    neighbors = soup._get_neighbors(55)  # Index 55 = (5, 5)
    assert len(neighbors) == 24
    
    # Corner cell (0, 0) should have fewer neighbors
    neighbors_corner = soup._get_neighbors(0)
    assert len(neighbors_corner) < 24

def test_spatial_epoch_execution():
    """Test spatial epoch respects locality."""
    soup = Grid2DSoup(width=5, height=5, seed=42)
    
    # Track interactions
    soup.run_epoch()
    
    # Should have executed some interactions
    assert soup.epoch == 1
    assert soup.total_executions > 0
```

#### Performance Requirements
- [ ] Handle grids up to 240×135 efficiently
- [ ] Epoch execution time < 60 seconds for default grid size

#### Technical Notes
- Consider wrapping boundaries (toroidal topology) as optional feature
- Optimize neighbor calculation (can be precomputed)
- Profile memory usage for large grids

#### References
- Paper Section 2.2: "Spatial simulations", pages 9-11
- Figure 8: 2D BFF soup visualization, page 11

---

## Extended Features & Analysis Issues

### Issue #8: Implement Replicator Detection

**Priority:** P2 (Medium)  
**Labels:** `analysis`, `feature`, `detection`  
**Estimated Effort:** 12 hours  
**Depends On:** #4, #5

#### Description
Implement automated detection of self-replicators in the soup. While perfect detection is computationally intractable (as noted in the paper), implement heuristic-based detection methods.

#### Requirements
Detection strategies:
1. **Token-based**: Detect rapid proliferation of specific token patterns
2. **Complexity-based**: State transition via high-order entropy jump
3. **Pattern-based**: Look for specific instruction patterns (loops with copy operations)
4. **Execution-based**: Test candidate programs for self-replication behavior

#### Implementation Details

**File:** `src/bff/detection.py`

```python
class ReplicatorDetector:
    """
    Heuristic-based detection of self-replicating programs.
    
    Combines multiple detection strategies to identify candidate
    self-replicators in the soup.
    """
    
    def __init__(self, confidence_threshold: float = 0.8):
        """
        Initialize detector.
        
        Args:
            confidence_threshold: Minimum confidence for classification
        """
        self.confidence_threshold = confidence_threshold
    
    def detect_state_transition(
        self,
        complexity_history: List[float],
        window: int = 100
    ) -> Optional[int]:
        """
        Detect state transition epoch via complexity spike.
        
        Args:
            complexity_history: List of high-order entropy values
            window: Sliding window size for change detection
            
        Returns:
            Epoch of state transition, or None if not detected
        """
        if len(complexity_history) < window:
            return None
        
        # Look for rapid increase in complexity
        for i in range(window, len(complexity_history)):
            recent = complexity_history[i-window:i]
            current = complexity_history[i]
            
            mean_recent = np.mean(recent)
            std_recent = np.std(recent)
            
            # Detect spike: current value > mean + 3*std and > 1.0
            if current > mean_recent + 3 * std_recent and current > 1.0:
                return i
        
        return None
    
    def detect_by_token_proliferation(
        self,
        soup: 'TokenPrimordialSoup',
        threshold: float = 0.5
    ) -> List[int]:
        """
        Detect replicators by token proliferation.
        
        If a single token dominates > threshold of soup, it's likely
        from a successful replicator.
        
        Args:
            soup: TokenPrimordialSoup instance
            threshold: Fraction of soup required for detection
            
        Returns:
            List of dominant token IDs
        """
        from .tokens import TokenAnalyzer
        
        total_tokens = soup.soup_size * soup.tape_length
        top_tokens = TokenAnalyzer.top_tokens(soup, k=10)
        
        dominant = []
        for token, count in top_tokens:
            if count / total_tokens > threshold:
                dominant.append(token)
        
        return dominant
    
    def test_replication(
        self,
        program: BFFTape,
        num_tests: int = 10,
        success_threshold: float = 0.7
    ) -> bool:
        """
        Test if a program self-replicates.
        
        Concatenate program with random food programs and check if
        the first 64 bytes remain identical after execution.
        
        Args:
            program: Candidate replicator
            num_tests: Number of random tests
            success_threshold: Fraction of successful replications required
            
        Returns:
            True if program appears to be a replicator
        """
        successes = 0
        
        for _ in range(num_tests):
            # Create random food
            food = BFFTape.random(64)
            
            # Concatenate and execute
            combined = self._concatenate(program, food)
            interpreter = BFFInterpreter(combined, max_steps=2**13)
            result = interpreter.execute()
            
            # Check if first 64 bytes match original program
            if np.array_equal(result.data[:64], program.data):
                successes += 1
        
        return successes / num_tests >= success_threshold
    
    def find_replicator_patterns(
        self,
        soup: PrimordialSoup,
        min_occurrences: int = 100
    ) -> List[bytes]:
        """
        Find frequently occurring program patterns.
        
        Args:
            soup: PrimordialSoup instance
            min_occurrences: Minimum number of occurrences
            
        Returns:
            List of common program patterns
        """
        from collections import Counter
        
        # Count program occurrences
        program_counts = Counter(
            tuple(p.data) for p in soup.programs
        )
        
        # Return patterns exceeding threshold
        common = [
            bytes(prog) for prog, count in program_counts.items()
            if count >= min_occurrences
        ]
        
        return common
    
    def extract_replicator(
        self,
        program: BFFTape,
        min_length: int = 8
    ) -> Optional[bytes]:
        """
        Extract minimal replicating substring from program.
        
        Uses sliding window to find smallest self-replicating segment.
        
        Args:
            program: Full program tape
            min_length: Minimum replicator length to consider
            
        Returns:
            Minimal replicator bytes, or None if not found
        """
        # Try different substring lengths
        for length in range(min_length, len(program) + 1):
            for start in range(len(program) - length + 1):
                candidate = program.data[start:start+length]
                
                # Create tape with candidate
                test_tape = BFFTape(length=64)
                test_tape.data[:length] = candidate
                
                # Test replication
                if self.test_replication(test_tape, num_tests=5):
                    return bytes(candidate)
        
        return None
```

#### Acceptance Criteria
- [ ] `ReplicatorDetector` class implemented
- [ ] `detect_state_transition()` identifies complexity spikes
- [ ] `detect_by_token_proliferation()` uses token statistics
- [ ] `test_replication()` empirically tests self-replication
- [ ] `find_replicator_patterns()` identifies common programs
- [ ] `extract_replicator()` finds minimal replicating substring
- [ ] Unit tests cover:
  - [ ] State transition detection on synthetic data
  - [ ] Replication testing with known replicators
  - [ ] Pattern extraction
- [ ] Integration test: Detect replicators in example runs from paper
- [ ] Test coverage ≥ 85%

#### Technical Notes
- Combine multiple detection methods for robustness
- Trade-off between false positives and false negatives
- Consider computational cost of extensive testing

#### References
- Paper discussion on replicator detection challenges, pages 4-5

---

### Issue #9: Implement Experiment Runner & Batch Processing

**Priority:** P2 (Medium)  
**Labels:** `infrastructure`, `experiments`, `automation`  
**Estimated Effort:** 8 hours  
**Depends On:** #3, #4

#### Description
Implement experiment runner for batch execution of multiple simulation runs with different parameters. Enable reproduction of Figures 5, 6, 7 from the paper.

#### Implementation Details

**File:** `src/bff/experiments.py`

```python
class ExperimentRunner:
    """
    Run batches of simulation experiments with parameter sweeps.
    """
    
    def __init__(self, output_dir: str = "./results"):
        """
        Initialize experiment runner.
        
        Args:
            output_dir: Directory to save results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_single_experiment(
        self,
        config: Dict[str, Any],
        run_id: int
    ) -> Dict[str, Any]:
        """
        Run single simulation experiment.
        
        Args:
            config: Configuration dictionary
            run_id: Unique run identifier
            
        Returns:
            Results dictionary
        """
        # Create soup
        soup = PrimordialSoup(
            soup_size=config.get('soup_size', 2**17),
            tape_length=config.get('tape_length', 64),
            max_steps_per_execution=config.get('max_steps', 2**13),
            mutation_rate=config.get('mutation_rate', 0.00024),
            seed=config.get('seed', run_id)
        )
        
        # Track metrics over time
        history = []
        
        def collect_metrics(s, epoch):
            metrics = ComplexityMetrics.soup_complexity(s)
            history.append(metrics)
        
        # Run simulation
        num_epochs = config.get('num_epochs', 16000)
        soup.run(num_epochs, callback=collect_metrics)
        
        return {
            'run_id': run_id,
            'config': config,
            'history': history,
            'final_complexity': history[-1]['high_order_entropy'],
            'state_transition_epoch': self._detect_transition(history)
        }
    
    def _detect_transition(self, history: List[Dict]) -> Optional[int]:
        """Detect state transition epoch."""
        complexity = [h['high_order_entropy'] for h in history]
        detector = ReplicatorDetector()
        return detector.detect_state_transition(complexity)
    
    def run_parameter_sweep(
        self,
        base_config: Dict[str, Any],
        param_name: str,
        param_values: List[Any],
        num_runs_per_value: int = 100,
        n_jobs: int = -1
    ) -> pd.DataFrame:
        """
        Run parameter sweep experiment.
        
        Args:
            base_config: Base configuration
            param_name: Parameter name to vary
            param_values: List of parameter values to test
            num_runs_per_value: Number of runs per parameter value
            n_jobs: Number of parallel jobs (-1 for all cores)
            
        Returns:
            DataFrame with results
        """
        from joblib import Parallel, delayed
        
        configs = []
        for value in param_values:
            for run in range(num_runs_per_value):
                config = base_config.copy()
                config[param_name] = value
                config['run_id'] = f"{param_name}_{value}_{run}"
                configs.append(config)
        
        # Run in parallel
        results = Parallel(n_jobs=n_jobs, verbose=10)(
            delayed(self.run_single_experiment)(cfg, i)
            for i, cfg in enumerate(configs)
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Save results
        output_file = self.output_dir / f"sweep_{param_name}.pkl"
        df.to_pickle(output_file)
        
        return df
    
    def replicate_figure_5(
        self,
        num_runs: int = 1000,
        num_epochs: int = 16000,
        n_jobs: int = -1
    ) -> List[Dict]:
        """
        Replicate Figure 5: Complexity distribution over time.
        
        Args:
            num_runs: Number of simulation runs
            num_epochs: Number of epochs per run
            n_jobs: Number of parallel jobs
            
        Returns:
            List of run histories
        """
        base_config = {
            'soup_size': 2**17,
            'tape_length': 64,
            'max_steps': 2**13,
            'mutation_rate': 0.00024,
            'num_epochs': num_epochs
        }
        
        from joblib import Parallel, delayed
        
        results = Parallel(n_jobs=n_jobs, verbose=10)(
            delayed(self.run_single_experiment)(base_config, i)
            for i in range(num_runs)
        )
        
        # Save results
        output_file = self.output_dir / "figure_5_data.pkl"
        with open(output_file, 'wb') as f:
            pickle.dump(results, f)
        
        return [r['history'] for r in results]
    
    def replicate_figure_6(
        self,
        mutation_rates: List[float] = None,
        num_runs: int = 1000,
        num_epochs: int = 16000,
        n_jobs: int = -1
    ) -> pd.DataFrame:
        """
        Replicate Figure 6: Mutation rate sweep.
        """
        if mutation_rates is None:
            mutation_rates = [0.0, 0.00012, 0.00024, 0.00048, 0.001, 0.005, 0.01]
        
        base_config = {
            'soup_size': 2**17,
            'tape_length': 64,
            'max_steps': 2**13,
            'num_epochs': num_epochs
        }
        
        return self.run_parameter_sweep(
            base_config,
            'mutation_rate',
            mutation_rates,
            num_runs_per_value=num_runs // len(mutation_rates),
            n_jobs=n_jobs
        )
```

#### Acceptance Criteria
- [ ] `ExperimentRunner` class implemented
- [ ] `run_single_experiment()` executes one simulation with metrics
- [ ] `run_parameter_sweep()` supports parameter variations
- [ ] Parallel execution support (using joblib)
- [ ] Progress tracking for long-running experiments
- [ ] Results saved to disk (pickle/CSV format)
- [ ] `replicate_figure_5()` reproduces Figure 5 experiment
- [ ] `replicate_figure_6()` reproduces Figure 6 experiment
- [ ] Configuration management for reproducibility
- [ ] Unit tests for configuration handling
- [ ] Integration test: Run small parameter sweep
- [ ] Test coverage ≥ 85%

#### Deliverables
- [ ] Experiment runner implementation
- [ ] Example configuration files
- [ ] Documentation for running experiments
- [ ] Example notebook: `notebooks/run_experiments.ipynb`

#### Performance Requirements
- [ ] Support parallel execution on multiple cores
- [ ] Handle 1000+ runs efficiently
- [ ] Memory-efficient (don't keep all results in memory)

#### Technical Notes
- Use joblib for parallel processing
- Implement checkpointing for long experiments
- Consider using SQLite for result storage (alternative to pickle)

---

### Issue #10: Create Documentation and Examples

**Priority:** P3 (Low)  
**Labels:** `documentation`, `examples`  
**Estimated Effort:** 8 hours  
**Depends On:** #0-#9

#### Description
Create comprehensive documentation, tutorials, and example notebooks for the computational life simulator.

#### Deliverables

1. **README.md** - Updated with:
   - Project overview and motivation
   - Installation instructions
   - Quick start guide
   - Citation information for paper

2. **API Documentation** - Generated from docstrings:
   - Use Sphinx or similar
   - Host on Read the Docs or GitHub Pages

3. **Tutorial Notebooks**:
   - `01_basic_bff_programs.ipynb` - BFF language basics
   - `02_primordial_soup_intro.ipynb` - Running simple simulations
   - `03_detecting_replicators.ipynb` - Finding self-replicators
   - `04_complexity_analysis.ipynb` - Analyzing soup evolution
   - `05_spatial_simulations.ipynb` - 2D grid experiments
   - `06_reproducing_paper_results.ipynb` - Replicating paper figures

4. **Developer Guide**:
   - Architecture overview
   - Adding new languages (Forth, SUBLEQ examples)
   - Extending metrics
   - Contributing guidelines

#### Acceptance Criteria
- [ ] README with installation and quick start
- [ ] 6 tutorial notebooks fully implemented
- [ ] API documentation generated and hosted
- [ ] Developer guide written
- [ ] All code examples tested and working
- [ ] Links to paper and related resources
- [ ] Example output figures included

---

## Additional Enhancement Issues

### Issue #11: Implement Forth Language Support

**Priority:** P3 (Low)  
**Labels:** `feature`, `forth`, `language`  
**Estimated Effort:** 15 hours  
**Depends On:** #3, #4

#### Description
Implement Forth language variants as described in Section 3.1 of the paper. Both primordial soup and long-tape variants.

[Detailed implementation similar to Issues #1-#3 but for Forth]

---

### Issue #12: Implement Z80 CPU Emulation

**Priority:** P3 (Low)  
**Labels:** `feature`, `z80`, `emulation`  
**Estimated Effort:** 20 hours  
**Depends On:** #3

#### Description
Implement Z80 CPU emulation for real-world instruction set experiments (Section 3.3).

[Detailed implementation for Z80 emulator integration]

---

### Issue #13: Performance Optimization

**Priority:** P3 (Low)  
**Labels:** `optimization`, `performance`  
**Estimated Effort:** 15 hours  
**Depends On:** #0-#9

#### Description
Optimize performance of core simulation loop for large-scale experiments.

**Optimization Targets:**
- JIT compilation with Numba
- Vectorized operations with NumPy
- Cython for interpreter hot path
- Memory pooling for tape objects
- Parallel execution improvements

---

### Issue #14: Web Interface

**Priority:** P4 (Optional)  
**Labels:** `ui`, `web`, `feature`  
**Estimated Effort:** 30 hours  
**Depends On:** #0-#9

#### Description
Create interactive web interface for running simulations and visualizing results in real-time.

**Features:**
- Live soup visualization
- Parameter controls
- Real-time metrics display
- Export results
- Share simulation URLs

**Tech Stack:**
- Backend: FastAPI
- Frontend: React + D3.js
- Real-time: WebSockets

---

## Summary

This comprehensive set of issues provides a complete roadmap for implementing the computational life simulator from the paper. The issues are:

1. **Prioritized** (P0-P4) for logical development order
2. **Estimated** for time planning
3. **Dependent** showing clear prerequisites
4. **Testable** with specific acceptance criteria
5. **Documented** with references to the paper

**Development Phases:**

- **Phase 1 (P0):** Core BFF implementation (#0-#3)
- **Phase 2 (P1-P2):** Metrics, visualization, detection (#4-#9)
- **Phase 3 (P3):** Extended features, documentation (#10-#13)
- **Phase 4 (P4):** Optional enhancements (#14)

**Total Estimated Effort:** ~150 hours for core implementation (P0-P2)

Each issue can be directly converted into a GitHub issue with labels, milestones, and assignments for team collaboration.