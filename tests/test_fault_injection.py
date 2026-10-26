import pytest
from src.core.fault_simulator import FaultSimulator, TransientFaultError

def test_fault_simulator_triggers_transient_error():
    sim = FaultSimulator(failure_rate=1.0)  # Always fail
    with pytest.raises(TransientFaultError) as exc_info:
        sim.execute_with_fault_injection("get_user_account_balance", {"user_id": "123"})
    assert "504 Gateway Timeout" in str(exc_info.value)

def test_fault_simulator_success_rate():
    sim = FaultSimulator(failure_rate=0.0)  # Never fail
    res = sim.execute_with_fault_injection("get_user_account_balance", {"user_id": "123"})
    assert res["status"] == "success"
