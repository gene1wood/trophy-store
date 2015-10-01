# == Class: trophystore::install
#
# Full description of class trophystore::install here.
#
# === Parameters
#
# Document parameters here.
#
# [*sample_parameter*]
#   Explanation of what this parameter affects and what it defaults to.
#   e.g. "Specify one or more upstream ntp servers as an array."
#
# === Variables
#
# Here you should define a list of variables that this module would require.
#
# [*sample_variable*]
#   Explanation of how this variable affects the funtion of this class and if it
#   has a default. e.g. "The parameter enc_ntp_servers must be set by the
#   External Node Classifier as a comma separated list of hostnames." (Note,
#   global variables should not be used in preference to class parameters  as of
#   Puppet 2.6.)
#
# === Examples
#
#  class { trophystore:
#    servers => [ 'pool.ntp.org', 'ntp.local.company.com' ]
#  }
#
# === Authors
#
# Gene Wood <gene_wood@cementhorizon.com>
#
# === Copyright
#
# Copyright 2015 Your name here, unless otherwise noted.
#
class trophystore::install inherits trophystore {

    file { '/opt/trophy-store':
        ensure => 'directory',
        owner  => 'root',
        group  => 'root',
        mode   => 755,
    }
    
    if $operatingsystemmajrelease == 6 {
        $db_package_name = 'mysql-server'
        $db_devel_package_name = 'mysql-devel'
        $db_service_name = 'mysqld'        
        $db_override_options = {}
        $python_devel_package_name = 'python27-python-devel'
        $pip_package_name = 'python-pip'

        class { 'scl::python27': }

        package { 'python27': 
            require => Class['scl::python27'],
        }
        
        package { 'python27-mod_wsgi':
            require => Package['python27'],
        }

        exec { 'install pip':
            command => '/usr/bin/scl enable python27 \'curl https://bootstrap.pypa.io/get-pip.py | python\'',
            creates => '/opt/rh/python27/root/usr/lib/python2.7/site-packages/pip',
            require => Class['scl::python27'],
        }

        exec { 'install virtualenv':
            command => '/usr/bin/scl enable python27 \'pip install virtualenv\'',
            creates => '/opt/rh/python27/root/usr/lib/python2.7/site-packages/virtualenv.py',
            require => [Exec['install pip'],
                        Class['scl::python27']],
        }
        exec {'create virtualenv':
            command => '/usr/bin/scl enable python27 \'virtualenv /opt/trophy-store/.virtualenv\'',
            creates => '/opt/trophy-store/.virtualenv',
            require => [Exec['install virtualenv'],
                        Class['scl::python27'],
                        File['/opt/trophy-store']],
        }
    }
    elsif $operatingsystemmajrelease == 7 {
        # In CentOS 7 Python 2.7 is the default version of python
        
        package { 'epel-release':
            source => 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'
        }

        $db_package_name = 'mariadb-server'
        $db_devel_package_name = 'mariadb-devel'
        $db_service_name = 'mariadb'
        $db_override_options = {
            'mysqld' => {
                'log-error' => '/var/log/mariadb/mariadb.log',
                'pid-file' => '/var/run/mariadb/mariadb.pid',
            },
            'mysqld_safe' => {
                'log-error' => '/var/log/mariadb/mariadb.log'
            },
        }
        $python_devel_package_name = 'python-devel'
        package { 'python': }
        package { 'python-pip':
            require => Package['epel-release'],
        }

        package { 'virtualenv':
            provider => 'pip',
            require => Package['python-pip'],
        }

        exec {'create virtualenv':
            command => '/usr/bin/virtualenv /opt/trophy-store/.virtualenv',
            creates => '/opt/trophy-store/.virtualenv',
            require => [Package['virtualenv'],
                        File['/opt/trophy-store']],
        }
    }

    class { '::mysql::server':
        root_password => $db_root_password,
        users         => {
            "${db_user}@localhost" => {
                ensure                   => 'present',
                password_hash            => mysql_password($db_password)
            }
        },
        package_name => $db_package_name,
        # package_ensure => '5.5.37-1.el7_0',  # workaround this bug in mariadb 5.5.40 https://bugzilla.redhat.com/show_bug.cgi?id=1166603
        service_name => $db_service_name,
        override_options => $db_override_options,
        databases => {
            'trophystore' => {
                ensure => 'present',
                charset => 'utf8',
            }
        },
        grants => {
            "${db_user}@localhost/trophystore.*" => {
                ensure     => 'present',
                options    => ['GRANT'],
                privileges => ['ALL'],
                table      => 'trophystore.*',
                user       => "${db_user}@localhost",
            }
        },
    }

    package { 'gcc':}
    package { 'python-devel':
        name => $python_devel_package_name,
        require => Package['gcc']
    }
    package { 'mariadb-devel':
        name => $db_devel_package_name,
        # ensure => '5.5.37-1.el7_0',  # workaround this bug in 5.5.40 https://bugzilla.redhat.com/show_bug.cgi?id=1166603
        require => Class['mysql::server'],
    }
    package { 'libffi-devel':}
    package { 'openssl-devel':}
    package { 'libyaml-devel':}

    # The packages are installed into the virtualenv with `exec` in order to
    # work around https://tickets.puppetlabs.com/browse/PUP-1062

    exec {'install MySQL-python':
        command => '/opt/trophy-store/.virtualenv/bin/pip install MySQL-python',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/MySQLdb',
        require => [Exec['create virtualenv'],
                    Class['mysql::server'],
                    Package['python-devel'] ]
    }
    exec {'install python-bcrypt':
        command => '/opt/trophy-store/.virtualenv/bin/pip install python-bcrypt',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/bcrypt',
        require => [ Exec['create virtualenv'], 
                     Package['python-devel']],
    }
    exec {'install boto':
        command => '/opt/trophy-store/.virtualenv/bin/pip install boto',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/boto',
        require => Exec['create virtualenv'],
    }

    # It appears that pyOpenSSL 0.14 and newer (e.g. 0.15.1) cause a segfault if selinux is enabled
    # due to the httpd_execmem boolean

    exec {'disable httpd_execmem':
        command => "/sbin/setsebool -P httpd_execmem 1",
        # /sys/fs/selinux/booleans/httpd_execmem syntax
        # "%d %d", current value , pending value
        onlyif => "/usr/bin/test `/bin/cut --delimiter=\" \" --fields=1 /sys/fs/selinux/booleans/httpd_execmem` -ne 1",
    }

    exec {'install pyOpenSSL':
        command => '/opt/trophy-store/.virtualenv/bin/pip install pyOpenSSL',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/OpenSSL',
        require => [ Exec['create virtualenv'],
                     Exec['disable httpd_execmem'],
                     Package['libffi-devel'],
                     Package['gcc'],
                     Package['openssl-devel'] ],
    }

    exec {'install PyYAML':
        command => '/opt/trophy-store/.virtualenv/bin/pip install PyYAML',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/yaml',
        require => [ Exec['create virtualenv'], 
                     Package['gcc'],
                     Package['libyaml-devel'] ],
    }

    exec {'install jinja2':
        command => '/opt/trophy-store/.virtualenv/bin/pip install jinja2',
        creates => '/opt/trophy-store/.virtualenv/lib/python2.7/site-packages/jinja2',
        require => [Exec['create virtualenv'],
                    Package['gcc'] ]
    }

    class { 'apache':
        default_mods        => false,
        default_confd_files => false,
    }
}
