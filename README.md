# Complexity Simulation

Computational life simulator inspired by *Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction* (Agüera y Arcas et al., 2024). The project explores how self-replicating programs evolve when subject to selective pressures inside a primordial soup of interacting Brainfuck-Fusion (BFF) organisms.

## Project Goals
- Implement a Brainfuck-Fusion interpreter and tape structure.
- Model a primordial soup environment where digital organisms compete, replicate, and mutate.
- Track complexity and entropy metrics to understand emergent behaviour.
- Provide tooling for experiments, visualization, and alternative execution substrates (Forth, Z80).

## Repository Layout
```
src/
  bff/        # Interpreter, soup, metrics (primary simulation core)
  forth/      # Planned Forth runtime integration (Issue #11)
  z80/        # Planned Z80 CPU emulation (Issue #12)
  utils/      # Shared helpers
notebooks/    # Research notebooks and exploratory analysis
visualizations/ # Plotting utilities and rendered artefacts
data/         # Input datasets and experiment results
tests/        # Automated test suite
```

## Getting Started
1. Create and activate a Python 3.8+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the package in editable mode if you plan to contribute code:
   ```bash
   pip install -e .
   ```
4. Run the test suite:
   ```bash
   pytest
   ```

## Roadmap
Development tasks are tracked as GitHub issues. Start with Issue #0 for repository scaffolding and proceed in numerical order to flesh out the simulator.

## License
This project is licensed under the terms of the [MIT License](LICENSE).
