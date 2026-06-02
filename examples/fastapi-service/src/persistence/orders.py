from src.domain.orders import OrderSummary, build_order_summary

_ORDERS = {
    "ord_123": {"status": "paid", "total_cents": 4200},
    "ord_404": {"status": "missing", "total_cents": 0},
}


def load_order_summary(order_id: str) -> OrderSummary:
    row = _ORDERS.get(order_id)
    if row is None:
        raise KeyError(order_id)
    return build_order_summary(
        order_id,
        status=str(row["status"]),
        total_cents=int(row["total_cents"]),
    )
