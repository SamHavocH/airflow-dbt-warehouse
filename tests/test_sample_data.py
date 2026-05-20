from scripts.sample_data import build_customers, build_events, build_orders, build_products


def test_sample_data_contains_expected_business_entities() -> None:
    assert len(build_customers()) >= 5
    assert len(build_products()) >= 5
    assert len(build_orders()) > 100
    assert len(build_events()) > 300


def test_orders_include_duplicate_versions_for_deduplication_demo() -> None:
    orders = build_orders()
    order_ids = [row["order_id"] for row in orders]

    assert len(order_ids) > len(set(order_ids))
