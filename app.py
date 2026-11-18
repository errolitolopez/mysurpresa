"""Start MySurpresa: flask --app app run --debug

The app itself is the mysurpresa package (mysurpresa/__init__.py: create_app).
"""

from mysurpresa import create_app

app = create_app()
