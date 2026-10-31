from shipping_quote import process_shipments, monitor_container_pressures


def test_empty_shipments_list():
    result = process_shipments([], 20.0)
    assert result == {
        "total_quote": 0.0,
        "status": "NO_CARGO"
    }


def test_approved_shipment_with_no_packages():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "packages": []
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result == {
        "total_quote": 10.0,
        "status": "CLEARED"
    }


def test_approved_shipment_using_default_values():
    shipments = [
        {
            "manifest_approved": True
        }
    ]
    result = process_shipments(shipments, 0.0)
    assert result == {
        "total_quote": 0.0,
        "status": "NO_CARGO"
    }


def test_container_with_empty_pressure_readings():
    result = monitor_container_pressures([[]])
    assert result == "STABLE"


def test_multiple_containers_with_stable_pressures():
    pressure_logs = [
        [15.0, 16.0, 17.0],
        [18.0, 15.0, 16.0]
    ]
    assert monitor_container_pressures(pressure_logs) == "STABLE"


def test_pressure_drop_resets_after_normal_reading():
    pressure_logs = [
        [13.0, 15.0, 13.0, 13.0]
    ]
    assert monitor_container_pressures(pressure_logs) == "LEAK_DETECTED"