from pathlib import Path

from pyapi.server import Application

SPEC_PATH = Path(__file__).parent / "petstore.yaml"
ENDPOINTS_MODULE = "example.pets"

app = Application.from_file(SPEC_PATH, module=ENDPOINTS_MODULE, debug=True)
