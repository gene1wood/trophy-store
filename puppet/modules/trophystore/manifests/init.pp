# == Class: trophystore
#
# Deploy an instance of Trophy Store
#
# === Parameters
#
# Document parameters here.
#
# [*db_password*]
#   The MySQL database user password.
#
# [*db_user*]
#   The MySQL database user username. Default : `trophystore_user`
#
# [*db_root_password*]
#   The MySQL database root user password.
#
# [*hmac_secret*]
#   A secrete value to enable HMAC signatures and should be a unique
#   unpredictable value. https://pypi.python.org/pypi/djangohmac
#
# [*django_secret*]
#   A secrete value to enable cryptographic signing and should be a unique
#   unpredictable value. https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
#
# [*ssl_cert_content*]
#   A string containing an x509 public certificate in PEM format
#
# [*ssl_key_content*]
#   A string containing an x509 private key in PEM format
#
# [*ssl_chain_content*]
#   A string containing concatenated x509 public certificates in PEM format
#
# [*site_name*]
#   DNS name of the site
#
# [*app_config*]
#   Hash of Trophy Store application configuration
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
class trophystore (
        $db_password = undef,
        $db_user = 'trophystore_user',
        $db_root_password = undef,
        $hmac_secret = undef,
        $django_secret = undef,
        $ssl_cert_content = undef,
        $ssl_key_content = undef,
        $ssl_chain_content = undef,
        $site_name = undef,
        $app_config = undef,
        ) {
    anchor { 'trophystore::begin': } ->
    class { '::trophystore::install': } ->
    class { '::trophystore::install-with-pip': } ->
    class { '::trophystore::config': } ~>
    class { '::trophystore::service': } ->
    anchor { 'trophystore::end': }
}
