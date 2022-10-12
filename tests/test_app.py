from inspect import iscoroutinefunction

import pytest

from pyapi.server import Application


@pytest.mark.parametrize("filename", ("openapi.json", "openapi.yaml"))
def test_app_is_created_from_file_path(config, filename):
    file_path = config.test_dir / filename
    app = Application.from_file(file_path, module=config.endpoint_base)
    assert app.spec["info"]["title"] == "Test Spec"


def test_app_raises_error_if_file_path_is_of_unknown_type(config):
    file_path = config.test_dir / "openapi.unknown"
    with pytest.raises(RuntimeError):
        Application.from_file(file_path)


def test_additional_path_on_server_url_adds_routes_with_prefix(spec_dict):
    from tests import endpoints

    spec_dict["servers"].insert(0, {"url": "http://localhost:8001/with/path"})
    app = Application(spec_dict, module=endpoints)
    expected_routes = {
        "/test",
        "/test-async",
        "/test/{test_arg}",
        "/with/path/test",
        "/with/path/test/{test_arg}",
        "/with/path/test-async",
    }
    assert {route.path for route in app.routes} == expected_routes


def test_app_raises_error_if_endpoints_cannot_be_found(spec_dict):
    with pytest.raises(RuntimeError):
        Application(spec_dict, module="foo.bar")


def test_app_raises_error_if_an_endpoint_function_is_missing(spec_dict, config):
    spec_dict["paths"]["/test"]["get"]["operationId"] = "fooBar"
    with pytest.raises(RuntimeError):
        Application(spec_dict, module=config.endpoint_base)


def test_app_attaches_correct_endpoint_function(spec_dict, config):
    from .endpoints import dummy_test_endpoint

    app = Application(spec_dict, module=config.endpoint_base)
    route = app.routes[0]
    assert route.endpoint is not dummy_test_endpoint
    assert route.endpoint.__wrapped__ is dummy_test_endpoint
    assert not iscoroutinefunction(dummy_test_endpoint)
    assert iscoroutinefunction(route.endpoint)
