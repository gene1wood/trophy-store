# Trophy Store

Trophy Store seeks to simplify the process that Mozillians go through when
requesting new or renewing existing SSL certificates by automating the 
process from request through to deployment.

Quick start
-----------

1. Add "trophystore" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'trophystore',
    )

2. Include the Trophy Store URLconf in your project urls.py like this::

    url(r'^/', include('trophystore.urls')),

3. Run `python manage.py migrate` to create the Trophy Store models.

4. Visit http://127.0.0.1:8000/ to user the app.