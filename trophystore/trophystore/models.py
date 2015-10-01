from django.db import models
import ast
# from utils import get_config


class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value, None)

class CertDestinations(models.Model):
    name = models.CharField(max_length=255,
         help_text="Name of the destination")
    iam_role_arn = models.CharField(max_length=255,
         help_text="ARN of the IAM Role to assume when accessing the AWS ELB"
         "destination.")
    zlb_hostname = models.CharField(max_length=253,
         help_text="DNS name of the Zeus load balancer destination")
    username = models.CharField(max_length=255,
         help_text="Username to access the destination")
    password = models.CharField(max_length=255,
         help_text="Password to access the destination")

    DESTINATION_TYPE_CHOICES = (
                     ('', 'None'),
                     ('elb', 'AWS ELB'),
                     ('zlb', 'Zeus Load Balancer'),
                     ('usr', 'The user')
                    )
    
    type = models.CharField(max_length=3,
                             choices=DESTINATION_TYPE_CHOICES,
                             default='',
                             blank=True)
    
    def __unicode__(self):
        return self.name
    

class Certificate(models.Model):
    common_name = models.CharField(max_length=255,
         help_text="Primary DNS name for the certificate")
    sans = ListField(blank=True,
         help_text="List of alternative DNS names for the certificate")
    validity = models.PositiveSmallIntegerField(default=1,
        help_text="Number of years certificate is valid for")
    server_type = models.SmallIntegerField(blank=True, default="-1",
        help_text="2: Apache, 45: Nginx, -1: Other")
    signature_hash = models.CharField(max_length=255,
        blank=True, help_text="sha1 or sha256", default="sha256")
    org_unit = models.CharField(max_length=255,
        blank=True)
    org_name = models.CharField(max_length=255,
        help_text="Mozilla Foundation or Mozilla Corporation")
    org_addr1 = models.CharField(max_length=255,
        default="331 E Evelyn Ave")
    org_addr2 = models.CharField(max_length=255, blank=True)
    org_city = models.CharField(max_length=255,
        default="Mountain View")
    org_state = models.CharField(max_length=255,
        default="CA")
    org_zip = models.CharField(max_length=255,
        default="94041")
    org_country = models.CharField(max_length=255,
        default="US")
    # telephone = models.CharField(max_length=255)
    # org_contact_job_title = models.CharField(max_length=255)
    # org_contact_firstname = models.CharField(max_length=255)
    # org_contact_lastname = models.CharField(max_length=255)
    # org_contact_email = models.EmailField()
    # org_contact_telephone = models.CharField(max_length=255)
    # org_contact_telephone_ext = models.CharField(max_length=255)
    ev = models.BooleanField(default=False)
    destinations = models.ManyToManyField(CertDestinations)

    private_key = models.TextField(max_length=16384, blank=True)
    certificate_request = models.TextField(max_length=16384, blank=True)
    request_id = models.IntegerField(null=True)
    order_id = models.IntegerField(null=True)
    serial = models.TextField(max_length=32, blank=True)
    certificate = models.TextField(max_length=16384, blank=True)
    intermediate_cert = models.TextField(max_length=2097152, blank=True)
    root_cert = models.TextField(max_length=16384, blank=True)
    pkcs7 = models.TextField(max_length=2097152, blank=True)

    business_unit = models.CharField(max_length=255,
        blank=True)

    STATE_CHOICES = (
                     ('', 'None'),
                     ('req', 'Requested'),
                     ('rej', 'Rejected'),
                     ('app', 'Approved'),
                     ('iss', 'Issued'),
                     ('dep', 'Deployed')
                    )

    REQUESTED = 'req'
    REJECTED = 'rej'
    APPROVED = 'app'
    ISSUED = 'iss'
    DEPLOYED = 'dep'

    state = models.CharField(max_length=3,
                             choices=STATE_CHOICES,
                             default='',
                             blank=True)

    # RFC 5280
    openssl_arg_map = {'common_name': 'commonName',
                       'org_city': 'localityName',
                       'org_country': 'countryName',
                       'org_unit': 'organizationalUnitName',
                       'org_name': 'organizationName',
                       'org_state': 'stateOrProvinceName'}

    def __unicode__(self):
        return self.common_name
