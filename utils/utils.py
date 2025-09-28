import secrets


def update_object(obj, **kwargs) -> None:
    """
    Update object attributes in the database.
    """
    if kwargs:
        obj.__class__.objects.filter(pk=obj.pk).update(**kwargs)

def generate_unique_link(prefix: str, char_size: int = 10) -> str:
    """
    Generate a short unique link with given prefix.
    Example: S_a8df9K2L or E_xc91UzpQ
    """
    token = secrets.token_urlsafe(char_size)  # random 8-10 chars
    return f"{prefix}_{token}"
