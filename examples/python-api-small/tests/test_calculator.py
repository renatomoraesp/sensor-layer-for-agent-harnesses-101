from src.calculator import divide


def test_divide_returns_quotient() -> None:
    assert divide(6, 2) == 3


def test_divide_rejects_zero() -> None:
    try:
        divide(1, 0)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
