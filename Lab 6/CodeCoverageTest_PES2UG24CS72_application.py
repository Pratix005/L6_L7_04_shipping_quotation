
import pytest
from shipping_quote import process_shipments, monitor_container_pressures


def test_invalid_shipments():
    with pytest.raises(ValueError):
        process_shipments("invalid", 10.0)


def test_negative_handling_fee():
    with pytest.raises(ValueError):
        process_shipments([], -5.0)


def test_unapproved_manifest():
    result = process_shipments(
        [{"manifest_approved": False, "packages": []}], 10.0
    )
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_air_shipment():
    shipments = [{
        "manifest_approved": True,
        "mode": "air",
        "packages": [{"weight_kg": 10, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 130.0
    assert result["status"] == "CLEARED"


def test_unsupported_transport_mode():
    shipments = [{
        "manifest_approved": True,
        "mode": "sea",
        "packages": []
    }]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "NO_CARGO"


def test_invalid_package_weight():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [
            {"weight_kg": 0},
            {"weight_kg": 2}
        ]
    }]
    result = process_shipments(shipments, 5.0)
    assert result["total_quote"] == 13.0
    assert result["status"] == "CLEARED"


def test_hazmat_non_fragile():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "is_fragile": False,
        "packages": [
            {"weight_kg": 1, "is_hazmat": True}
        ]
    }]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 60.0
    assert result["status"] == "CLEARED"


def test_hazmat_fragile():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "is_fragile": True,
        "express_priority": True,
        "packages": [
            {"weight_kg": 5, "is_hazmat": True},
            {"weight_kg": 10, "is_hazmat": False}
        ]
    }]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 0.0
    assert result["status"] == "NO_CARGO"


def test_heavy_package():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 40, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 250.0
    assert result["status"] == "CLEARED"


def test_express_priority():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "express_priority": True,
        "packages": [{"weight_kg": 10, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 75.0
    assert result["status"] == "CLEARED"


def test_flagged_review():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "packages": [{"weight_kg": 0}]
        }
        for _ in range(4)
    ]
    result = process_shipments(shipments, 0.0)
    assert result == {
        "total_quote": 0.0,
        "status": "FLAGGED_REVIEW"
    }


def test_empty_pressure_logs():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_leak_detection():
    logs = [[15.0, 13.0, 12.0]]
    assert monitor_container_pressures(logs) == "LEAK_DETECTED"


def test_pressure_stable_after_reset():
    logs = [[13.0, 14.0, 13.0, 15.0]]
    assert monitor_container_pressures(logs) == "STABLE"


def test_multiple_stable_containers():
    logs = [
        [13.0],
        [15.0, 13.0, 16.0]
    ]
    assert monitor_container_pressures(logs) == "STABLE"
