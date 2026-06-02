from app.services import get_order_summary


def order_summary(order_id: str) -> dict[str, str]:
    return get_order_summary(order_id)
