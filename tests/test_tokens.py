"""Tests for the token tracking system."""

import numpy as np
import pytest

from src.bff.tokens import Token, TokenTape, TokenInterpreter, TokenAnalyzer


class TestToken:
    """Test Token dataclass and packing/unpacking."""

    def test_token_packing(self):
        """Test token packing/unpacking preserves values."""
        token = Token(epoch=100, position=50000, char=42)
        packed = token.to_uint64()
        unpacked = Token.from_uint64(packed)

        assert unpacked.epoch == 100
        assert unpacked.position == 50000
        assert unpacked.char == 42

    def test_token_packing_edge_cases(self):
        """Test token packing with edge case values."""
        # Max values within bit ranges
        token = Token(epoch=0xFFFFF, position=0xFFFFFF, char=255)
        packed = token.to_uint64()
        unpacked = Token.from_uint64(packed)

        assert unpacked.epoch == 0xFFFFF
        assert unpacked.position == 0xFFFFFF
        assert unpacked.char == 255

    def test_token_packing_zero(self):
        """Test token packing with all zeros."""
        token = Token(epoch=0, position=0, char=0)
        packed = token.to_uint64()
        unpacked = Token.from_uint64(packed)

        assert unpacked.epoch == 0
        assert unpacked.position == 0
        assert unpacked.char == 0
        assert packed == 0

    def test_copy_with_char(self):
        """Test copy_with_char preserves epoch and position."""
        token = Token(epoch=100, position=50000, char=42)
        new_token = token.copy_with_char(99)

        assert new_token.epoch == 100
        assert new_token.position == 50000
        assert new_token.char == 99

    def test_copy_with_char_wrapping(self):
        """Test copy_with_char handles char overflow."""
        token = Token(epoch=100, position=50000, char=42)
        # 256 should wrap to 0
        new_token = token.copy_with_char(256)

        assert new_token.char == 0


class TestTokenTape:
    """Test TokenTape class."""

    def test_token_tape_creation(self):
        """Test basic token tape creation."""
        tape = TokenTape(length=10)

        assert len(tape) == 10
        assert len(tape.tokens) == 10
        assert tape.tokens.dtype == np.uint64

    def test_token_tape_with_data(self):
        """Test token tape creation with initial data."""
        data = np.array([1, 2, 3, 4, 5], dtype=np.uint8)
        tape = TokenTape(length=5, data=data)

        assert len(tape) == 5
        assert tape[0] == 1
        assert tape[4] == 5

    def test_token_tape_with_tokens(self):
        """Test token tape creation with initial tokens."""
        data = np.array([1, 2, 3], dtype=np.uint8)
        tokens = np.array([100, 200, 300], dtype=np.uint64)
        tape = TokenTape(length=3, data=data, tokens=tokens)

        assert tape.tokens[0] == 100
        assert tape.tokens[1] == 200
        assert tape.tokens[2] == 300

    def test_token_tape_setitem_updates_char(self):
        """Test that __setitem__ updates token char."""
        tape = TokenTape(length=5)
        # Set initial token
        tape.tokens[0] = Token(epoch=10, position=20, char=30).to_uint64()

        # Update value
        tape[0] = 99

        # Token should have updated char
        token = Token.from_uint64(tape.tokens[0])
        assert token.epoch == 10
        assert token.position == 20
        assert token.char == 99

    def test_copy_with_token(self):
        """Test copy_with_token propagates both data and tokens."""
        tape = TokenTape(length=10)
        tape.data[0] = 42
        tape.tokens[0] = Token(epoch=5, position=100, char=42).to_uint64()

        tape.copy_with_token(0, 5)

        assert tape.data[5] == 42
        assert tape.tokens[5] == tape.tokens[0]

    def test_copy_with_token_wrapping(self):
        """Test copy_with_token with index wrapping."""
        tape = TokenTape(length=5)
        tape.data[0] = 99
        original_token = Token(epoch=1, position=2, char=99).to_uint64()
        tape.tokens[0] = original_token

        # Copy with wrapping indices
        tape.copy_with_token(0, 7)  # 7 % 5 = 2

        assert tape.data[2] == 99
        assert tape.tokens[2] == original_token

    def test_random_token_tape(self):
        """Test random token tape creation with unique tokens."""
        tape = TokenTape.random(length=64, epoch=0, program_idx=5, seed=42)

        # All tokens should be unique
        assert len(np.unique(tape.tokens)) == 64

        # Check one token has correct structure
        token = Token.from_uint64(tape.tokens[0])
        assert token.epoch == 0
        assert 320 <= token.position < 384  # 5 * 64 + [0-64)

    def test_random_token_tape_different_programs(self):
        """Test tokens are unique across different programs."""
        tape1 = TokenTape.random(length=10, epoch=0, program_idx=0, seed=42)
        tape2 = TokenTape.random(length=10, epoch=0, program_idx=1, seed=43)

        # Tokens should be different (different positions)
        token1 = Token.from_uint64(tape1.tokens[0])
        token2 = Token.from_uint64(tape2.tokens[0])

        assert token1.position != token2.position

    def test_token_tape_copy(self):
        """Test token tape copy creates independent copy."""
        tape1 = TokenTape.random(length=10, epoch=0, program_idx=0, seed=42)
        tape2 = tape1.copy()

        # Modify tape2
        tape2[0] = 123

        # tape1 should be unchanged
        assert tape1[0] != 123
        # But tokens should be preserved
        assert len(tape2.tokens) == 10


class TestTokenInterpreter:
    """Test TokenInterpreter class."""

    def test_token_interpreter_requires_token_tape(self):
        """Test that TokenInterpreter requires TokenTape."""
        from src.bff.tape import BFFTape
        regular_tape = BFFTape(length=10)

        with pytest.raises(TypeError):
            TokenInterpreter(regular_tape)

    def test_token_interpreter_copy_instruction(self):
        """Test token interpreter handles . (copy) instruction."""
        tape = TokenTape(length=128)
        tape.data[0] = 42
        tape.tokens[0] = Token(epoch=0, position=0, char=42).to_uint64()

        # Program: . (copy from head0 to head1)
        tape[1] = ord('.')

        interpreter = TokenInterpreter(tape)
        interpreter.head0 = 0
        interpreter.head1 = 10
        interpreter.pc = 1
        interpreter.step()

        # Token should be copied
        assert tape.tokens[10] == tape.tokens[0]
        assert tape.data[10] == 42

    def test_token_interpreter_reverse_copy_instruction(self):
        """Test token interpreter handles , (reverse copy) instruction."""
        tape = TokenTape(length=128)
        tape.data[10] = 99
        tape.tokens[10] = Token(epoch=5, position=10, char=99).to_uint64()

        # Program: , (copy from head1 to head0)
        tape[1] = ord(',')

        interpreter = TokenInterpreter(tape)
        interpreter.head0 = 0
        interpreter.head1 = 10
        interpreter.pc = 1
        interpreter.step()

        # Token should be copied
        assert tape.tokens[0] == tape.tokens[10]
        assert tape.data[0] == 99

    def test_token_interpreter_increment_preserves_origin(self):
        """Test that + preserves token origin."""
        tape = TokenTape(length=128)
        original_token = Token(epoch=100, position=200, char=5).to_uint64()
        tape.tokens[0] = original_token
        tape.data[0] = 5

        # Program: + (increment)
        tape[1] = ord('+')

        interpreter = TokenInterpreter(tape)
        interpreter.head0 = 0
        interpreter.pc = 1
        interpreter.step()

        # Data should be incremented
        assert tape.data[0] == 6

        # Token should preserve epoch/position but update char
        token = Token.from_uint64(tape.tokens[0])
        assert token.epoch == 100
        assert token.position == 200
        assert token.char == 6

    def test_token_interpreter_decrement_preserves_origin(self):
        """Test that - preserves token origin."""
        tape = TokenTape(length=128)
        original_token = Token(epoch=100, position=200, char=10).to_uint64()
        tape.tokens[0] = original_token
        tape.data[0] = 10

        # Program: - (decrement)
        tape[1] = ord('-')

        interpreter = TokenInterpreter(tape)
        interpreter.head0 = 0
        interpreter.pc = 1
        interpreter.step()

        # Data should be decremented
        assert tape.data[0] == 9

        # Token should preserve epoch/position but update char
        token = Token.from_uint64(tape.tokens[0])
        assert token.epoch == 100
        assert token.position == 200
        assert token.char == 9

    def test_token_interpreter_other_instructions(self):
        """Test that other instructions don't affect tokens."""
        tape = TokenTape(length=128)
        original_token = Token(epoch=1, position=2, char=3).to_uint64()
        tape.tokens[0] = original_token

        # Program: > (move head0 right)
        tape[0] = ord('>')

        interpreter = TokenInterpreter(tape)
        interpreter.step()

        # Token should be unchanged
        assert tape.tokens[0] == original_token


class TestTokenAnalyzer:
    """Test TokenAnalyzer class."""

    def test_count_unique_tokens(self):
        """Test counting unique tokens."""
        tape1 = TokenTape.random(length=10, epoch=0, program_idx=0, seed=42)
        tape2 = TokenTape.random(length=10, epoch=0, program_idx=1, seed=43)

        count = TokenAnalyzer.count_unique_tokens([tape1, tape2])

        # Should have 20 unique tokens (all different)
        assert count == 20

    def test_count_unique_tokens_with_duplicates(self):
        """Test counting unique tokens with duplicates."""
        tape1 = TokenTape(length=5)
        tape2 = TokenTape(length=5)

        # Set same token in multiple positions
        shared_token = Token(epoch=0, position=0, char=42).to_uint64()
        tape1.tokens[0] = shared_token
        tape1.tokens[1] = shared_token
        tape2.tokens[0] = shared_token

        count = TokenAnalyzer.count_unique_tokens([tape1, tape2])

        # Should count the zero tokens and the one shared token
        assert count == 2  # 0 and shared_token

    def test_count_unique_tokens_empty(self):
        """Test counting unique tokens with empty list."""
        count = TokenAnalyzer.count_unique_tokens([])
        assert count == 0

    def test_top_tokens(self):
        """Test finding top tokens."""
        tape1 = TokenTape(length=10)
        tape2 = TokenTape(length=10)

        # Create tokens with different frequencies
        token1 = Token(epoch=1, position=1, char=1).to_uint64()
        token2 = Token(epoch=2, position=2, char=2).to_uint64()

        # token1 appears 5 times
        for i in range(5):
            tape1.tokens[i] = token1

        # token2 appears 3 times
        for i in range(3):
            tape2.tokens[i] = token2

        top = TokenAnalyzer.top_tokens([tape1, tape2], k=3)

        # Should be sorted by count
        assert len(top) >= 2
        # Most common should be token1 with count 5
        assert top[0][0] == token1
        assert top[0][1] == 5

    def test_top_tokens_empty(self):
        """Test top_tokens with empty list."""
        top = TokenAnalyzer.top_tokens([], k=10)
        assert top == []

    def test_token_diversity_all_unique(self):
        """Test token diversity when all tokens are unique."""
        tape1 = TokenTape.random(length=10, epoch=0, program_idx=0, seed=42)
        tape2 = TokenTape.random(length=10, epoch=0, program_idx=1, seed=43)

        diversity = TokenAnalyzer.token_diversity([tape1, tape2])

        # All 20 tokens should be unique
        assert diversity == 1.0

    def test_token_diversity_all_same(self):
        """Test token diversity when all tokens are the same."""
        tape1 = TokenTape(length=10)
        tape2 = TokenTape(length=10)

        shared_token = Token(epoch=0, position=0, char=42).to_uint64()
        tape1.tokens[:] = shared_token
        tape2.tokens[:] = shared_token

        diversity = TokenAnalyzer.token_diversity([tape1, tape2])

        # Only 1 unique token out of 20
        assert diversity == 1.0 / 20.0

    def test_token_diversity_empty(self):
        """Test token diversity with empty list."""
        diversity = TokenAnalyzer.token_diversity([])
        assert diversity == 0.0

    def test_decode_token(self):
        """Test decoding packed token."""
        token = Token(epoch=100, position=50000, char=42)
        packed = token.to_uint64()

        epoch, position, char = TokenAnalyzer.decode_token(packed)

        assert epoch == 100
        assert position == 50000
        assert char == 42
