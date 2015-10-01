class trophystore::config inherits trophystore {
    file { '/etc/trophystore':
        ensure => directory,
        owner => 'root',
        group => 'apache',
        mode => '0640',
    }
    
    file { '/etc/trophystore/local_settings.py':
        owner => 'root',
        group => 'apache',
        mode => '0640',
        content => template('trophystore/local_settings.py.erb'),
        require => File['/etc/trophystore'],
        notify => Service['httpd'],
    }
    
    file { '/etc/trophystore/trophystore.yaml.dist':
        owner => 'root',
        group => 'root',
        mode => '0640',
        source => 'puppet:///modules/trophystore/etc/trophystore/trophystore.yaml.dist'
    }

    file { '/etc/trophystore/trophystore.yaml':
        owner => 'root',
        group => 'apache',
        mode => '0640',
        content => inline_template("<%= @app_config.to_yaml + '\n' %>")
    }

    file { '/var/log/trophystore.log':
        ensure => file,
        owner => 'apache',
        group => 'apache',
        mode => '0640',
        selrole => 'object_r',
        seltype => 'httpd_log_t',
        seluser => 'system_u',
    }

    exec { 'apply db migrations':
        command => '/opt/trophy-store/.virtualenv/bin/trophystore-manage migrate',
        unless  => '/bin/bash -c \'echo "use trophystore; show tables;" | /opt/trophy-store/.virtualenv/bin/trophystore-manage dbshell | grep auth_user\'',
        require => [Exec['install trophystore'],
                    File['/etc/trophystore/local_settings.py'],
                    File['/etc/trophystore/trophystore.yaml'],
                    File['/var/log/trophystore.log']],
                    
    }

    file { '/etc/trophystore/wsgi.py':
        owner => 'root',
        group => 'apache',
        mode => '0640',
        source => 'puppet:///modules/trophystore/etc/trophystore/wsgi.py',
        notify => Service['httpd'],
    }

    $mod_wsgi_package_name = $operatingsystemmajrelease ? {
        6 => python27-mod_wsgi,
        7 => undef,
        default => under,
    }
    
    if $operatingsystemmajrelease == 6 {
        class { 'apache::mod::wsgi':
            wsgi_python_home   => '/opt/trophy-store/.virtualenv/',
            wsgi_python_path   => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages',
            package_name       => 'python27-mod_wsgi',
            mod_path           => 'python27-mod_wsgi.so',
        }
    }
    elsif $operatingsystemmajrelease == 7 {
        class { 'apache::mod::wsgi':
            wsgi_python_home   => '/opt/trophy-store/.virtualenv/',
            wsgi_python_path   => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages',
        }
    }    

    include 'apache::mod::ssl'

    $ssl_keys_dir = dirname($::apache::default_ssl_key)
    $ssl_key_filename = "${ssl_keys_dir}/${site_name}.key"
    $ssl_cert_filename = "${::apache::ssl_certs_dir}/${site_name}.crt"
    $ssl_chain_filename = "${::apache::ssl_certs_dir}/${site_name}.chain.crt"

    if $ssl_cert_content {
        file { $ssl_cert_filename:
            owner => 'root',
            group => 'root',
            mode  => '0644',
            content => $ssl_cert_content,
        }
    }

    if $ssl_key_content {
        file { $ssl_key_filename:
            owner => 'root',
            group => 'root',
            mode  => '0600',
            content => $ssl_key_content,
        }
    }

    if $ssl_chain_content {
        file { $ssl_chain_filename:
            owner => 'root',
            group => 'root',
            mode  => '0644',
            content => $ssl_chain_content,
        }
    }

    apache::vhost { $site_name:
        port    => '443',
        docroot => '/opt/trophy-store/wsgi/',  #???
        # log_level => 'debug',
        ssl => true,
        ssl_cert => $ssl_cert_content ? {
            undef => undef,
            default => $ssl_cert_filename
        },
        ssl_chain => $ssl_chain_content ? {
            undef => undef,
            default => $ssl_chain_filename
        },
        ssl_key => $ssl_key_content ? {
            undef => undef,
            default => $ssl_key_filename
        },
        wsgi_application_group      => '%{GLOBAL}',
        wsgi_daemon_process         => 'trophystore',
        wsgi_daemon_process_options => { 
            processes    => '2', 
            threads      => '15', 
            display-name => '%{GROUP}',
        },
        wsgi_import_script          => '/etc/trophystore/wsgi.py',
        wsgi_import_script_options  =>
            { process-group => 'trophystore', application-group => '%{GLOBAL}' },
        wsgi_process_group          => 'trophystore',
        wsgi_script_aliases         => { '/' => '/etc/trophystore/wsgi.py' },
        require => [File[$ssl_cert_filename],
                    File[$ssl_key_filename],
                    Class['apache::mod::wsgi'],
                    File['/etc/trophystore/wsgi.py'],
                    Exec['apply db migrations']],
    }
    
    # TODO : Install trophystore pip package (instead of expecting the source to be on disk
    # TODO : Load fixtures ( trophystore/fixtures/initial_data.json )
    # https://docs.djangoproject.com/en/1.7/howto/initial-data/

}