"""
Common Functions to Validate Configurations
"""
from django.conf import settings


def validate_lms_config():
    """
    Validates configurations for lms and raise ValueError if not valid
    """
    validate_common_config()

    # validate feature based configurations
    validate_marketing_site_config()


def validate_cms_config():
    """
    Validates configurations for lms and raise ValueError if not valid
    """
    validate_common_config()

    # validate feature based configurations
    validate_marketing_site_config()


def validate_common_config():
    """
    Validates configurations common for all apps
    """
    if not settings.ENV_TOKENS.get('LMS_ROOT_URL'):
        raise ValueError("'LMS_ROOT_URL' is not defined.")


def validate_marketing_site_config():
    """
    Validates 'marketing site' related configurations
    """
    if settings.FEATURES.get('ENABLE_MKTG_SITE'):
        if not hasattr(settings, 'MKTG_URLS'):
            raise ValueError("'ENABLE_MKTG_SITE' is True, but 'MKTG_URLS' is not defined.")
        if not settings.MKTG_URLS.get('ROOT'):
            raise ValueError("There is no 'ROOT' defined in 'MKTG_URLS'")
