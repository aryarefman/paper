import pytest
from src.core.lattice import PermissionLevel, PermissionLattice, ToolSchema

def test_permission_level_ordering():
    p1 = PermissionLevel.LEVEL_1_READ_SINGLE
    p2 = PermissionLevel.LEVEL_2_READ_BATCH
    p4 = PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

    assert p2.subsumes(p1)
    assert p4.strictly_subsumes(p2)
    assert not p1.strictly_subsumes(p2)

def test_lattice_capability_preserving_downgrade():
    tools = [
        ToolSchema(
            name="get_user_account_balance",
            description="Reads one user balance",
            permission_level=PermissionLevel.LEVEL_1_READ_SINGLE,
            domain="database",
            capability="financial_balance",
            parameters={}
        ),
        ToolSchema(
            name="lookup_student_transcript",
            description="Reads student transcript",
            permission_level=PermissionLevel.LEVEL_1_READ_SINGLE,
            domain="database",
            capability="academic_transcript",
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
    lattice = PermissionLattice(tools)

    # When financial_balance is requested, it must pick get_user_account_balance, NOT transcript!
    least_tool = lattice.find_least_sufficient_tool(
        domain="database",
        required_capability="financial_balance",
        required_level=PermissionLevel.LEVEL_1_READ_SINGLE
    )
    assert least_tool is not None
    assert least_tool.name == "get_user_account_balance"

    # When academic_transcript is requested, it must pick lookup_student_transcript
    transcript_tool = lattice.find_least_sufficient_tool(
        domain="database",
        required_capability="academic_transcript",
        required_level=PermissionLevel.LEVEL_1_READ_SINGLE
    )
    assert transcript_tool is not None
    assert transcript_tool.name == "lookup_student_transcript"
