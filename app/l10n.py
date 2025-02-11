from fluent.runtime import FluentLocalization, FluentResourceLoader
import os

LOCALES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'l10n')
SUPPORTED_LOCALES = ['en', 'ru', 'uk']
DEFAULT_LOCALE = 'en'

loader = FluentResourceLoader(os.path.join(LOCALES_DIR, '{locale}.ftl'))
_localizations = {}

def get_localization(locale: str) -> FluentLocalization:
    if locale not in _localizations:
        if locale not in SUPPORTED_LOCALES:
            locale = DEFAULT_LOCALE
        try:
            ftl_path = os.path.join(LOCALES_DIR, f"{locale}.ftl")
            _localizations[locale] = FluentLocalization(
                [locale],
                [ftl_path],
                loader
            )
        except Exception as e:
            if locale != DEFAULT_LOCALE:
                return get_localization(DEFAULT_LOCALE)
            raise e
    return _localizations[locale]

class Message:
    @staticmethod
    def get_message(locale: str, message_id: str, **kwargs) -> str:
        try:
            l10n = get_localization(locale)
            message = l10n.format_value(message_id, kwargs)
            return message if message != message_id else message_id
        except Exception:
            return message_id