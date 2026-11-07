"""Registry of all ORM models, so metadata is complete wherever it is needed."""


def register_models() -> None:
    """Import every model module so its tables are registered on ``Base.metadata``."""
    import acme_pay.compensation.models
    import acme_pay.employees.models  # noqa: F401  (imported for its side effect)
