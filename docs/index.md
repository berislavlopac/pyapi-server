# PyAPI Server

Lightweight API framework using an OpenAPI spec for routing and validation.

**PyAPI Server** is a Python library for serving REST APIs based on
[OpenAPI](https://swagger.io/resources/open-api/) specifications. It is based on [Starlette](https://www.starlette.io) and is functionally very similar to [connexion](https://connexion.readthedocs.io), except that it aims to be fully [ASGI](https://asgi.readthedocs.io)-compliant.

**WARNING:** This is still very much work in progress and not quite ready for production usage. Until version 1.0 is released, any version can be expected to break backward compatibility.

### Why PyAPI Server?

The main advantage of PyAPI Server is that it uses the OpenAPI specification to both prepare and validate requests and responses.

Specifically, when PyAPI Server receives a request it validates it against the URLs defined in the specification, raising an error in case of an invalid request. On a valid request it looks for an "endpoint function" matching the request URL's `operationId`; this function is supposed to process a request and return a response, which is then also validated based on the specification rules before being sent back to the client.
## Quick Start

```python
from pyapi.server import Application
from some.path import endpoints

app = Application.from_file("path/to/openapi.yaml", module=endpoints)
```

## Example Setup

The minimal setup consists of three files:

* A REST(ful) API specification in the form of an OpenAPI file, usually in YAML or JSON format.
* A Python file, e.g. `server.py`, which initiates your application.
* Another Python file containing the individual endpoint functions.

The directory `src/examples/server/` contains a working example PyAPI Server application, using the specification at `src/examples/petstore.yaml` -- which is a copy of the standard OpenAPI
[example specification](https://editor.swagger.io/).

To run the example, follow these steps inside a Python `virtualenv`:

1. Install [`poetry`](https://poetry.eustace.io/docs/#installation)
2. Install PyAPI server with optional dependencies: `poetry install -E uvicorn`
3. Start the PyAPI example server: `uvicorn example.server:app --reload --host 0.0.0.0 --port 5000 --log-level debug`


## Application

A PyAPI Server application is an instance of the `pyapi.server.Application` class, which is a subclass of
`starlette.applications.Starlette`; this means it is fully ASGI-compatible and can be used as any other ASGI app.

When initialising a PyAPI Server app, it is necessary to provide an OpenAPI specification file.

For example:

```python
from pyapi.server import Application
app = Application(spec=api_spec)
```

The value of `spec` is either a Python dictionary of the OpenAPI spec, or an `openapi-core` `Spec` object. There is a helper class method which will load the spec provided a path in a specification file:

```python
app = Application.from_file('myserver/spec.yaml')
```

Optionally, a module containing endpoint functions (see below) can be added as a keyword argument. It can be specified as the dot-separated path to the module location; in the above example, it might be the file `myserver/endpoints.py` or the directory `myserver/endpoints/`. Alternatively, `module` can be the actual imported module:

```python
from myserver import endpoints
app = Application(api_spec, module=endpoints)
```

The `Application` constructor also accepts the following keyword arguments:

* `validate_responses`: Boolean (defaults to `True`) If `True`, each response will be validated against the spec before being sent back to the caller.
* `enforce_case`: Boolean (defaults to `True`). If `true`, the `operationId` values will be normalized to snake case when setting endpoint functions. For example, `operationId` `fooBar` will expect the function named `foo_bar`.

Any other keyword arguments provided to the `Application` constructor will be passed directly into the `Starlette` application class.


## Endpoints

### Endpoint Functions

An endpoint is a standard Python function, which needs to conform to the following requirements:

1. It needs to accept a single positional argument, a request object compatible with the Starlette [`Request`](https://www.starlette.io/requests/).
2. It has to return either a Python dictionary, or an object compatible with the Starlette [`Response`](https://www.starlette.io/responses/). If it is a dictionary, PyAPI Server will convert it into a `JSONResponse`.
3. It doesn't have to be a coroutine function (defined using `async def` syntax), but it is highly recommended, especially if it needs to perform any asynchronous operations itself (e.g. if it makes a call to an external API).

A basic example of an endpoint function:

```python
async def get_pet_by_id(request):
    return {
        "id": request.path_params['id'],
        "species": "cat",
        "name": "Lady Athena",
    }
```

### Setting Endpoints on Application

The OpenAPI spec defines the endpoints ("paths") that the API handles, as well as the requests and responses it can recognise. Each endpoint has a [field](https://swagger.io/specification/#operation-object) called `operationId`, which is supposed to be globally unique; PyAPI server takes advantage of this field to find the corresponding endpoint function.

Endpoint functions can be defined in several ways:


#### A Python Module

The first way is as a Python module that contains the endpoint functions. For example, assume that we have the module
`server/endpoints.py`, looking something like this:

```python
async def foo_endpoint(request):
    return {"foo": "bar"}
    
async def bar_endpoint(request):
    return {"bar": "foo"}
```

We can then define our application in the following way:

```python
from myserver import endpoints

app = Application(spec=api_spec, module=endpoints)
```

Assuming, of course, that our OpenAPI spec contains `operationId`s named `fooEndpoint` and `barEndpoint`.


#### A Python Module Path

Alternatively, instead of an imported module we can pass a string in the form of a dot-separated path; for example, `myserver.endpoints`. The equivalent of the example above would now be:

```python
app = Application(spec=api_spec, module="myserver.endpoints")
```

PyAPI Server will try to locate the endpoint module by combining the `module` argument and the `operationId` value, converting the function name to snake case if necessary. E.g. if the base is `myserver.endpoints` and the `operationId` is `fooEndpoint`, it will import the `foo_endpoint` function located in either `myserver/endpoints.py` (or `myserver/endpoints/__init__.py`). Also, if the `operationId` value itself contains dots it will try to build the full path, so `some.extra.levels.fooBar` will look for the module `myserver/endpoints/some/extra/levels.py`.


#### Setting Individual Endpoints

The endpoints can also be set individually, using the `set_endpoint` method:

```python
from pyapi.server import Application
from myserver.endpoints import some_endpoint, another_endpoint

app = Application(spec=api_spec)

app.set_endpoint(some_endpoint)
```

PyAPI Server determines the operation from the function name: in the example above it would be set on the `operationId` named `someEndpoint`. Alternatively, the `operationId` can be provided explicitly:

```python
app.set_endpoint(another_endpoint, operation_id="someOtherOperationId")
```


#### The Endpoint Decorator

It is also possible to define endpoints as they are defines, using the `endpoint` decorator, which works analogous
to the `set_endpoint` method:

```python
app = Application(spec=api_spec)

@app.endpoint
def some_endpoint(request):
    ...
    
@app.endpoint(operation_id="someOtherOperationId")
def another_endpoint(request):
    ...
    
@app.endpoint("aCompletelyDifferentOperationId")
def yet_another_endpoint(request):
    ...
```

### Additional Server Configuration

The server instance can be additionally configured with a few OpenAPI-specific custom handlers:

* **custom_formatters** is a dict of custom [formatter](https://github.com/p1c2u/openapi-core#formats) objects that will be applied both to requests and responses.
* **custom_media_type_deserializers** are [functions](https://github.com/p1c2u/openapi-core#deserializers) that can deserialise custom media types.

Example:

```python
app = Application(spec=api_spec)
api.custom_formatters = {
    "email": EmailFormatter,
}
api.custom_media_type_deserializers = {
    "application/protobuf": protobuf_deserializer,
}
```
