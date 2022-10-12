import pytest
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
async def test_server_raises_error_on_invalid_endpoint_function_response(
    spec_dict, config, monkeypatch
):
    from . import endpoints

    monkeypatch.setattr(endpoints, "dummy_test_endpoint", lambda request: "sdfsdfsfds")

    path = "/test"
    app = Application(spec_dict, module=config.endpoint_base)

    route, request = _prepare(app, path)

    with pytest.raises(ValueError):
        await route.endpoint(request)
