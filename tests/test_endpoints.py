from inspect import iscoroutinefunction

import pytest

from pyapi.server import Application


def test_endpoints_are_defined_as_named_module_with_dotted_name(spec_dict):
    spec_dict["paths"]["/test"]["get"]["operationId"] = "endpoints.dummyTestEndpoint"
    spec_dict["paths"]["/test"]["post"]["operationId"] = "endpoints.dummyPostEndpoint"
    spec_dict["paths"]["/test/{test_arg}"]["get"]["operationId"] = (
        "endpoints.dummyTestEndpointWithArgument"
    )
    spec_dict["paths"]["/test-async"]["get"]["operationId"] = "endpoints.dummyTestEndpointCoro"
    app = Application(spec_dict, module="tests")
    route = app.routes[0]
    assert callable(route.endpoint)
    assert route.endpoint.__name__ == "dummy_test_endpoint"
    assert route.path == "/test"


def test_endpoints_are_defined_as_imported_module(spec_dict):
    from tests import endpoints

    app = Application(spec_dict, module=endpoints)
    route = app.routes[0]
    assert callable(route.endpoint)
    assert route.endpoint.__name__ == "dummy_test_endpoint"
    assert route.path == "/test"


def test_endpoints_are_defined_as_imported_module_with_dotted_names(spec_dict):
    import tests

    spec_dict["paths"]["/test"]["get"]["operationId"] = "endpoints.dummyTestEndpoint"
    spec_dict["paths"]["/test"]["post"]["operationId"] = "endpoints.dummyPostEndpoint"
    spec_dict["paths"]["/test/{test_arg}"]["get"]["operationId"] = (
        "endpoints.dummyTestEndpointWithArgument"
    )
    spec_dict["paths"]["/test-async"]["get"]["operationId"] = "endpoints.dummyTestEndpointCoro"
    app = Application(spec_dict, module=tests)
    route = app.routes[0]
    assert callable(route.endpoint)
    assert route.endpoint.__name__ == "dummy_test_endpoint"
    assert route.path == "/test"


def test_endpoint_decorator_determines_endpoint_from_function_name(spec_dict):
    app = Application(spec_dict)
    assert app.routes == []

    @app.endpoint
    def dummy_test_endpoint(request):
        return {}

    route = app.routes[0]
    assert route.endpoint is not dummy_test_endpoint
    assert route.endpoint.__wrapped__ is dummy_test_endpoint
    assert not iscoroutinefunction(dummy_test_endpoint)
    assert iscoroutinefunction(route.endpoint)


def test_endpoint_decorator_determines_endpoint_by_given_operation_id(spec_dict):
    operation_id = "dummyTestEndpoint"
    app = Application(spec_dict)
    assert app.routes == []

    @app.endpoint(operation_id)
    def foo_bar(request):
        return {}

    route = app.routes[0]
    operation = app._operations[operation_id]
    assert route.path.endswith(operation.path)
    assert operation.method.upper() in route.methods
    assert route.endpoint is not foo_bar
    assert route.endpoint.__wrapped__ is foo_bar
    assert not iscoroutinefunction(foo_bar)
    assert iscoroutinefunction(route.endpoint)


def test_endpoint_decorator_with_incorrect_operation_id_raises_error(spec_dict):
    operation_id = "iDontExist"
    app = Application(spec_dict)
    assert app.routes == []

    with pytest.raises(ValueError) as ex:

        @app.endpoint(operation_id)
        def foo_bar(request):
            return {}

        assert str(ex) == f"ValueError: Unknown operationId: {operation_id}."


def test_set_endpoint_method_determines_endpoint_from_function_name(spec_dict):
    from .endpoints import dummy_test_endpoint

    app = Application(spec_dict)
    assert app.routes == []

    app.set_endpoint(dummy_test_endpoint)

    route = app.routes[0]
    assert route.endpoint is not dummy_test_endpoint
    assert route.endpoint.__wrapped__ is dummy_test_endpoint
    assert not iscoroutinefunction(dummy_test_endpoint)
    assert iscoroutinefunction(route.endpoint)
