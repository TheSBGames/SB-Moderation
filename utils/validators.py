def is_valid_channel_id(channel_id: str) -> bool:
    """Validate if the provided channel ID is a valid Discord channel ID."""
    return channel_id.isdigit() and 18 <= len(channel_id) <= 21

def is_valid_user_id(user_id: str) -> bool:
    """Validate if the provided user ID is a valid Discord user ID."""
    return user_id.isdigit() and 18 <= len(user_id) <= 21

def is_valid_role_id(role_id: str) -> bool:
    """Validate if the provided role ID is a valid Discord role ID."""
    return role_id.isdigit() and 18 <= len(role_id) <= 21

def is_valid_duration(duration: int) -> bool:
    """Validate if the provided duration is a positive integer."""
    return isinstance(duration, int) and duration > 0

def is_valid_badword(badword: str) -> bool:
    """Validate if the provided badword is a non-empty string."""
    return isinstance(badword, str) and len(badword) > 0

def is_valid_category_id(category_id: str) -> bool:
    """Validate if the provided category ID is a valid Discord category ID."""
    return category_id.isdigit() and 18 <= len(category_id) <= 21

def is_valid_xp_amount(xp: int) -> bool:
    """Validate if the provided XP amount is a non-negative integer."""
    return isinstance(xp, int) and xp >= 0

def is_valid_level(level: int) -> bool:
    """Validate if the provided level is a positive integer."""
    return isinstance(level, int) and level > 0