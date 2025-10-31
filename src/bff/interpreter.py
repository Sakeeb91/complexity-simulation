"""Core Brainfuck-Fusion interpreter primitives.

This module implements the execution engine for BFF programs, including state
management, instruction dispatch, and integration hooks for the primordial
soup simulation.
"""

from __future__ import annotations

from typing import Dict

from .tape import BFFTape


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
        self.bracket_map: Dict[int, int] = {}
