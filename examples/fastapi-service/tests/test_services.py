from app.services import get_order_summary


def test_get_order_summary_returns_status() -> None:
    assert get_order_summary("ord_123")["status"] == "example"
