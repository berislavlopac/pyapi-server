import pytest
from openapi_core.validation.exceptions import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from pyapi.server import Application


async def _dummy_receive():
    return {"type": "http.request"}


def _prepare(app, path):
    global _dummy_receive

    for route in app.routes:
        if route.path == path:
            break

    request_scope = {
        "type": "http",
        "root_path": app.spec["servers"][0]["url"],
        "path": route.path,
        "query_string": "",
        "headers": {},
        "app": app,
        "method": "get",
    }
    request = Request(request_scope, _dummy_receive)
    return route, request


@pytest.mark.asyncio
async def test_server_wraps_endpoint_function_result_with_jsonresponse(spec_dict, config):
    path = "/test"
    app = Application(spec_dict, module=config.endpoint_base)

    route, request = _prepare(app, path)

    response = await route.endpoint(request)
    assert isinstance(response, JSONResponse)


@pytest.mark.asyncio
async def test_server_wraps_async_endpoint_function_result_with_jsonresponse(spec_dict, config):
    path = "/test_asyncio"
    app = Application(spec_dict, module=config.endpoint_base)

    route, request = _prepare(app, path)

    response = await route.endpoint(request)
    assert isinstance(response, JSONResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize("response_value", (("sdfsdfsfds"), 1234, [1, 2, 3]))
async def test_server_raises_error_when_endpoint_response_is_not_response_or_dict(
    spec_dict, config, monkeypatch, response_value
):
    from . import endpoints

    monkeypatch.setattr(endpoints, "dummy_test_endpoint", lambda request: response_value)

    path = "/test"
    app = Application(spec_dict, module=config.endpoint_base)

    route, request = _prepare(app, path)

    with pytest.raises(TypeError):
        await route.endpoint(request)


@pytest.mark.asyncio
async def test_server_raises_error_on_invalid_endpoint_function_response(
    spec_dict, config, monkeypatch
):
    from . import endpoints

    monkeypatch.setattr(endpoints, "dummy_test_endpoint", lambda request: JSONResponse(""))

    path = "/test"
    app = Application(spec_dict, module=config.endpoint_base)

    route, request = _prepare(app, path)

    with pytest.raises(ValidationError):
        await route.endpoint(request)


@pytest.mark.asyncio
async def test_server_skips_response_validation_for_declared_operation_id(
    spec_dict, config, monkeypatch
):
    from . import endpoints

    monkeypatch.setattr(endpoints, "dummy_test_endpoint", lambda request: JSONResponse(""))

    path = "/test"
    app = Application(
        spec_dict, module=config.endpoint_base, skip_response_validation=["dummy_test_endpoint"]
    )

    route, request = _prepare(app, path)

    response = await route.endpoint(request)
    assert isinstance(response, JSONResponse)
