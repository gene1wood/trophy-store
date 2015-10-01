import logging

from django.forms import ModelForm
from django.shortcuts import render
import django.core.urlresolvers
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

# from session_csrf import anonymous_csrf

# from django import forms

from models import Certificate
import utils

logger = logging.getLogger(__name__)


class CertificateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(CertificateForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        # If the request has already been submitted then only "destinations"
        # should be mutable
        self.read_only_fields = ['validity',
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
                          'ev']
        if instance and not instance.state == '':
            for field in self.read_only_fields:
                self.fields[field].widget.attrs['readonly'] = True

    def clean(self):
        super(CertificateForm, self).clean()
        instance = getattr(self, 'instance', None)
        if instance and not instance.state == '':
            for field in self.read_only_fields:
                self.cleaned_data[field] = instance.__dict__[field]
        return self.cleaned_data

    class Meta:
        model = Certificate
        fields = ['common_name',
                  'sans',
                  'validity',
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
#                   'telephone',
#                   'org_contact_job_title',
#                   'org_contact_firstname',
#                   'org_contact_lastname',
#                   'org_contact_email',
#                   'org_contact_telephone',
#                   'org_contact_telephone_ext',
                  'ev',
                  'business_unit',
                  'destinations']


def is_mozillian(user):
    return user.is_authenticated() and user.email.endswith('@mozilla.com')

def index(request, template='trophystore/home.html'):
    """Main view."""
    data = {'is_authorized': utils.is_authorized(request.user)}
    return render(request, template, data)

from django.http import HttpResponse
from django.conf import settings, global_settings
@user_passes_test(utils.is_authorized)
def showsettings(request):
    settings._setup()

    def module_to_dict(module, omittable=lambda k: k.startswith('_')):
        """Converts a module namespace to a Python dictionary."""
        return {k: repr(v) for k, v in module.__dict__.items() if not omittable(k)}

    user_settings = module_to_dict(settings._wrapped)
    default_settings = module_to_dict(global_settings)

    output = []
    for key in sorted(user_settings):
        if key not in default_settings:
            output.append("%s = %s  ###" % (key, user_settings[key]))
        elif user_settings[key] != default_settings[key]:
            output.append("%s = %s" % (key, user_settings[key]))
        else:
            output.append("### %s = %s" % (key, user_settings[key]))
    logger.debug('\n'.join(output))
    html = "<html><body>Check the log</body></html>"
    return HttpResponse(html)    

@user_passes_test(utils.is_authorized)
def cacheclear(request):
    from django.core.cache import cache
    cache.clear()
    return redirect(django.core.urlresolvers.reverse('index'))

@user_passes_test(utils.is_authorized)
def request(request, template='trophystore/request.html'):
    """Request a certificate"""
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            new_cert = form.save()
            request_id = utils.submit_certificate_request(new_cert)
            if request_id:
                logger.debug("Certificate request_id : %s" % request_id)
                new_cert.request_id = request_id
                new_cert.state = Certificate.REQUESTED
                new_cert.save()
                messages.add_message(request,
                                     messages.INFO,
                                     'Certificate request for %s submitted '
                                     'successfully' % new_cert.common_name)
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     'Certificate request for %s failed'
                                     % new_cert.common_name)
                new_cert.delete()
            return redirect(django.core.urlresolvers.reverse('request'))
    else:
        form = CertificateForm()

    data = {'form': form}
    return render(request, template, data)


@user_passes_test(utils.is_authorized)
def display_list(request, template='trophystore/display_list.html'):
    """Display a list of requests"""
    if request.method == 'POST' and 'action' in request.POST:
        certificate = Certificate.objects.get(pk=request.POST['id'])
        if request.POST['action'] == 'approve':
            logger.info('Approve %s' % request.POST['id'])

            result = utils.approve_request(certificate)
            if result:
                certificate.order_id = result
                certificate.state = Certificate.APPROVED
                certificate.save()
                messages.add_message(request, messages.INFO,
                                     'Certificate %s approved'
                                     % certificate.common_name)
            else:
                messages.add_message(request, messages.ERROR,
                                     'Certificate %s approval failed'
                                     % certificate.common_name)
            return redirect(django.core.urlresolvers.reverse('display_list'))
        elif request.POST['action'] == 'reject':
            logger.info('Reject %s' % request.POST['id'])
            result = utils.reject_request(certificate)
            if result:
                certificate.state = Certificate.REJECTED
                certificate.save()
                messages.add_message(request, messages.INFO,
                                     'Certificate %s rejected'
                                     % certificate.common_name)
            else:
                messages.add_message(request, messages.ERROR,
                                     'Certificate %s rejection failed'
                                     % certificate.common_name)
            return redirect(django.core.urlresolvers.reverse('display_list'))
        else:
            logger.error('Unexpected submission of %s in display'
                         % request.POST['action'])
            return redirect(django.core.urlresolvers.reverse('display_list'))

    else:
        logger.debug("Request is %s" % request.POST)
        data = {'certificates': Certificate.objects.all(
                                    ).filter(request_id__isnull=False)}
        return render(request, template, data)


@user_passes_test(utils.is_authorized)
def display_cert(request, cert_id, template='trophystore/display_cert.html'):
    """Display a single certificate"""

    # TODO : combine display_cert and request

    if request.method == 'POST':
        instance = Certificate.objects.get(id=cert_id)
        form = CertificateForm(instance=instance,
                               data=request.POST)
        if form.is_valid():
            new_cert = form.save()
            messages.add_message(request,
                                 messages.INFO,
                                 'Certificate %s updated'
                                 % new_cert.common_name)
            return redirect(django.core.urlresolvers.reverse('display_list'))
    else:
        certificate = Certificate.objects.get(pk=cert_id)
        form = CertificateForm(instance=certificate)
        data = {'form': form,
                'certificate': certificate}
        return render(request, template, data)


@user_passes_test(utils.is_authorized)
def deploy(request, template='trophystore/deploy.html'):
    certificates = Certificate.objects.all().filter(
                       state__exact=Certificate.APPROVED)

    # TODO : Move this to a celery task to passively poll for new approved
    #        certs in the background
    # http://www.celeryproject.org/
    data = {}
    if len(certificates) == 0:
        messages.add_message(request,
                             messages.INFO,
                             'There are no pending approved certificates')

        return render(request, template, data)

    fetched_certs = []
    for certificate in certificates:
        if utils.fetch_certificate(certificate):
            logger.debug("Certificate %s is ready to be fetched"
                         % certificate.common_name)
            fetched_certs.append(certificate.id)
        else:
            logger.debug("Certificate %s is not available to be fetched"
                         % certificate.common_name)

    if len(fetched_certs) == 0:
        messages.add_message(request,
                             messages.INFO,
                             'There are %s pending approved certificates but '
                             'none have been issued yet'
                             % len(certificates))
        return render(request, template, data)

    for certificate in [x for x in certificates if x.id in fetched_certs]:
        result = utils.deploy_certificate(certificate)
        if False in result.values():
            messages.add_message(
                 request,
                 messages.ERROR,
                 'Certificate %s deployed to "%s" but failed to deploy to "%s"'
                 % (certificate.common_name,
                    [x for x in result.keys() if result[x]],
                    [x for x in result.keys() if not result[x]]))
            # TODO update state to partially deployed, deal with this case
        else:
            certificate.state = Certificate.DEPLOYED
            certificate.save()
            messages.add_message(request,
                                 messages.INFO,
                                 'Certificate %s deployed to "%s"'
                                 % (certificate.common_name,
                                    [x for x in result.keys()]))
    return render(request, template, data)
