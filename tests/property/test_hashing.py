"""Property tests for source hashing."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from grand_strategy_lab.cli import sha256_bytes


@pytest.mark.property
@given(st.binary())
def test_hash_is_deterministic_and_hex64(data: bytes) -> None:
    digest = sha256_bytes(data)
    assert digest == sha256_bytes(data)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)
