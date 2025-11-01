"""Token tracking system for BFF programs.

This module implements the "radioactive tracer" token system that allows
tracking the origin and propagation of bytes through the soup. Each byte
has an associated token containing (epoch, position, char) information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple

import numpy as np

from .tape import BFFTape


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


class TokenTape(BFFTape):
    """
    Extended BFF tape with token tracking.

    Each byte has an associated token that tracks its origin.
    Tokens are stored as uint64 values in a parallel array.
    """

    def __init__(self, length: int = 64, data: Optional[np.ndarray] = None,
                 tokens: Optional[np.ndarray] = None):
        """
        Initialize token tape.

        Args:
            length: Tape length
            data: Optional initial data (uint8 array)
            tokens: Optional initial tokens (uint64 array)
        """
        super().__init__(length, data)

        if tokens is None:
            # Create tokens initialized to zero
            self.tokens = np.zeros(length, dtype=np.uint64)
        else:
            if len(tokens) != length:
                raise ValueError("tokens length must match tape length")
            self.tokens = tokens.copy()

    def __setitem__(self, index: int, value: int):
        """
        Set byte and update token char only.

        This preserves the token's epoch and position.
        """
        super().__setitem__(index, value)
        # Update char in existing token
        idx = index % len(self)
        if self.tokens[idx] != 0:
            token = Token.from_uint64(self.tokens[idx])
            token.char = value
            self.tokens[idx] = token.to_uint64()

    @property
    def data(self) -> np.ndarray:
        """Access underlying data array."""
        return self._data

    def copy(self) -> 'TokenTape':
        """Create a deep copy of the token tape."""
        return TokenTape(length=len(self), data=self._data.copy(),
                        tokens=self.tokens.copy())
