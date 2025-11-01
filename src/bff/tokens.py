"""Token tracking system for BFF programs.

This module implements the "radioactive tracer" token system that allows
tracking the origin and propagation of bytes through the soup. Each byte
has an associated token containing (epoch, position, char) information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple

import numpy as np


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
        """
        Pack token into 64-bit integer.

        Uses 20 bits for epoch, 24 bits for position, 20 bits for char.
        This allows:
        - Up to ~1M epochs
        - Up to ~16M positions (256 programs * 64K tape length)
        - Full 256 char values with headroom

        Returns:
            Packed 64-bit integer representation
        """
        # Ensure values fit in their bit ranges
        epoch = self.epoch & 0xFFFFF  # 20 bits
        position = self.position & 0xFFFFFF  # 24 bits
        char = self.char & 0xFF  # 8 bits (but stored in 20-bit field)

        return (epoch << 44) | (position << 20) | char

    @classmethod
    def from_uint64(cls, value: int) -> 'Token':
        """
        Unpack token from 64-bit integer.

        Args:
            value: Packed 64-bit integer

        Returns:
            Token instance with unpacked values
        """
        epoch = (value >> 44) & 0xFFFFF
        position = (value >> 20) & 0xFFFFFF
        char = value & 0xFF  # Only use lower 8 bits for char
        return cls(epoch, position, char)

    def copy_with_char(self, new_char: int) -> 'Token':
        """
        Create copy with updated char (for +/- operations).

        This preserves the token's origin (epoch, position) while
        updating only the character value.

        Args:
            new_char: New character value (0-255)

        Returns:
            New Token instance with updated char
        """
        return Token(self.epoch, self.position, new_char & 0xFF)
