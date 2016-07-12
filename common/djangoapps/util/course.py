"""
Utility methods related to course
"""
import logging
from django.conf import settings

from opaque_keys.edx.keys import CourseKey
from util.url import strip_scheme

log = logging.getLogger(__name__)


def get_lms_link_for_about_page(course_key):
    """
    Returns the url to the course about page from the location tuple.
    """

    assert isinstance(course_key, CourseKey)

    if settings.FEATURES.get('ENABLE_MKTG_SITE', False):
        if not hasattr(settings, 'MKTG_URLS'):
            log.exception("ENABLE_MKTG_SITE is True, but MKTG_URLS is not defined.")
            return None

        marketing_urls = settings.MKTG_URLS

        # Root will be "https://www.edx.org". The complete URL will still not be exactly correct,
        # but redirects exist from www.edx.org to get to the Drupal course about page URL.
        about_base = marketing_urls.get('ROOT')

        if about_base is None:
            log.exception('There is no ROOT defined in MKTG_URLS')
            return None
    else:
        about_base = settings.ENV_TOKENS.get('LMS_BASE')

    # replaces marketing url scheme with 'https' to follow lms/cms
    about_base = strip_scheme(about_base)

    return u"https://{about_base_url}/courses/{course_key}/about".format(
        about_base_url=about_base,
        course_key=course_key.to_deprecated_string()
    )
