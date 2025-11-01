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
from .interpreter import BFFInterpreter


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
        Set byte value.

        Note: This does NOT update the token. Tokens are only updated
        by the TokenInterpreter during execution (for +/- operations).
        """
        super().__setitem__(index, value)

    @property
    def data(self) -> np.ndarray:
        """Access underlying data array."""
        return self._data

    def copy(self) -> 'TokenTape':
        """Create a deep copy of the token tape."""
        return TokenTape(length=len(self), data=self._data.copy(),
                        tokens=self.tokens.copy())

    def copy_with_token(self, src_idx: int, dst_idx: int):
        """
        Copy byte and token from src to dst.

        This is used by the BFF copy instructions (. and ,) to
        propagate both data and origin information.

        Args:
            src_idx: Source index
            dst_idx: Destination index
        """
        src_idx = src_idx % len(self)
        dst_idx = dst_idx % len(self)
        self._data[dst_idx] = self._data[src_idx]
        self.tokens[dst_idx] = self.tokens[src_idx]

    @classmethod
    def random(cls, length: int = 64, epoch: int = 0,
               program_idx: int = 0, seed: Optional[int] = None) -> 'TokenTape':
        """
        Create random tape with unique tokens.

        Each byte is initialized with a unique token containing:
        - epoch: The current epoch number
        - position: program_idx * length + byte_idx (unique global position)
        - char: The random byte value

        Args:
            length: Tape length
            epoch: Current epoch (for token creation)
            program_idx: Program index in soup (for unique positions)
            seed: Random seed for reproducibility

        Returns:
            TokenTape with random data and unique tokens
        """
        rng = np.random.default_rng(seed)
        data = rng.integers(0, 256, size=length, dtype=np.uint8)

        # Create unique tokens for each byte
        tokens = np.zeros(length, dtype=np.uint64)
        for i in range(length):
            position = program_idx * length + i
            token = Token(epoch, position, int(data[i]))
            tokens[i] = token.to_uint64()

        return cls(length, data, tokens)


class TokenInterpreter(BFFInterpreter):
    """
    BFF interpreter with token tracking.

    Extends the base BFFInterpreter to track token propagation
    through copy operations and preserve token origins through
    increment/decrement operations.
    """

    def __init__(self, tape: TokenTape, max_steps: int = 2**13):
        """
        Initialize with a TokenTape.

        Args:
            tape: The TokenTape to execute on
            max_steps: Maximum number of instructions to execute

        Raises:
            TypeError: If tape is not a TokenTape instance
        """
        if not isinstance(tape, TokenTape):
            raise TypeError("TokenInterpreter requires TokenTape")
        super().__init__(tape, max_steps)

    def _execute_instruction(self, instruction: int) -> None:
        """
        Execute instruction with token tracking.

        Token propagation rules:
        - Copy operations (. and ,) copy both data and tokens
        - Increment/decrement (+/-) preserve token origin, update char only
        - All other operations don't affect tokens

        Args:
            instruction: The instruction byte to execute
        """
        # Check for copy operations that need token tracking
        if instruction == ord('.'):
            # Copy from head0 to head1 (including token)
            self.tape.copy_with_token(self.head0, self.head1)
        elif instruction == ord(','):
            # Copy from head1 to head0 (including token)
            self.tape.copy_with_token(self.head1, self.head0)
        elif instruction == ord('+') or instruction == ord('-'):
            # Increment/decrement operations preserve token origin
            idx = self.head0 % len(self.tape)
            current_value = int(self.tape.data[idx])  # Convert to Python int

            if instruction == ord('+'):
                new_value = (current_value + 1) % 256
            else:  # ord('-')
                new_value = (current_value - 1) % 256

            # Update data and token char (preserving epoch/position)
            self.tape.data[idx] = np.uint8(new_value)
            if self.tape.tokens[idx] != 0:
                token = Token.from_uint64(self.tape.tokens[idx])
                token.char = new_value
                self.tape.tokens[idx] = token.to_uint64()
        else:
            # Other instructions don't affect tokens, use base implementation
            super()._execute_instruction(instruction)


class TokenAnalyzer:
    """
    Analyze token statistics in a soup.

    Provides methods for analyzing token diversity, finding popular tokens,
    and understanding self-replicator emergence through token tracking.
    """

    @staticmethod
    def count_unique_tokens(programs: List[TokenTape]) -> int:
        """
        Count unique tokens across all programs in the soup.

        Args:
            programs: List of TokenTape instances

        Returns:
            Number of unique tokens
        """
        if not programs:
            return 0

        all_tokens = np.concatenate([p.tokens for p in programs])
        return len(np.unique(all_tokens))

    @staticmethod
    def top_tokens(programs: List[TokenTape], k: int = 32) -> List[Tuple[int, int]]:
        """
        Get the k most common tokens.

        Args:
            programs: List of TokenTape instances
            k: Number of top tokens to return

        Returns:
            List of (token, count) tuples sorted by count descending
        """
        if not programs:
            return []

        all_tokens = np.concatenate([p.tokens for p in programs])
        unique, counts = np.unique(all_tokens, return_counts=True)

        # Sort by count descending
        sorted_indices = np.argsort(-counts)

        return [(int(unique[i]), int(counts[i])) for i in sorted_indices[:k]]

    @staticmethod
    def token_diversity(programs: List[TokenTape]) -> float:
        """
        Calculate token diversity (unique tokens / total tokens).

        This metric helps detect self-replicator emergence. When a self-replicator
        dominates the soup, token diversity drops significantly as the same tokens
        propagate through many programs.

        Args:
            programs: List of TokenTape instances

        Returns:
            Diversity value between 0 and 1 (1 = all tokens unique, 0 = all same)
        """
        if not programs:
            return 0.0

        total_tokens = sum(len(p) for p in programs)
        unique_tokens = TokenAnalyzer.count_unique_tokens(programs)

        if total_tokens == 0:
            return 0.0

        return unique_tokens / total_tokens

    @staticmethod
    def decode_token(token_value: int) -> Tuple[int, int, int]:
        """
        Decode a packed token value into its components.

        Args:
            token_value: Packed uint64 token

        Returns:
            Tuple of (epoch, position, char)
        """
        token = Token.from_uint64(token_value)
        return (token.epoch, token.position, token.char)
