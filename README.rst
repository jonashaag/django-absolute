Django Absolute
===============

.. image:: https://secure.travis-ci.org/noirbizarre/django-absolute.png
   :target: http://travis-ci.org/noirbizarre/django-absolute

Django Absolute provides context processors and template tags to use full absolute URLs in templates.

Installation
------------

You can install Django Absolute with pip:

.. code-block:: bash

    pip install django-absolute

or with easy_install:

.. code-block:: bash

    easy_install django-absolute


Add ``absolute`` to your ``settings.INSTALLED_APPS``.


Context processor
-----------------

Add ``absolute.context_processors.absolute`` to your template context processors.
Note that this requires the ``request`` context processor shipped with Django.

Then you can access the following variables in your templates:

* ``ABSOLUTE_ROOT``: full absolute root URL (without trailing slash) based on incoming request
* ``ABSOLUTE_ROOT_URL``: full absolute root URL (with trailing slash) based on incoming request
* ``SITE_ROOT``: full absolute root URL (without trailing slash) based on current Django Site
* ``SITE_ROOT_URL``: full absolute root URL (with trailing slash) based on current Django site


Template tags
-------------

Django absolute provide 2 template tags:

* ``absolute``: acts like ``url`` but provide a full URL based on incoming request.
* ``site``: acts like ``url`` but provide a full URL based on current Django Site.

To use theses template tags, you need to load the ``absolute`` template tag library.

.. code-block:: html+django

    {% load absolute %}

    {% url "my_view" %}
    {% absolute "my_view" %}
    {% site "my_view" %}

These template tags have exactly the same syntax as ``url``, including the "`as`" syntax:

.. code-block:: html+django

    {% absolute "my_view" as the_url %}
    {{ the_url }}

You may optionally pass a custom ``site`` to the ``{% site %}`` templatetag to
always make it used that given site:

.. code-block:: html+django
  
    {% site "my_view" site my_site_obj ...url args... %}


Settings
--------
``{% site "my_view" %}`` guesses the from the current request if HTTP or HTTPS
should be used. To force a protocol (for example if using without a request),
use the ``ABSOLUTE_URL_PROTOCOL`` setting::

  ABSOLUTE_URL_PROTOCOL = 'https'
