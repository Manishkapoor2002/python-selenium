"""Request / response data models for the API layer.

Use ``dataclasses`` (stdlib) for new models so the framework does not
take a hard runtime dependency on Pydantic. Add one module per
resource (e.g. ``user_models.py``, ``order_models.py``).
"""


