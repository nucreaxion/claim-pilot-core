from claim_pilot_core.core.exceptions import (
    ClaimNotFoundError,
    ClaimPilotError,
    DatabaseError,
    PolicyNotFoundError,
    ToolExecutionError,
    ValidationError,
)


def test_base_exception():
    err = ClaimPilotError("something went wrong", code="TEST_ERROR")
    assert err.message == "something went wrong"
    assert err.code == "TEST_ERROR"
    d = err.to_dict()
    assert d["error"] == "TEST_ERROR"
    assert d["message"] == "something went wrong"


def test_database_error():
    err = DatabaseError("connection refused")
    assert err.code == "DATABASE_ERROR"


def test_tool_execution_error():
    err = ToolExecutionError("policy_search", "timeout")
    assert "policy_search" in err.message
    assert err.tool_name == "policy_search"


def test_validation_error():
    err = ValidationError("invalid policy_id", field="policy_id")
    assert err.field == "policy_id"


def test_not_found_errors():
    err = PolicyNotFoundError("AUTO-999")
    assert err.code == "POLICY_NOT_FOUND"
    assert err.resource_id == "AUTO-999"

    err = ClaimNotFoundError("CLM-999")
    assert err.code == "CLAIM_NOT_FOUND"
