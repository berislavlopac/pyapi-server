from jsonschema_path import SchemaPath

from pyapi.server.spec import OperationSpec


def test_OperationSpec_get_all_creates_dict_of_operations(spec_dict):
    spec = SchemaPath.from_dict(spec_dict)
    operation_ids = (
        "dummyTestEndpoint",
        "dummyPostEndpoint",
        "dummyTestEndpointWithArgument",
        "dummyTestEndpointCoro",
    )
    operations = OperationSpec.get_all(spec)
    assert sorted(operations) == sorted(operation_ids)


def test_OperationSpec_groups_parameters_by_type(spec_dict):
    operations = OperationSpec.get_all(SchemaPath.from_dict(spec_dict))
    operation = operations["dummyTestEndpointWithArgument"]
    assert hasattr(operation, "parameters")
    assert "test_arg" in operation.parameters["path"]
