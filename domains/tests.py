# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django import test
from django.conf import settings
from django.conf.urls import url
from django.contrib.sites.models import Site
from django.shortcuts import render
from domains.hooks.base import StrHookBase, TupleHookBase, ListHookBase, DictHookBase, IntHookBase
from domains.compat import text_type


urlpatterns = [
    url('^$', lambda request: render(request, 'test_index.html')),
]


class TestIntHook(IntHookBase):
    attribute = 'DOMAINS_TEST_ATTRIBUTE_INT'

    def value(self, request):
        return 0


class TestStrHook(StrHookBase):
    attribute = 'DOMAINS_TEST_ATTRIBUTE_STR'

    def value(self, request):
        return request.get_host()


class TestDictHook(DictHookBase):
    attribute = 'DOMAINS_TEST_ATTRIBUTE_DICT'

    def value(self, request):
        v = request.get_host()
        return {
            1: v + '_1',
            2: v + '_2',
        }


class TestListHook(ListHookBase):
    attribute = 'DOMAINS_TEST_ATTRIBUTE_LIST'

    def value(self, request):
        v = request.get_host()
        return [v, v, v]


class TestTupleHook(TupleHookBase):
    attribute = 'DOMAINS_TEST_ATTRIBUTE_TUPLE'

    def value(self, request):
        v = request.get_host()
        return (v, v, v)


class EnvironmentTest(test.TestCase):
    """
    Tests the environment
    """
    def test_middleware(self):
        self.assertIn('domains.middleware.RequestMiddleware',
                      settings.MIDDLEWARE_CLASSES)


class TestBase(test.TestCase):
    """
    Common things
    """
    urls = 'domains.tests'

    def setUp(self):
        """
        Runs before each unit test
        """
        self.client = test.Client()


class TemplateLoadersTest(TestBase):
    """
    Test suite for dynamic template directories
    """

    def test_foo_dot_com(self):
        """
        Tests for first domain
        """
        resp = self.client.get('/', HTTP_HOST='test.foo.com')
        self.assertContains(resp, text='test.foo.com')
        self.assertNotContains(resp, text='test.bar.com')

    def test_bar_dot_com(self):
        """
        Tests for second domain
        """
        resp = self.client.get('/', HTTP_HOST='test.bar.com')
        self.assertContains(resp, 'test.bar.com')
        self.assertNotContains(resp, 'test.foo.com')

    def test_another_domain(self):
        """
        Tests if templates with domain name not found
        """
        resp = self.client.get('/', HTTP_HOST='github.com')
        self.assertNotContains(resp, 'test.bar.com')
        self.assertNotContains(resp, 'test.foo.com')
        self.assertContains(resp, 'DEFAULT')

    def test_complex(self):
        """
        Complex
        """
        tests = (
            ('test.foo.com', 'test.foo.com'),
            ('microsoft.com', 'DEFAULT'),
            ('test.foo.com', 'test.foo.com'),
            ('test.bar.com', 'test.bar.com'),
            ('google.com', 'DEFAULT'),
            ('test.bar.com', 'test.bar.com'),
            ('test.foo.com', 'test.foo.com'),
            ('yahoo.com', 'DEFAULT'),
        )

        for domain, content in tests:
            resp = self.client.get('/', HTTP_HOST=domain)
            self.assertContains(resp, content)


            self.assertEquals(text_type(domain),
                              text_type(settings.DOMAINS_TEST_ATTRIBUTE_STR))

            self.assertEquals(0,  # @TODO!
                              settings.DOMAINS_TEST_ATTRIBUTE_INT)

#            self.assertEquals((domain, domain, domain), 
#                              tuple(settings.DOMAINS_TEST_ATTRIBUTE_TUPLE))

            self.assertEquals([domain, domain, domain],  # @TODO!
                              list(settings.DOMAINS_TEST_ATTRIBUTE_LIST))

    def test_custom_function(self):
        """
        Custom function
        """
        func = 'domains.tests.test_function'
        with self.settings(DOMAINS_TEMPLATE_NAME_FUNCTION=func):
            resp = self.client.get('/', HTTP_HOST='microsoft.com')
            self.assertContains(resp, 'CUSTOM')


class SiteIdTest(TestBase):
    """
    Test dynamic
    """
    def setUp(self):
        super(SiteIdTest, self).setUp()
        self.sites = {
            1: Site.objects.create(domain='test.foo.com', name='Foo'),
            2: Site.objects.create(domain='test.bar.com', name='Bar'),
            3: Site.objects.create(domain='github.com', name='Git'),
        }

    def test_1(self):
        for _ in range(0, 3):
            for pk, site in self.sites.items():
                self.client.get('/', HTTP_HOST=site.domain)
                curr = Site.objects.get_current()
                self.assertEquals(curr.domain, site.domain)
                self.assertEquals(curr.pk, site.pk)


def test_function(template_dir, template_name):
    """
    Generates parts of template name
    """
    return template_dir, 'custom_' + template_name
