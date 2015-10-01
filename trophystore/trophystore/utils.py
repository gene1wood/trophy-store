import requests
from OpenSSL import crypto
import json
import logging
import os.path
import yaml
import boto.iam
import sys

logger = logging.getLogger(__name__)

API_SITE = 'https://www.digicert.com/clients/rest/api'
GROUP_NAME = 'TrophyStore'

def dump_rsa_privatekey(pkey):
    """
    Dump a private rsa key to a buffer

    :param pkey: The PKey to dump
    :return: The buffer with the dumped key in
    :rtype: :py:data:`str`
    """

    # Based off of https://github.com/pyca/pyopenssl/blob/27398343217703c5261e67d6c19dda89ba559f1b/OpenSSL/crypto.py#L1418-L1466

    from OpenSSL._util import (
        ffi as _ffi,
        lib as _lib,
        exception_from_error_queue as _exception_from_error_queue)

    from OpenSSL import crypto
    from functools import partial

    class Error(Exception):
        """
        An error occurred in an `OpenSSL.crypto` API.
        """

    _raise_current_error = partial(_exception_from_error_queue, Error)

    bio = crypto._new_mem_buf()

    cipher_obj = _ffi.NULL

    rsa = _lib.EVP_PKEY_get1_RSA(pkey._pkey)
    helper = crypto._PassphraseHelper(crypto.FILETYPE_PEM, None)
    result_code = _lib.PEM_write_bio_RSAPrivateKey(
        bio, rsa, cipher_obj, _ffi.NULL, 0,
        helper.callback, helper.callback_args)
    helper.raise_if_problem()

    if result_code == 0:
        _raise_current_error()

    return crypto._bio_to_string(bio)


def get_config():
    config_filename = '/etc/trophystore/trophystore.yaml'
    try:
        with open(os.path.expanduser(config_filename)) as f:
            data = yaml.load(f)
            if ('certificate_authorities' in data and
                type(data['certificate_authorities']) == dict and
                len(data['certificate_authorities']) >= 1):
                return data
            else:
                logger.error("Config file %s is missing critical values"
                             % config_filename)
                return False
    except:
        logger.error("Unable to open config file %s" % config_filename)
        return False

def is_authorized(user):
    config = get_config()
    if not config or ('users' not in config) or type(config['users']) != list:
        return False
    if user.is_authenticated():
        logger.error("%s is_authenticated %s and %s in config['users'] %s" % 
                     (user.email, user.is_authenticated(), user.email, user.email.lower() in [x.lower() for x in config['users']]))
        return user.email.lower() in [x.lower() for x in config['users']]
    else:
        return False


def get_digicert_credentials(account_name=None):
    config = get_config()
    if not config:
        return False
    if account_name is None:
        # If there are multiple digicert accounts and no account_name
        # is specified, the first one found is used
        account_name = next(
            (x for x in config['certificate_authorities']
             if config['certificate_authorities'][x]['type'] == 'digicert'),
                            None)
    if account_name not in config['certificate_authorities']:
        logger.error("Unable to find %s in config : %s"
                     % (account_name, config['certificate_authorities']))
        return False
    return (config['certificate_authorities'][account_name]['account_id'],
            config['certificate_authorities'][account_name]['api_key'])


def call_digicert_api(url_suffix,
                      data,
                      method='POST'):
    headers = {'content-type': 'application/vnd.digicert.rest-v1+json',
               'User-Agent': 'trophystore/1.0.0'}
    url = API_SITE + url_suffix

    logger.debug("Calling Digicert API with method %s at url %s with data %s"
                 % (method, url, data))

    digicert_credentials = get_digicert_credentials()

    if not digicert_credentials:
        return [False,
                "Unable to read digicert credentials from config",
                {'errors': [{'code': 0,
                             'description': ''}]
                }
               ]
    logger.debug("Using creds %s and %s" % digicert_credentials)

    response = requests.request(
        method,
        url,
        data=json.dumps(data) if not data is None else None,
        headers=headers,
        auth=digicert_credentials)
    status_code_map = {
        200: [True, ''],
        201: [True, 'Created'],
        204: [True, 'No content'],
        400: [False, 'General client error'],
        401: [False, 'Invalid account ID and API key combination'],
        403: [False, 'API key missing permissions required'],
        404: [False, 'Page does not exist'],
        405: [False, 'Method not found'],
        406: [False, 'Requested content type or API version is invalid']}

    logger.debug("%s : Digicert API response code %s : '%s' and body %s"
                  % (status_code_map[response.status_code][0],
                     response.status_code,
                     status_code_map[response.status_code][1],
                     response.text))

    if response.status_code in [200, 201, 204, 400, 401, 404, 405, 406]:
        return status_code_map[response.status_code] + [response.json()]
    elif response.status_code in [403]:
        return (status_code_map[response.status_code] +
                [{'errors': [{'code': response.status_code,
                              'description': response.text()}]}])
    else:
        return [False,
                'API is unavailable',
                {'errors': [{'code': response.status_code,
                             'description': response.text()}]
                }
               ]


def generate_csr(certificate):
    pkey_type = crypto.TYPE_RSA
    pkey_bits = 2048
    digest_type = 'md5'
    pkey = crypto.PKey()
    pkey.generate_key(pkey_type, pkey_bits)
    #certificate.private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey)
    #certificate.save()

    req = crypto.X509Req()
    subj = req.get_subject()
    for key in certificate.openssl_arg_map:
        if not getattr(certificate, key) in [None, '']:
            setattr(subj,
                    certificate.openssl_arg_map[key],
                    getattr(certificate, key))

    # TODO : add sans : http://stackoverflow.com/a/25714864/168874

    # We are not adding oids like streetAddress and postalCode to the CSR

    req.set_pubkey(pkey)
    req.sign(pkey, digest_type)
    #certificate.certificate_request = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    #certificate.save()
    return (dump_rsa_privatekey(pkey),
            crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))


def submit_certificate_request(certificate):
    data = {}
    (private_key, csr) = generate_csr(certificate)
    certificate.private_key = private_key
    certificate.csr = csr
    certificate.save()
    for key in certificate.__dict__:
        if type(getattr(certificate, key)) == list:
            data[key] = ', '.join(getattr(certificate, key))
        elif key in ['validity',
                     'common_name',
                     'sans',
                     'server_type',
                     'signature_hash',
                     'org_unit',
                     'org_name',
                     'org_addr1',
                     'org_addr2',
                     'org_city',
                     'org_state',
                     'org_zip',
                     'org_country',
                     'ev',
                     'csr',
                     'business_unit']:
            data[key] = getattr(certificate, key)
        else:
            continue

    response = call_digicert_api('/enterprise/certificate/ssl',
                                 data)
    logger.debug(response)
    if response[0]:
        return response[2]['request_id']
    else:
        return False


def approve_request(certificate):
    response = call_digicert_api(
                     '/request/%s' % certificate.request_id,
                     {'note': 'Certificate request approved by trophystore'},
                     'APPROVE')
    if response[0]:
        return response[2]['order_id']
    else:
        return False


def reject_request(certificate):
    response = call_digicert_api(
                     '/request/%s' % certificate.request_id,
                     {'note': 'Certificate request rejected by trophystore'},
                     'REJECT')
    if response[0]:
        return True
    else:
        return False


def fetch_certificate(certificate):
    response = call_digicert_api(
                     '/order/%s/certificate' % certificate.order_id,
                     None,
                     'GET')
    if response[0]:
        certificate.serial = response[2]['serial']
        certificate.certificate = response[2]['certs']['certificate']
        certificate.intermediate_cert = response[2]['certs']['intermediate']
        certificate.root_cert = response[2]['certs']['root']
        certificate.pkcs7 = response[2]['certs']['pkcs7']
        certificate.save()
        return True
    else:
        return False


def get_aws_credentials(destination):
    import boto.sts
    conn_sts = boto.sts.connect_to_region('us-east-1')
    return conn_sts.assume_role(destination.iam_role_arn,
                                'TrophyStoreSession')


def install_certificate_in_aws(destination, certificate):
    path = '/'
    region = 'universal'  # The region used when interacting with boto.iam
    assumed_role = get_aws_credentials(destination)
    conn_iam = boto.iam.connect_to_region(
                  region,
                  aws_access_key_id=assumed_role.credentials.access_key,
                  aws_secret_access_key=assumed_role.credentials.secret_key,
                  security_token=assumed_role.credentials.session_token)

    existing_certs = (conn_iam.list_server_certs(path_prefix=path)
                      ['list_server_certificates_response']
                      ['list_server_certificates_result']
                      ['server_certificate_metadata_list'])

    if certificate.common_name in [x['server_certificate_name']
                                   for x
                                   in existing_certs]:
        logger.error("Certificate already exists in %s" % destination.record)

    request_params = {
              'cert_name': certificate.common_name.replace("\r", ""),
              'cert_body': certificate.certificate.replace("\r", ""),
              'private_key': certificate.private_key.replace("\r", ""),
              'cert_chain': certificate.intermediate_cert.replace("\r", "") +
                            certificate.root_cert.replace("\r", ""),
              'path': path}

    logger.debug("Submitting request to AWS to install certificate : %s"
                 % json.dumps(request_params, indent=4))
    return conn_iam.upload_server_cert(**request_params)


def install_certificate_in_stingray(destination, certificate):
    url = "https://%s:9070/api/tm/3.0/config/active" % destination.zlb_hostname
    headers = {'content-type': 'application/json'}
    client = requests.Session()
    client.auth = (destination.username, destination.password)
    client.verify = False  # This is to accommodate stingrays with self-signed certs

    properties = {'note': certificate.common_name.replace("\r", ""),
                  'private': certificate.private_key.replace("\r", ""),
                  'public': certificate.certificate.replace("\r", "") +
                            certificate.intermediate_cert.replace("\r", "") +
                            certificate.root_cert.replace("\r", ""),
                  'request' : certificate.certificate_request.replace("\r", "")}
    data = {'properties': {'basic': properties}}
    response = client.put(url + "/ssl/server_keys/" + certificate.common_name.replace("\r", ""),
                          data=json.dumps(data),
                          headers=headers)
    return response

def deploy_certificate(certificate):
    result = {}
    for destination in certificate.destinations.all():
        if destination.type == 'zlb':
            result[destination.name] = install_certificate_in_stingray(
                    destination,
                    certificate)
        elif destination.type == 'aws':
            result[destination.name] = install_certificate_in_aws(
                    destination,
                    certificate)
        else:
            logger.error("Unknown destination type %s"
                      % destination.type)
            result = False
    return result            

def manage():
    sys.path.append("/etc/trophystore")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
