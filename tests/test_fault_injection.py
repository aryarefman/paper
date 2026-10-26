import pytest
from src.core.fault_simulator import FaultSimulator

def test_fault_simulator_triggers_transient_fault():
    sim = FaultSimulator(failure_rate=1.0, seed=42)  # Always inject
    has_fault, resp = sim.simulate_execution("get_user_account_balance", {"user_id": "123"}, is_minimal_tool=True)
    assert has_fault is True
    assert resp["code"] == 504
    assert resp["error_type"] == "GatewayTimeout"

def test_fault_simulator_non_minimal_tool_never_faults():
    sim = FaultSimulator(failure_rate=1.0, seed=42)
    # Admin tools do not trigger transient faults in the testbed
    has_fault, resp = sim.simulate_execution("query_entire_financial_database", {"user_id": "123"}, is_minimal_tool=False)
    assert has_fault is False
    assert resp["code"] == 200
