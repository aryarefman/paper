import pytest
from src.core.lattice import PermissionLevel, PermissionLattice, ToolSchema

def test_permission_level_ordering():
    p1 = PermissionLevel.LEVEL_1_READ_SINGLE
    p2 = PermissionLevel.LEVEL_2_READ_BATCH
    p4 = PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

    assert p2.subsumes(p1)
    assert p4.strictly_subsumes(p2)
    assert not p1.strictly_subsumes(p2)

def test_lattice_find_least_sufficient_tool():
    tools = [
        ToolSchema(
            name="get_single_record",
            description="Reads one record",
            permission_level=PermissionLevel.LEVEL_1_READ_SINGLE,
            domain="database",
            target_entity="single_record",
            parameters={}
        ),
        ToolSchema(
            name="query_all_records",
            description="Queries whole db",
            permission_level=PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED,
            domain="database",
            target_entity="single_record",
            parameters={}
        )
    ]
    lattice = PermissionLattice(tools)

    # When LEVEL_1 is required, it must pick get_single_record
    least_tool = lattice.find_least_sufficient_tool(
        domain="database",
        target_entity="single_record",
        required_level=PermissionLevel.LEVEL_1_READ_SINGLE
    )
    assert least_tool is not None
    assert least_tool.name == "get_single_record"
