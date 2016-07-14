"""
Common Methods to Validate Configurations
"""
from django.conf import settings


def validate_marketing_site_config():
    """
    Validate 'marketing site' related configurations
    """
    if not hasattr(settings, 'MKTG_URLS'):
        raise ValueError("ENABLE_MKTG_SITE is True, but MKTG_URLS is not defined.")
    if not settings.MKTG_URLS.get('ROOT'):
        raise ValueError('There is no ROOT defined in MKTG_URLS')
