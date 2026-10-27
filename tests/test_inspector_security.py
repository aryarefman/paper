import pytest
from src.core.lattice import PermissionLevel, PermissionLattice, ToolSchema
from src.core.inspector import ParameterScopeInspector
from src.core.verifier import LeastPrivilegeVerifier

def test_inspector_detects_shell_command():
    # Vulnerability check: ls / must not be classified as LEVEL_1
    args = {"command": "ls /"}
    level = ParameterScopeInspector.infer_required_scope(args)
    assert level == PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

def test_inspector_detects_raw_sql_query():
    # Vulnerability check: SELECT * FROM must be classified as LEVEL_4
    args = {"query": "SELECT * FROM accounts"}
    level = ParameterScopeInspector.infer_required_scope(args)
    assert level == PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

def test_inspector_detects_department_code_injection():
    # Vulnerability check: SQL injection in department_code must not pass as legitimate batch
    args = {"department_code": "' OR '1'='1"}
    level = ParameterScopeInspector.infer_required_scope(args)
    assert level == PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

def test_inspector_legitimate_department_code():
    args = {"department_code": "IF"}
    level = ParameterScopeInspector.infer_required_scope(args)
    assert level == PermissionLevel.LEVEL_2_READ_BATCH

def test_inspector_singular_entity_id():
    args = {"user_id": "5025201048"}
    level = ParameterScopeInspector.infer_required_scope(args)
    assert level == PermissionLevel.LEVEL_1_READ_SINGLE

def test_verifier_blocks_argument_smuggling():
    # If agent invokes a LEVEL_1 tool with a LEVEL_4 command payload, verifier must block
    tools = [
        ToolSchema(
            name="get_user_account_balance",
            description="Reads single balance",
            permission_level=PermissionLevel.LEVEL_1_READ_SINGLE,
            domain="database",
            capability="financial_balance",
            parameters={}
        )
    ]
    verifier = LeastPrivilegeVerifier(PermissionLattice(tools))
    final_tool, final_args, v_res = verifier.verify_and_route(
        candidate_tool_name="get_user_account_balance",
        arguments={"command": "cat /etc/passwd"}
    )
    assert v_res.was_blocked is True
    assert final_tool == "get_user_account_balance"
    assert "Privilege mismatch" in v_res.reason

def test_verifier_independent_of_benchmark_labels():
    # Verifier operates without passing domain and capability ground truth
    tools = [
        ToolSchema(
            name="get_user_account_balance",
            description="Reads single balance",
            permission_level=PermissionLevel.LEVEL_1_READ_SINGLE,
            domain="database",
            capability="financial_balance",
            parameters={}
        ),
        ToolSchema(
            name="query_entire_financial_database",
            description="Queries whole db",
            permission_level=PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED,
            domain="database",
            capability="financial_balance",
            parameters={}
        )
    ]
    verifier = LeastPrivilegeVerifier(PermissionLattice(tools))
    final_tool, final_args, v_res = verifier.verify_and_route(
        candidate_tool_name="query_entire_financial_database",
        arguments={"user_id": "1001"}
    )
    assert v_res.was_downgraded is True
    assert final_tool == "get_user_account_balance"
