from acme_pay.core.database import to_async_url


def test_switches_plain_postgres_url_to_asyncpg_driver() -> None:
    url, connect_args = to_async_url("postgresql://acme:acme@localhost:5432/acme_pay")

    assert url == "postgresql+asyncpg://acme:acme@localhost:5432/acme_pay"
    assert connect_args == {}


def test_moves_neon_ssl_parameters_into_connect_args() -> None:
    url, connect_args = to_async_url(
        "postgresql://user:secret@ep-x.neon.tech/acme_pay?sslmode=require&channel_binding=require"
    )

    assert url == "postgresql+asyncpg://user:secret@ep-x.neon.tech/acme_pay"
    assert connect_args == {"ssl": "require"}
