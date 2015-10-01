class trophystore::install-with-pip inherits trophystore {

    # Normally these dependencies are handled with the vendor submodule
    # Which you get by using the "--recursive" argument when you clone trophy-store
    #
    # git clone --recursive https://github.com/gene1wood/trophy-store /opt/trophy-store
    #
    # If you don't do that, you can add these into the virtualenv with pip
    #
    # http://playdoh.readthedocs.org/en/latest/packages.html#the-vendor-library

    # package { 'gcc':}
    package { 'git': }

    exec {'install funfactory':
        command => '/opt/trophy-store/.virtualenv/bin/pip install funfactory',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/funfactory',
        require => Exec['create virtualenv'],
    }
    exec {'install Django':
        command => '/opt/trophy-store/.virtualenv/bin/pip install Django',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/django',
        require => Exec['create virtualenv'],
    }
    exec {'install django_sha2':
        command => '/opt/trophy-store/.virtualenv/bin/pip install django_sha2',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/django_sha2',
        require => [Exec['create virtualenv'],
                    Exec['install Django']],
    }
    exec {'install django-mozilla-product-details':
        command => '/opt/trophy-store/.virtualenv/bin/pip install git+git://github.com/mozilla/django-mozilla-product-details',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/product_details',
        require => [Exec['create virtualenv'],
                    Exec['install Django'],
                    Package['git']],
    }
    exec {'install django-session-csrf':
        command => '/opt/trophy-store/.virtualenv/bin/pip install django-session-csrf',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/session_csrf',
        require => [Exec['create virtualenv'],
                    Exec['install Django']],
    }
    exec {'install django_nose':
        command => '/opt/trophy-store/.virtualenv/bin/pip install django_nose',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/django_nose',
        require => [Exec['create virtualenv'],
                    Exec['install Django']],
    }
    exec {'install django-celery':
        command => '/opt/trophy-store/.virtualenv/bin/pip install django-celery',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/djcelery',
        require => [Exec['create virtualenv'],
                    Package['gcc'] ]
    }
    exec {'install commonware':
        command => '/opt/trophy-store/.virtualenv/bin/pip install commonware',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/commonware',
        require => Exec['create virtualenv'],
    }
    exec {'install django-browserid':
        command => '/opt/trophy-store/.virtualenv/bin/pip install git+git://github.com/mozilla/django-browserid.git',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/django_browserid',
        require => [Exec['create virtualenv'],
                   Package['git']],
    }
    exec {'install django-cronjobs':
        command => '/opt/trophy-store/.virtualenv/bin/pip install django-cronjobs',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/cronjobs',
        require => Exec['create virtualenv'],
    }
    exec {'install tower':
        command => '/opt/trophy-store/.virtualenv/bin/pip install tower',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/tower',
        require => Exec['create virtualenv'],
    }
    exec {'install Babel':
        command => '/opt/trophy-store/.virtualenv/bin/pip install Babel',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/babel',
        require => Exec['create virtualenv'],
    }
    exec {'install django_compressor':
        command => '/opt/trophy-store/.virtualenv/bin/pip install django_compressor',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/compressor',
        require => Exec['create virtualenv'],
    }
    exec {'install jingo':
        command => '/opt/trophy-store/.virtualenv/bin/pip install jingo',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/jingo',
        require => [Exec['create virtualenv'],
                    Exec['install jinja2']],
    }
    exec {'install django-mobility':
        command => '/opt/trophy-store/.virtualenv/bin/pip install django-mobility',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/mobility',
        require => [Exec['create virtualenv'],
                    Exec['install Django']],
    }
    exec {'install bleach':
        command => '/opt/trophy-store/.virtualenv/bin/pip install bleach',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/bleach',
        require => Exec['create virtualenv'],
    }
    exec {'install cef':
        command => '/opt/trophy-store/.virtualenv/bin/pip install cef',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/cef.py',
        require => Exec['create virtualenv'],
    }
    exec {'install nuggets':
        command => '/opt/trophy-store/.virtualenv/bin/pip install git+git://github.com/mozilla/nuggets.git',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/dictconfig.py',
        require => [Exec['create virtualenv'],
                   Package['git']],
    }
    exec {'install trophystore':
        command => '/opt/trophy-store/.virtualenv/bin/pip install /opt/src/trophystore',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/trophystore',
        require => [Exec['create virtualenv'],
                    Exec['install boto'],
                    Exec['install Django'],
                    Exec['install jinja2'],
                    Exec['install MySQL-python'],
                    Exec['install pyOpenSSL'],
                    Exec['install PyYAML'],
                    Exec['install django-browserid']],
    }
}