""" Tests for course utils. """

from django.test import TestCase, override_settings, RequestFactory
import mock
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from util.course import get_lms_link_for_about_page


class LmsLinksTestCase(TestCase):
    """ Tests for LMS links. """

    def test_about_page(self):
        """ Get URL for about page, no marketing site """
        with mock.patch.dict('django.conf.settings.FEATURES', {'ENABLE_MKTG_SITE': False}):
            self.assertEquals(self.get_about_page_link(), "//localhost:8000/courses/mitX/101/test/about")

    @override_settings(MKTG_URLS={'ROOT': 'dummy-root'})
    def test_about_page_marketing_site(self):
        """ Get URL for about page, marketing root present. """
        with mock.patch.dict('django.conf.settings.FEATURES', {'ENABLE_MKTG_SITE': True}):
            self.assertEquals(self.get_about_page_link(), "//dummy-root/courses/mitX/101/test/about")
        with mock.patch.dict('django.conf.settings.FEATURES', {'ENABLE_MKTG_SITE': False}):
            self.assertEquals(self.get_about_page_link(), "//localhost:8000/courses/mitX/101/test/about")

    @override_settings(MKTG_URLS={'ROOT': 'http://www.dummy'})
    def test_about_page_marketing_site_remove_http(self):
        """ Get URL for about page, marketing root present, remove http://. """
        with mock.patch.dict('django.conf.settings.FEATURES', {'ENABLE_MKTG_SITE': True}):
            self.assertEquals(self.get_about_page_link(), "//www.dummy/courses/mitX/101/test/about")

    @override_settings(MKTG_URLS={'ROOT': 'https://www.dummy'})
    def test_about_page_marketing_site_remove_https(self):
        """ Get URL for about page, marketing root present, remove https://. """
        with mock.patch.dict('django.conf.settings.FEATURES', {'ENABLE_MKTG_SITE': True}):
            self.assertEquals(self.get_about_page_link(), "//www.dummy/courses/mitX/101/test/about")

    @override_settings(MKTG_URLS={'ROOT': 'www.dummyhttps://x'})
    def test_about_page_marketing_site_https__edge(self):
        """ Get URL for about page, only remove https:// at the beginning of the string. """
        with mock.patch.dict('django.conf.settings.FEATURES', {'ENABLE_MKTG_SITE': True}):
            self.assertEquals(self.get_about_page_link(), "//www.dummyhttps://x/courses/mitX/101/test/about")

    @override_settings(MKTG_URLS={})
    def test_about_page_marketing_urls_not_set(self):
        """ Error case. ENABLE_MKTG_SITE is True, but there is either no MKTG_URLS, or no MKTG_URLS Root property. """
        with mock.patch.dict('django.conf.settings.FEATURES', {'ENABLE_MKTG_SITE': True}):
            self.assertEquals(self.get_about_page_link(), None)

    @override_settings(LMS_BASE=None)
    def test_about_page_no_lms_base(self):
        """ No LMS_BASE, nor is ENABLE_MKTG_SITE True """
        self.assertEquals(self.get_about_page_link(), None)

    def get_about_page_link(self):
        """ create mock course and return the about page link """
        course_key = SlashSeparatedCourseKey('mitX', '101', 'test')
        request = RequestFactory().get("/test_path")
        request.META['HTTP_HOST'] = "localhost:8000"  # pylint: disable=no-member
        return get_lms_link_for_about_page(request, course_key)
