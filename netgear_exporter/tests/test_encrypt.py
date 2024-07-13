"""Unit tests for netgear password encryption"""

from ..connector import _encrypt_password


def test_encrypt() -> None:
    """Test encryption"""

    rand = "1450459452"
    password = "foobar"
    expected = "6e80d4621bd4aadbf2ce5e2c04d9a487"

    assert _encrypt_password(password, rand) == expected
