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
            target_entity="single_record",
            parameters={}
        ),
        ToolSchema(
            name="query_entire_financial_database",
            description="Broad SQL query",
            permission_level=PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED,
            domain="database",
            target_entity="single_record",
            parameters={}
        )
    ]
    return PermissionLattice(tools)

def test_verifier_automatic_downgrade(sample_lattice):
    verifier = LeastPrivilegeVerifier(sample_lattice)

    # Agent proposed the over-privileged tool, but arguments only supply a single user ID
    final_tool, final_args, v_res = verifier.verify_and_route(
        candidate_tool_name="query_entire_financial_database",
        arguments={"user_id": "5025201048"},
        domain="database",
        target_entity="single_record"
    )

    assert v_res.was_downgraded is True
    assert final_tool == "get_user_account_balance"
    assert v_res.executed_permission == PermissionLevel.LEVEL_1_READ_SINGLE
