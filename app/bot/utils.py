from typing import Optional


def get_language_code(language_code: Optional[str]) -> str:
    if language_code:
        return language_code
    return 'ru'
