"""Primordial soup simulation for BFF programs.

This module implements the core simulation environment where random BFF programs
interact through concatenation and execution, following the Turing gas variant
from Fontana (1990) as adapted in the paper.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np
from tqdm import tqdm

from .interpreter import BFFInterpreter
from .tape import BFFTape


class PrimordialSoup:
    """
    Primordial soup simulator for BFF programs.

    Implements the Turing gas variant from Fontana (1990) adapted
    for BFF programs as described in the paper. Programs interact
    through concatenation and execution:

        A + B --exec--> split(exec(AB)) = A' + B'

    This creates a self-organizing system where self-replicators can
    emerge and dominate the soup.
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
        if soup_size <= 0:
            raise ValueError("soup_size must be positive")
        if tape_length <= 0:
            raise ValueError("tape_length must be positive")
        if max_steps_per_execution <= 0:
            raise ValueError("max_steps_per_execution must be positive")
        if mutation_rate < 0 or mutation_rate > 1:
            raise ValueError("mutation_rate must be in range [0, 1]")

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

        An epoch consists of a number of random pair interactions
        followed by background mutations.

        Args:
            interactions_per_epoch: Number of random pair interactions
                                   (default: soup_size)
        """
        if interactions_per_epoch is None:
            interactions_per_epoch = self.soup_size

        for _ in range(interactions_per_epoch):
            # Select random ordered pair (without replacement)
            i, j = self.rng.choice(self.soup_size, size=2, replace=False)

            # Execute interaction
            self._interact(i, j)

        # Apply background mutations
        self._apply_mutations()

        self.epoch += 1

    def _interact(self, idx_a: int, idx_b: int):
        """
        Perform interaction between two programs.

        The interaction follows: A + B --exec--> A' + B'
        where A' and B' are the first and second halves of exec(AB).

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

        # Split and return to soup
        new_a, new_b = self._split(result)
        self.programs[idx_a] = new_a
        self.programs[idx_b] = new_b

        self.total_executions += 1

    def _concatenate(self, tape_a: BFFTape, tape_b: BFFTape) -> BFFTape:
        """
        Concatenate two tapes into a single tape.

        Args:
            tape_a: First tape
            tape_b: Second tape

        Returns:
            New tape with contents of tape_a followed by tape_b
        """
        # Get underlying data from both tapes
        data_a = tape_a._data
        data_b = tape_b._data

        # Concatenate
        combined_data = np.concatenate([data_a, data_b])

        # Create new tape with combined length
        return BFFTape(length=len(tape_a) + len(tape_b), data=combined_data)

    def _split(self, tape: BFFTape) -> Tuple[BFFTape, BFFTape]:
        """
        Split tape into two equal parts.

        If the tape length is odd, the first tape gets the extra byte.

        Args:
            tape: Tape to split

        Returns:
            Tuple of (first_half, second_half)
        """
        total_length = len(tape)
        split_point = total_length // 2

        # Get first and second halves
        first_data = tape._data[:split_point]
        second_data = tape._data[split_point:2*split_point]

        # Create new tapes
        tape_a = BFFTape(length=split_point, data=first_data)
        tape_b = BFFTape(length=split_point, data=second_data)

        return tape_a, tape_b

    def _apply_mutations(self):
        """
        Apply random mutations to the soup.

        Each byte has a mutation_rate probability of being randomly
        changed to a different value.
        """
        if self.mutation_rate <= 0:
            return

        # Calculate total number of bytes in soup
        total_bytes = self.soup_size * self.tape_length

        # Generate mutations
        num_mutations = self.rng.binomial(total_bytes, self.mutation_rate)

        if num_mutations == 0:
            return

        # Select random positions to mutate
        for _ in range(num_mutations):
            # Select random program
            prog_idx = self.rng.integers(0, self.soup_size)
            # Select random byte in program
            byte_idx = self.rng.integers(0, self.tape_length)
            # Assign random new value
            new_value = self.rng.integers(0, 256)

            self.programs[prog_idx][byte_idx] = new_value

    def run(self, num_epochs: int, callback: Optional[Callable[[PrimordialSoup, int], None]] = None):
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
        """
        Get current state snapshot for analysis.

        Returns:
            Dictionary containing current soup state
        """
        return {
            'epoch': self.epoch,
            'soup_size': self.soup_size,
            'tape_length': self.tape_length,
            'programs': [p.copy() for p in self.programs],
            'total_executions': self.total_executions
        }
