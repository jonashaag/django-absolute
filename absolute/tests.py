import json

from unittest import skipIf

from django import VERSION
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template import Context, Template, RequestContext
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from absolute.context_processors import absolute


class AbsoluteContextProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_context_processors_absolute(self):
        request = self.factory.get('/')
        context = absolute(request)

        self.assertIn('ABSOLUTE_ROOT', context)
        self.assertIn('ABSOLUTE_ROOT_URL', context)
        self.assertEqual(context['ABSOLUTE_ROOT'], 'http://testserver')
        self.assertEqual(context['ABSOLUTE_ROOT_URL'], 'http://testserver/')

    @override_settings(INSTALLED_APPS=('django.contrib.sites', 'absolute'))
    def test_context_processors_site(self):
        request = self.factory.get('/')
        context = absolute(request)

        domain = Site.objects.get_current().domain

        self.assertIn('SITE_ROOT', context)
        self.assertIn('SITE_ROOT_URL', context)
        self.assertEqual(context['SITE_ROOT'], 'http://%s' % domain)
        self.assertEqual(context['SITE_ROOT_URL'], 'http://%s/' % domain)

    @override_settings(INSTALLED_APPS=('absolute',))
    def test_context_processors_site_not_installed(self):
        request = self.factory.get('/')
        context = absolute(request)

        self.assertNotIn('SITE_ROOT', context)
        self.assertNotIn('SITE_ROOT_URL', context)


TEMPLATE1 = Template('''{% load absolute %}
    {
        "absolute": "{% absolute "test_url" %}",
        "site": "{% site "test_url" %}"
    }
    '''
)
TEMPLATE2 = Template('''{% load absolute %}
    {% absolute "test_url" as absolute_url %}
    {% site "test_url" as site_url %}
    {
        "absolute": "{{ absolute_url }}",
        "site": "{{ site_url }}"
    }
    '''
)


class AbsoluteTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_template_tags(self):
        request = self.factory.get(reverse('test_url'))
        rendered = TEMPLATE1.render(RequestContext(request))
        data = json.loads(rendered)

        domain = Site.objects.get_current().domain
        self.assertEqual(data['absolute'], 'http://testserver/test')
        self.assertEqual(data['site'], 'http://%s/test' % domain)

    def test_template_tag_as_syntax(self):
        request = self.factory.get(reverse('test_url'))
        rendered = TEMPLATE2.render(RequestContext(request))
        data = json.loads(rendered)

        domain = Site.objects.get_current().domain
        self.assertEqual(data['absolute'], 'http://testserver/test')
        self.assertEqual(data['site'], 'http://%s/test' % domain)

    def test_site_fallback(self):
        '''Should fallback on http protocol if request is missing'''
        t = Template('{% load absolute %}{% site "test_url" %}')
        rendered = t.render(Context())
        domain = Site.objects.get_current().domain
        self.assertEqual(rendered, 'http://%s/test' % domain)

    def test_site_override(self):
        foo_site = Site.objects.create(domain='foo.com', name='foo.com')
        t = Template('{% load absolute %}{% site "test_url" site my_site %}')
        rendered = t.render(Context({'my_site': foo_site}))
        self.assertEqual(rendered, 'http://foo.com/test')

    @override_settings(ABSOLUTE_URL_PROTOCOL='xxx')
    def test_site_protocol(self):
        t = Template('{% load absolute %}{% site "test_url"  %}')
        rendered = t.render(Context())
        self.assertEqual(rendered, 'xxx://example.com/test')

    @override_settings(INSTALLED_APPS=('absolute',), ALLOWED_HOSTS=('bar.com',))
    def test_template_tags_without_contrib_sites(self):
        self.factory.defaults['HTTP_HOST'] = 'bar.com'
        request = self.factory.get(reverse('test_url'))
        rendered = TEMPLATE1.render(RequestContext(request))
        data = json.loads(rendered)

        self.assertEqual(data['absolute'], 'http://bar.com/test')
        self.assertEqual(data['site'], 'http://bar.com/test')
