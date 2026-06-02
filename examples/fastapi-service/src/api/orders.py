from src.persistence.orders import load_order_summary


def get_order_summary_response(order_id: str) -> dict[str, str | int]:
    summary = load_order_summary(order_id)
    return {
        "order_id": summary.order_id,
        "status": summary.status,
        "total_cents": summary.total_cents,
    }
