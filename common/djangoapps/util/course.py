"""
Utility methods related to course
"""
import logging
from django.conf import settings

from opaque_keys.edx.keys import CourseKey
import re

log = logging.getLogger(__name__)


def get_lms_link_for_about_page(course_key):
    """
    Returns the url to the course about page from the location tuple.
    """
    assert isinstance(course_key, CourseKey)

    about_base = lms_root_url = settings.ENV_TOKENS.get('LMS_ROOT_URL')

    if settings.FEATURES.get('ENABLE_MKTG_SITE'):
        # Root will be "https://www.edx.org". The complete URL will still not be exactly correct,
        # but redirects exist from www.edx.org to get to the Drupal course about page URL.
        about_base = settings.MKTG_URLS['ROOT']
        # Strip off https:// (or http://) to be consistent with the formatting of LMS_BASE.
        about_base = re.sub(r"^https?://", lms_root_url.urlparse().scheme if lms_root_url else "", about_base)
    elif not lms_root_url:

        #about_base = settings.ENV_TOKENS.get('LMS_ROOT_URL')
        #if not about_base:
        log.error()
        return None

    # Strip off https:// (or http://) to be consistent with the formatting of LMS_BASE.
    #about_base = re.sub(r"^https?://", "", about_base)
    return u"{about_base_url}/courses/{course_key}/about".format(
        about_base_url=about_base,
        course_key=course_key.to_deprecated_string()
    )
