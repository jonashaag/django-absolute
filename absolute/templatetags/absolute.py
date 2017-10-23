# -*- coding: utf-8 -*-
from django.contrib.sites.shortcuts import get_current_site
from django.template import Library
from django.template.defaulttags import URLNode, url
from django.template.base import Token
from django.conf import settings

register = Library()


class AbsoluteUrlNode(URLNode):
    def render(self, context):
        asvar, self.asvar = self.asvar, None  # Needed to get a return value from super
        path = super(AbsoluteUrlNode, self).render(context)
        self.asvar = asvar
        request = context['request']
        absolute_url = request.build_absolute_uri(path)
        if asvar:
            context[asvar] = absolute_url
            return ''
        else:
            return absolute_url


@register.tag
def absolute(parser, token):
    '''
    Returns a full absolute URL based on the request host.

    This template tag takes exactly the same paramters as url template tag.
    '''
    node = url(parser, token)
    return AbsoluteUrlNode(
        view_name=node.view_name,
        args=node.args,
        kwargs=node.kwargs,
        asvar=node.asvar
    )


class SiteUrlNode(URLNode):
    def __init__(self, site, *args, **kwargs):
        self.site = site
        super().__init__(*args, **kwargs)

    def render(self, context):
        asvar, self.asvar = self.asvar, None  # Needed to get a return value from super
        path = super(SiteUrlNode, self).render(context)
        self.asvar = asvar

        request = context.get('request')

        if self.site:
            site = self.site.resolve(context)
        else:
            site = get_current_site(request)
        assert hasattr(site, 'domain')

        protocol = getattr(settings, 'ABSOLUTE_URL_PROTOCOL', None)
        if protocol is None:
            if request is not None:
                protocol = 'https' if request.is_secure() else 'http'
            else:
                protocol = 'http'
        site_url = "%s://%s%s" % (protocol, site.domain, path)
        if asvar:
            context[asvar] = site_url
            return ''
        else:
            return site_url


@register.tag
def site(parser, token):
    '''
    Returns a full absolute URL based on the current site.

    This template tag takes exactly the same paramters as url template tag,
    plus an optional "site" argument to force usage of a given Site object::

        {% site "my_view" site my_site_obj %}
    '''
    bits = token.split_contents()
    if len(bits) > 2 and bits[2] == 'site':
        site = parser.compile_filter(bits[3])
        token = Token(token.token_type, ' '.join(bits[:2] + bits[4:]), token.position, token.lineno)
    else:
        site = None

    node = url(parser, token)

    return SiteUrlNode(
        site=site,
        view_name=node.view_name,
        args=node.args,
        kwargs=node.kwargs,
        asvar=node.asvar
    )
