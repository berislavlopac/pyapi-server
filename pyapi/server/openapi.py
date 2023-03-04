"""OpenAPI request and response wrappers; adapted from openapi-core."""
from asyncio import ensure_future, get_running_loop, run
from typing import Optional

from openapi_core.validation.request.datatypes import RequestParameters
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import JSONResponse, Response  # noqa: F401


class OpenAPIRequest:
    """Wrapper for PyAPI Server requests."""

    def __init__(self, request: Request):
        self.request = request
        self._body: Optional[dict] = None
        self.parameters = RequestParameters(
            query=self.request.query_params,
            header=self.request.headers,
            cookie=self.request.cookies,
            path=self.request.path_params,
        )

        body_coroutine = self.request.json()
        try:
            loop = get_running_loop()
        except RuntimeError:
            self._body = run(body_coroutine)
        else:
            task = ensure_future(body_coroutine, loop=loop)
            task.add_done_callback(lambda fut: self._set_body(fut.result()))

    def _set_body(self, value):
        self._body = value

    @property
    def host_url(self) -> str:
        """Return the request host url."""
        return self.request.base_url._url

    @property
    def path(self) -> str:
        """Return the request path."""
        return self.request.url.path

    @property
    def method(self) -> str:
        """Return the request HTTP method."""
        return self.request.method.lower()

    @property
    def body(self) -> Optional[str]:
        """Return the request body as string, if present."""
        body = self._body
        if isinstance(body, bytes):
            return body.decode("utf-8")
        assert body is None or isinstance(body, str)
        return body

    @property
    def mimetype(self) -> str:
        """Return the request content type."""
        content_type = self.request.headers["Content-Type"]
        if content_type:
            return content_type.partition(";")[0]

        return ""


class OpenAPIResponse:
    """Wrapper for PyAPI Server responses."""

    def __init__(self, response: Response):
        self.response = response

    @property
    def data(self) -> str:
        """Return the response content as string."""
        if isinstance(self.response.body, bytes):
            return self.response.body.decode("utf-8")
        assert isinstance(self.response.body, str)
        return self.response.body

    @property
    def status_code(self) -> int:
        """Return the response HTTP status code."""
        return self.response.status_code

    @property
    def mimetype(self) -> str:
        """Return the response content type."""
        return self.response.media_type or ""

    @property
    def headers(self) -> Headers:
        """Return the response headers."""
        return self.response.headers
