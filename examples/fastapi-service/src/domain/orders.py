from dataclasses import dataclass


@dataclass(frozen=True)
class OrderSummary:
    order_id: str
    status: str
    total_cents: int


def build_order_summary(order_id: str, *, status: str, total_cents: int) -> OrderSummary:
    if not order_id:
        raise ValueError("order_id is required")
    return OrderSummary(order_id=order_id, status=status, total_cents=total_cents)
