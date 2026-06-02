from src.domain.orders import build_order_summary


def test_build_order_summary_rejects_empty_id() -> None:
    try:
        build_order_summary("", status="paid", total_cents=4200)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
