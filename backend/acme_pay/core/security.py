"""Who is acting. The single seam where real authentication plugs in (ADR 0008)."""

HR_MANAGER = "HR Manager"


async def get_current_actor() -> str:
    """Return the acting user's display name, recorded on every salary change.

    v1 has no login, so this is always the HR manager. Replacing this dependency with
    an OIDC/JWT verifier adds authentication without touching routes or services.
    """
    return HR_MANAGER
