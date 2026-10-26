import pytest
from src.core.lattice import PermissionLevel, PermissionLattice, ToolSchema
from src.core.verifier import LeastPrivilegeVerifier

@pytest.fixture
def sample_lattice():
    tools = [
        ToolSchema(
            name="get_user_account_balance",
            description="Read single user balance",
            permission_level=PermissionLevel.LEVEL_1_READ_SINGLE,
            domain="database",
            capability="financial_balance",
            parameters={}
        ),
        ToolSchema(
            name="lookup_student_transcript",
            description="Read transcript",
            permission_level=PermissionLevel.LEVEL_1_READ_SINGLE,
            domain="database",
            capability="academic_transcript",
            parameters={}
        ),
        ToolSchema(
            name="query_entire_financial_database",
            description="Broad SQL query",
            permission_level=PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED,
            domain="database",
            capability="financial_balance",
            parameters={}
        )
    ]
    return PermissionLattice(tools)

def test_verifier_automatic_downgrade(sample_lattice):
    verifier = LeastPrivilegeVerifier(sample_lattice)

    # Over-privileged financial tool proposed with single ID argument
    final_tool, final_args, v_res = verifier.verify_and_route(
        candidate_tool_name="query_entire_financial_database",
        arguments={"user_id": "5025201048"},
        domain="database",
        required_capability="financial_balance"
    )

    assert v_res.was_downgraded is True
    assert final_tool == "get_user_account_balance"
    assert v_res.executed_permission == PermissionLevel.LEVEL_1_READ_SINGLE

def test_verifier_prevents_wrong_capability_cross_downgrade(sample_lattice):
    verifier = LeastPrivilegeVerifier(sample_lattice)

    # Transcript query should never be downgraded to account balance tool!
    final_tool, final_args, v_res = verifier.verify_and_route(
        candidate_tool_name="lookup_student_transcript",
        arguments={"student_id": "5025211020"},
        domain="database",
        required_capability="academic_transcript"
    )

    assert final_tool == "lookup_student_transcript"
    assert v_res.was_downgraded is False
