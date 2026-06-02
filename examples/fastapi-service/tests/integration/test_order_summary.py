from src.api.orders import get_order_summary_response


def test_get_order_summary_response() -> None:
    response = get_order_summary_response("ord_123")

    assert response == {
        "order_id": "ord_123",
        "status": "paid",
        "total_cents": 4200,
    }
