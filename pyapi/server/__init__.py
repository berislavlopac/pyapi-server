"""PyAPI Server."""

from __future__ import annotations

from functools import wraps
from http import HTTPStatus
from importlib import import_module
from inspect import iscoroutine
from logging import getLogger
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, cast, Mapping, Optional, Union
from urllib.parse import urlsplit

from jsonschema_path import SchemaPath
from openapi_core import validate_request, validate_response
from openapi_core.exceptions import OpenAPIError
from openapi_core.security.exceptions import SecurityProviderError
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from stringcase import snakecase

from .spec import get_spec_from_file, OperationSpec
from .validation import JSONResponse, OpenAPIRequest, OpenAPIResponse, Request, Response

log = getLogger(__name__)


class Application(Starlette):
    """PyAPI server application."""

    def __init__(
        self,
        spec: Union[SchemaPath, dict],
        *,
        module: Optional[Union[str, ModuleType]] = None,
        validate_responses: bool = True,
        enforce_case: bool = True,
        custom_format_validators: Optional[Mapping[str, Callable]] = None,
        spec_url: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        if isinstance(spec, dict):
            spec = SchemaPath.from_dict(spec, base_uri=spec_url)
        self.spec: SchemaPath = spec
        self.validate_responses = validate_responses
        self.enforce_case = enforce_case
        self.custom_format_validators = custom_format_validators

        self._operations = OperationSpec.get_all(self.spec)
        self._server_paths = {urlsplit(server["url"]).path for server in self.spec["servers"]}

        if module is not None:
            if isinstance(module, str):
                module = _load_module(module)

            for operation_id in self._operations:
                name = operation_id
                if "." in name:
                    base, name = name.rsplit(".", 1)
                    base_module = _load_module(f"{module.__name__}.{base}")
                else:
                    base_module = module
                if self.enforce_case:
                    name = snakecase(name)
                try:
                    endpoint_fn = getattr(base_module, name)
                except AttributeError as ex:
                    raise RuntimeError(
                        f"The function `{base_module.__name__}.{name}` does not exist!"
                    ) from ex
                self.set_endpoint(endpoint_fn, operation_id=operation_id)

    def set_endpoint(
        self, endpoint_fn: Callable, *, operation_id: Optional[str] = None
    ) -> None:
        """
        Sets endpoint function for a given `operationId`.

        If the `operation_id` is not given, it will try to determine it based on the
        function name.

        Args:
            endpoint_fn: A callable (i.e. a function) that handles the endpoint.
            operation_id: Optional ID of the operation to attach the callable to.
                          If omitted, the `operation_id` is determined based on
                          the callable's name.
        """
        if operation_id is None:
            operation_id = endpoint_fn.__name__
        if self.enforce_case and operation_id not in self._operations:
            operation_id_key = {snakecase(op_id): op_id for op_id in self._operations}.get(
                operation_id
            )
        else:
            operation_id_key = operation_id
        try:
            operation = self._operations[cast(str, operation_id_key)]
        except KeyError as ex:
            raise ValueError(f"Unknown operationId: {operation_id}.") from ex

        @wraps(endpoint_fn)
        async def wrapper(request: Request, **kwargs) -> Response:
            openapi_request = OpenAPIRequest(request)
            try:
                validate_request(
                    request=openapi_request,
                    spec=self.spec,
                    extra_format_validators=self.custom_format_validators,
                )
            except SecurityProviderError as ex:
                if self.debug:
                    log.exception("Invalid security")
                raise HTTPException(HTTPStatus.FORBIDDEN, "Invalid security.") from ex
            except OpenAPIError as ex:
                if self.debug:
                    log.exception("Bad request")
                raise HTTPException(HTTPStatus.BAD_REQUEST, "Bad request") from ex

            response = endpoint_fn(request, **kwargs)
            if iscoroutine(response):
                response = await response
            if isinstance(response, dict):
                response = JSONResponse(response)
            elif not isinstance(response, Response):
                raise ValueError(
                    f"The endpoint function `{endpoint_fn.__name__}` must return"
                    " either a dict or a Response instance."
                )

            # TODO: pass a list of operation IDs to specify which responses not to validate
            if self.validate_responses:
                validate_response(
                    request=openapi_request,
                    response=OpenAPIResponse(response),
                    spec=self.spec,
                    extra_format_validators=self.custom_format_validators,
                )
            return response

        for server_path in self._server_paths:
            self.add_route(
                server_path + operation.path, wrapper, [operation.method], name=operation_id
            )

    def endpoint(self, operation_id: Union[Callable, str]):
        """
        Decorator for setting endpoints.

        If used without arguments, it will try to determine the `operationId` based on the
        decorated function name:

            @app.endpoint
            def foo_bar(request):
                # sets the endpoint for operationId fooBar

        Otherwise, the `operationId` can be set explicitly:

            @app.endpoint("fooBar"):
            def my_endpoint():
                ...

        Args:
            operation_id: ID of the operation to attach the callable to.
        """
        if callable(operation_id):
            self.set_endpoint(operation_id)
            return operation_id

        def decorator(endpoint_fn):
            self.set_endpoint(endpoint_fn, operation_id=operation_id)
            return endpoint_fn

        return decorator

    @classmethod
    def from_file(cls, path: Union[Path, str], *args, **kwargs) -> Application:
        """
        Creates an instance of the class by loading the spec from a local file.

        Args:
            path: Path of the OpenAPI spec file.
            args: Positional arguments are passed on to the class constructor.
            kwargs: Keyword arguments are passed on to the class constructor.
        """
        path = Path(path)
        return cls(get_spec_from_file(path), *args, spec_url=path.as_uri(), **kwargs)


def _load_module(name: str) -> ModuleType:
    """Helper function to load a module based on its dotted-string name."""
    try:
        module = import_module(name)
    except ModuleNotFoundError as ex:
        raise RuntimeError(f"The module `{name}` does not exist!") from ex
    else:
        return module
