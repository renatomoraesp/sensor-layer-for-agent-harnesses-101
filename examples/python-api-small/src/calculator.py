def divide(left: float, right: float) -> float:
    if right == 0:
        raise ValueError("cannot divide by zero")
    return left / right
