"""Primordial soup simulation interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Organism:
    """Represents an organism instance in the simulation space."""

    genome: bytes
    energy: float


class PrimordialSoup:
    """Container for the self-replicating program ecosystem."""

    def __init__(self) -> None:
        self._organisms: list[Organism] = []

    def seed(self, organisms: Iterable[Organism]) -> None:
        """Add initial organisms to the soup."""

        self._organisms.extend(organisms)

    def step(self) -> None:
        """Advance the simulation one tick. Detailed mechanics arrive in Issue #3."""

        raise NotImplementedError("Simulation mechanics planned for Issue #3")
