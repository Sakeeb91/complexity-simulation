"""Core Brainfuck-Fusion interpreter primitives.

This module will host the execution engine for BFF programs, including state
management, instruction dispatch, and integration hooks for the primordial
soup simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class BFFInstruction:
    """Lightweight representation of a single BFF instruction."""

    opcode: str
    argument: int | None = None


class BFFInterpreter:
    """Execute Brainfuck-Fusion bytecode against a tape structure.

    The implementation will be fleshed out in Issue #2 and subsequent tasks.
    """

    def __init__(self) -> None:
        self._instructions: List[BFFInstruction] = []

    def load(self, instructions: Iterable[BFFInstruction]) -> None:
        """Load a sequence of instructions into the interpreter."""

        self._instructions = list(instructions)

    def run(self) -> None:
        """Execute the loaded program. Placeholder until Issue #3 delivers the runtime."""

        raise NotImplementedError("Execution engine planned for Issue #3")
