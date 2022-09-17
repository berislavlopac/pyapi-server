"""Starlette requests."""
from __future__ import annotations

from functools import partial
from typing import Any, Dict, Literal, NamedTuple, Optional

from openapi_core.deserializing.media_types.factories import MediaTypeDeserializersFactory
from openapi_core.unmarshalling.schemas.factories import (
    OAS30Validator,
    SchemaUnmarshallersFactory,
    UnmarshalContext,
)
from openapi_core.validation.request import datatypes, RequestValidator
from openapi_core.validation.response import ResponseValidator
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match


class OpenAPIRequest(NamedTuple):
    """Basic OpenAPIRequest implementation."""

    host_url: str
    path: str
    method: str
    mimetype: str
    parameters: datatypes.RequestParameters
    body: Optional[str] = None

    @classmethod
    async def from_request(cls, request: Request) -> OpenAPIRequest:
        """Create OpenAPIREQuest from Starlette request."""
        path = request.url.path

        for route in request.app.router.routes:
            match, _ = route.matches(request)
            if match == Match.FULL:
                path = route.path
                break

        parameters = datatypes.RequestParameters(
            path=request.path_params,
            query=datatypes.ImmutableMultiDict(request.query_params),
            header=request.headers,
            cookie=datatypes.ImmutableMultiDict(request.cookies),
        )

        return cls(
            host_url=f"{request.url.scheme}://{request.url.netloc}",
            path=path,
            method=request.method.casefold(),
            parameters=parameters,
            body=(await request.body()).decode(),
            mimetype=request.headers.get("content-type"),
        )


class OpenAPIResponse(NamedTuple):
    """Basic OpenAPIResponse v."""

    data: str
    status_code: int
    mimetype: str
    headers: datatypes.Headers

    @classmethod
    def from_response(cls, response: Response) -> OpenAPIResponse:
        """Create OpenAPIResponse from Starlette response."""
        mimetype, *_ = response.headers.get("content-type", "").split(";")
        return cls(
            data=response.body.decode(),
            status_code=response.status_code,
            mimetype=mimetype,
            headers=datatypes.Headers(dict(response.headers)),
        )


def _get_validator(
    object_type: Literal["request", "response"],
    custom_formatters: Dict[str, Any],
    custom_media_type_deserializers: Dict[str, Any],
) -> ResponseValidator:
    validator_class = {"request": RequestValidator, "response": ResponseValidator}[object_type]
    return validator_class(
        SchemaUnmarshallersFactory(
            OAS30Validator,
            custom_formatters=custom_formatters,
            context=UnmarshalContext.RESPONSE,
        ),
        media_type_deserializers_factory=MediaTypeDeserializersFactory(
            custom_deserializers=custom_media_type_deserializers,
        ),
    )


get_response_validator = partial(_get_validator, "response")
get_request_validator = partial(_get_validator, "request")
