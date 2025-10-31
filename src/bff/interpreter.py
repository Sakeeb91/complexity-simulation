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
        self.bracket_map = self._build_bracket_map()

    def _build_bracket_map(self) -> Dict[int, int]:
        """
        Build a mapping of bracket positions for O(1) jumps.

        Returns:
            Dictionary mapping [ positions to ] positions and vice versa

        Raises:
            ValueError: If brackets are unmatched
        """
        bracket_map = {}
        stack = []

        for i in range(len(self.tape)):
            instruction = self.tape[i]

            if instruction == ord('['):
                stack.append(i)
            elif instruction == ord(']'):
                if not stack:
                    raise ValueError(f"Unmatched closing bracket at position {i}")
                opening = stack.pop()
                # Map opening to closing and closing to opening
                bracket_map[opening] = i
                bracket_map[i] = opening

        if stack:
            raise ValueError(f"Unmatched opening bracket at position {stack[0]}")

        return bracket_map

    def _execute_instruction(self, instruction: int) -> None:
        """
        Execute a single instruction byte.

        Args:
            instruction: The instruction byte to execute
        """
        # Head movement instructions
        if instruction == ord('<'):
            self.head0 = (self.head0 - 1) % len(self.tape)
        elif instruction == ord('>'):
            self.head0 = (self.head0 + 1) % len(self.tape)
        elif instruction == ord('{'):
            self.head1 = (self.head1 - 1) % len(self.tape)
        elif instruction == ord('}'):
            self.head1 = (self.head1 + 1) % len(self.tape)
        # Value modification instructions
        elif instruction == ord('-'):
            current_value = self.tape[self.head0]
            self.tape[self.head0] = (current_value - 1) % 256
        elif instruction == ord('+'):
            current_value = self.tape[self.head0]
            self.tape[self.head0] = (current_value + 1) % 256
        # Copy operations
        elif instruction == ord('.'):
            # Copy from head0 to head1
            self.tape[self.head1] = self.tape[self.head0]
        elif instruction == ord(','):
            # Copy from head1 to head0
            self.tape[self.head0] = self.tape[self.head1]
        # Loop/conditional jump instructions
        elif instruction == ord('['):
            # If tape[head0] == 0, jump to matching ]
            if self.tape[self.head0] == 0:
                if self.pc in self.bracket_map:
                    self.pc = self.bracket_map[self.pc]
                else:
                    # Unmatched bracket - terminate
                    self.terminated = True
        elif instruction == ord(']'):
            # If tape[head0] != 0, jump to matching [
            if self.tape[self.head0] != 0:
                if self.pc in self.bracket_map:
                    self.pc = self.bracket_map[self.pc]
                else:
                    # Unmatched bracket - terminate
                    self.terminated = True
