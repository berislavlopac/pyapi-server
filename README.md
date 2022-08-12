# PyAPI Server

**PyAPI Server** is a Python library for serving REST APIs based on
[OpenAPI](https://swagger.io/resources/open-api/) specifications. It is based on [Starlette](https://www.starlette.io) and is functionally very similar to [connexion](https://connexion.readthedocs.io), except that it aims to be fully [ASGI](https://asgi.readthedocs.io)-compliant.

**WARNING:** This is still a work in progress and not quite ready for production usage. Until version 1.0 is released, any new release can be expected to break backward compatibility.


## Quick Start

```python
from pyapi.server import Application
from some.path import endpoints

app = Application.from_file("path/to/openapi.yaml", module=endpoints)
```
