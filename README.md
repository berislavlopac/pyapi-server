# PyAPI Server

[![Build Status](https://b11c.semaphoreci.com/badges/pyapi-server/branches/main.svg?style=shields&key=e9eeb9d2-6487-4aba-9207-e46c84f9bc6f)](https://b11c.semaphoreci.com/projects/pyapi-server)
[![Documentation Status](https://readthedocs.org/projects/pyapi-server/badge/?version=latest)](https://pyapi-server.readthedocs.io/en/latest/?badge=latest)

**PyAPI Server** is a Python library for serving REST APIs based on
[OpenAPI](https://swagger.io/resources/open-api/) specifications. It is based on [Starlette](https://www.starlette.io) and is functionally very similar to [connexion](https://connexion.readthedocs.io), except that it aims to be fully [ASGI](https://asgi.readthedocs.io)-compliant.

**WARNING:** This is still a work in progress and not quite ready for production usage. Until version 1.0 is released, any new release can be expected to break backward compatibility.


## Quick Start

```python
from pyapi.server import Application
from some.path import endpoints

app = Application.from_file("path/to/openapi.yaml", module=endpoints)
```
