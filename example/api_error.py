from starlette.requests import Request
from starlette.responses import JSONResponse
from openapi_core.exceptions import OpenAPIError
from http import HTTPStatus

def handle_error(request: Request, ex: Exception):
    if isinstance(ex, OpenAPIError):
        resp = {}
        resp["type"] = request.url.path
        resp["code"] = "FORMAT_ERROR"
        resp["detail"]  = str(ex.__cause__) if ex.__cause__ is not None else str(ex)
        return JSONResponse(content=resp, status_code=HTTPStatus.BAD_REQUEST)  
    if isinstance(ex, SecurityProviderError):
        resp = {}
        resp["type"] = request.url.path
        resp["code"] = "SECURITY_ERROR"
        resp["detail"]  = str(ex.__cause__) if ex.__cause__ is not None else str(ex)
        return JSONResponse(content=resp, status_code=HTTPStatus.FORBIDDEN)  