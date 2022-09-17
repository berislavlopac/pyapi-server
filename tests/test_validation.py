from openapi_core.validation.request.protocols import Request as RequestProtocol
from openapi_core.validation.response.protocols import Response as ResponseProtocol

from pyapi.server.validation import datatypes, OpenAPIRequest, OpenAPIResponse


def test_openapirequest_implements_request_protocol():
    request = OpenAPIRequest(
        host_url="host_url",
        path="path_pattern",
        method="method",
        parameters=datatypes.RequestParameters(),
        body="body",
        mimetype="mimemtype",
    )
    assert isinstance(request, RequestProtocol)


def test_openapiresponse_implements_response_protocol():
    response = OpenAPIResponse(
        data="data", status_code=200, mimetype="mimetype", headers=datatypes.Headers()
    )
    assert isinstance(response, ResponseProtocol)
