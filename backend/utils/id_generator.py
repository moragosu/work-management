import uuid


def next_sequential_id(items: list, prefix: str, id_key: str = "id") -> str:
    """Generate next sequential ID (e.g. O1→O2, T3→T4)."""
    if not items:
        return f"{prefix}1"
    max_num = 0
    for item in items:
        try:
            num = int(item[id_key].replace(prefix, ""))
            if num > max_num:
                max_num = num
        except (ValueError, KeyError):
            pass
    return f"{prefix}{max_num + 1}"


def short_uuid(prefix: str) -> str:
    """Generate a short random ID (e.g. 'S3F2A1B4')."""
    return f"{prefix}{str(uuid.uuid4())[:8].upper()}"
