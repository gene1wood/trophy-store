# Trophy Store

## Operations

### How to launch Trophy Store

The `trophystore` puppet module will configure apache to surface Trophy Store over https.

To manually run Trophy Store

```
sudo /opt/trophy-store/.virtualenv/bin/python /opt/trophy-store/trophystore/manage.py runserver
```

### How to access Trophy Store

Browse to https://yourservername/

If you're running Trophy Store manually with `runserver`, browse to http://localhost:8000/

### How to rebuild the datastore

If a model is changed, then the DB needs to be rebuilt. Here's how to rebuild it and retain the data. Execute these steps as the `root` user

#### Export data and clear DB

```
cd /opt/trophy-store
.virtualenv/bin/python trophystore/manage.py dumpdata certmanager --format='json' --indent=4 --verbosity=1 > /tmp/dumpdata.json && \
.virtualenv/bin/python trophystore/manage.py sqlflush | .virtualenv/bin/python trophystore/manage.py dbshell
```

#### Update model

Change your model

#### Rebuild DB and import data

```
/opt/trophy-store/.virtualenv/bin/python manage.py migrate && \
/opt/trophy-store/.virtualenv/bin/python manage.py loaddata /tmp/dumpdata.json && \
rm /tmp/dumpdata.json
```

### Provisioning

On CentOS 7

See the included CloudFormation template

```
sudo rpm -ivh http://yum.puppetlabs.com/puppetlabs-release-el-7.noarch.rpm
sudo yum install -y puppet git

sudo bash -c "cat > /var/lib/hiera/common.yaml" <<End-of-message
---
trophystore::db_password: `openssl rand -base64 32`
trophystore::db_root_password: `openssl rand -base64 32`
trophystore::hmac_secret: `openssl rand -base64 32`
trophystore::django_secret: `openssl rand -base64 32`
End-of-message
sudo git clone https://github.com/gene1wood/trophy-store /opt/trophy-store
sudo ln -s /opt/trophy-store/puppet/modules/trophystore /etc/puppet/modules/trophystore
sudo puppet module install puppetlabs-stdlib 
sudo puppet module install puppetlabs-mysql
sudo puppet module install puppetlabs-apache
sudo puppet apply --modulepath=/etc/puppet/modules -e "include trophystore"
sudo /opt/trophy-store/.virtualenv/bin/python /opt/trophy-store/manage.py migrate
echo "Make sure to configure /etc/trophystore.yaml (you can use /etc/trophystore.yaml.dist as a guide)"
```

## AWS

### AWS Permissions Needed

The EC2 instance running Trophy Store will need to be able to assume an 
IAM role in any AWS accounts that you wish to be able to deploy certificates
into.

The way to accomplish this is two fold.

You must create an IAM role in each of the AWS accounts that you want to 
deploy certificates into. These accounts are the *trusting* accounts.

You must also create an IAM role in the AWS account that holds the ec2 
instance onto which trophy store will be deployed. This account is the
*trusted* account.

Here are instructions on how to create each of these roles.

#### The Trusting Account

Here's how to create the IAM role for the trusting account
```
#!/usr/bin/env python

# Set this to the ARN of the trusted account role
trusted_account_role_arn="arn:aws:iam::656532927350:role/TrophyStore"

import boto.iam
conn_iam = boto.iam.connect_to_region('universal')
role_name='TrophyStoreCertificateManager'
assume_role_policy_document = '''{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"",
      "Effect":"Allow",
      "Principal":{
        "AWS":"%s"
      },
      "Action":"sts:AssumeRole"
    }
  ]
}''' % trusted_account_role_arn
policy_document = '''{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Action":[
        "iam:UploadServerCertificate",
        "iam:ListServerCertificates",
        "iam:UpdateServerCertificate",
        "iam:GetServerCertificate"
      ],
      "Effect":"Allow",
      "Resource":"*"
    }
  ]
}'''

create_role_result = conn_iam.create_role(role_name=role_name,
                                          assume_role_policy_document=assume_role_policy_document)
put_role_policy_result = conn_iam.put_role_policy(role_name=role_name,
                                                  policy_name="ManipulateServerCertificates",
                                                  policy_document=policy_document)
```

#### The trusted account

```
import boto.iam
conn_iam = boto.iam.connect_to_region('universal')
role_name='TrophyStore'
instance_profile_name='TrophyStoreInstanceProfile'
assume_role_policy_document = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'''
policy_document = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "*"
    }
  ]
}'''

print(conn_iam.create_role(role_name=role_name,
                           assume_role_policy_document=assume_role_policy_document))
print(conn_iam.put_role_policy(role_name=role_name,
                               policy_name="TrophyStoreLaunchPerms",
                               policy_document=policy_document))
print(conn_iam.create_instance_profile(instance_profile_name))
print(conn_iam.add_role_to_instance_profile(instance_profile_name,
                                            role_name))
```

### Launching the Trophy Store EC2 Instance

Load the included CloudFormation template to provision an EC2 instance.

## Zeus Stingray Permissions Needed

### Enable the API
Make sure the API is enabled on the Stingray Traffic Manager by browsing to `System > Security` in the web UI
In the `REST API` section confirm that `rest!enabled` is set to `Yes`

### Create Stingray User Group

```
import requests
import json
username = "admin"
password = "password"
zlb_hostname = "zlb1.example.com"

url = "https://%s:9070/api/tm/3.0/config/active" % zlb_hostname
headers = {'content-type': 'application/json'}

client = requests.Session()
client.auth = (username, password)
client.verify = False

group_name = "TrophyStore"
permissions = [
    {u'access_level': u'none', u'name': u'Web_Cache'},
    {u'access_level': u'none', u'name': u'Pools!Edit!Load_Balancing'},
    {u'access_level': u'none', u'name': u'Java'},
    {u'access_level': u'full', u'name': u'Pools!Edit!SSL'},
    {u'access_level': u'none', u'name': u'Event_Log'},
    {u'access_level': u'none', u'name': u'SSL!DNSSEC_Keys'},
    {u'access_level': u'none', u'name': u'Monitors'},
    {u'access_level': u'none', u'name': u'Cloud_Credentials'},
    {u'access_level': u'none', u'name': u'Wizard'},
    {u'access_level': u'none', u'name': u'Pools!Edit!Persistence'},
    {u'access_level': u'none', u'name': u'Security'},
    {u'access_level': u'none', u'name': u'Support_Files'},
    {u'access_level': u'none', u'name': u'AFM'},
    {u'access_level': u'none', u'name': u'Shutdown'},
    {u'access_level': u'none', u'name': u'Traffic_Managers'},
    {u'access_level': u'none', u'name': u'Log_Viewer'},
    {u'access_level': u'none', u'name': u'Bandwidth'},
    {u'access_level': u'none', u'name': u'Request_Logs'},
    {u'access_level': u'none', u'name': u'SNMP'},
    {u'access_level': u'none', u'name': u'Reboot'},
    {u'access_level': u'none', u'name': u'Connections'},
    {u'access_level': u'none', u'name': u'Virtual_Servers'},
    {u'access_level': u'none', u'name': u'SOAP_API'},
    {u'access_level': u'none', u'name': u'Map'},
    {u'access_level': u'ro', u'name': u'Pools'},
    {u'access_level': u'none', u'name': u'Support'},
    {u'access_level': u'none', u'name': u'Global_Settings'},
    {u'access_level': u'none', u'name': u'Pools!Edit!Connection_Management'},
    {u'access_level': u'none', u'name': u'Catalog'},
    {u'access_level': u'none', u'name': u'SLM'},
    {u'access_level': u'none', u'name': u'SSL'},
    {u'access_level': u'none', u'name': u'Locations'},
    {u'access_level': u'none', u'name': u'Monitoring'},
    {u'access_level': u'none', u'name': u'Service_Protection'},
    {u'access_level': u'none', u'name': u'Persistence'},
    {u'access_level': u'none', u'name': u'Steelhead'},
    {u'access_level': u'none', u'name': u'Alerting'},
    {u'access_level': u'none', u'name': u'SSL!CAs'},
    {u'access_level': u'none', u'name': u'Pools!Edit!Bandwidth'},
    {u'access_level': u'none', u'name': u'Audit_Log'},
    {u'access_level': u'none', u'name': u'Backup'},
    {u'access_level': u'none', u'name': u'Pools!Edit!Monitors'},
    {u'access_level': u'none', u'name': u'Extra_Files'},
    {u'access_level': u'none', u'name': u'Statd'},
    {u'access_level': u'none', u'name': u'Help'},
    {u'access_level': u'none', u'name': u'Rate'},
    {u'access_level': u'none', u'name': u'Pools!Edit!Autoscaling'},
    {u'access_level': u'none', u'name': u'GLB_Services'},
    {u'access_level': u'none', u'name': u'Restart'},
    {u'access_level': u'none', u'name': u'Custom'},
    {u'access_level': u'none', u'name': u'Authenticators'},
    {u'access_level': u'none', u'name': u'Aptimizer'},
    {u'access_level': u'none', u'name': u'Rules'},
    {u'access_level': u'none', u'name': u'Traffic_IP_Groups'},
    {u'access_level': u'none', u'name': u'Draining'},
    {u'access_level': u'none', u'name': u'License_Keys'},
    {u'access_level': u'none', u'name': u'SSL!Client_Certs'},
    {u'access_level': u'none', u'name': u'Diagnose'},
    {u'access_level': u'none', u'name': u'Access_Management'},
    {u'access_level': u'full', u'name': u'SSL!SSL_Certs'},
    {u'access_level': u'none', u'name': u'Config_Summary'},
    {u'access_level': u'none', u'name': u'MainIndex'}
]

properties = {u'password_expire_time': 0, 
              u'description': u'Permissions to manipulate SSL certificates', 
              u'timeout': 30,
              u'permissions': permissions}
data = {'properties': {'basic': properties}}
response = client.put(url + "/user_groups/" + group_name,
                      data=json.dumps(data),
                      headers=headers)
```

### Create Stingray User

As creating users is not possible through the Stingray API, here are the steps to create the user through the web UI

1. Browse to https://zlb1.example.com:9090/apps/zxtm/index.fcgi?section=Access%20Management%3ALocalUsers
2. In the `Create new user` section fill in the values
  * Username : `trophystore`
  * Password : `somepassword`
  * Confirm password : `somepassword`
  * Group : `TrophyStore`
3. Click `Create User`

## Configuring
Use the example configuration file, `/etc/trophystore.yaml.dist` to create your configuration in `/etc/trophystore.yaml`. 
Use this file to define all of your certificate authorities and certificate destinations.

## Notes

### pyOpenSSL

pyopenssl is missing a function to export a private key in PKCS#1 format

As the binary distributed pyOpenSSL that you get when doing a `sudo apt-get install python-openssl` doesn't 
include the private modules we need to build and install it ourselves

pyopenssl depends on `libffi-dev` : `sudo apt-get install libffi-dev`

`pip install pyOpenSSL`

### yaml

Depends on python-yaml which requires libyaml-dev

`sudo apt-get install libyaml-dev`

`pip install PyYAML`

### funfactory

Depends on funfactory

`pip install funfactory`

### How to cleanup and delete an AWS deployed cert

If you've generated a cert and deployed it to an AWS account and want to clean it up here's how

```
certname='example.com'
import boto.iam
conn_iam = boto.iam.connect_to_region('universal', profile_name='my-aws-account-boto-profile-name')
print(conn_iam.delete_server_cert(certname))
```

## Deprecated Notes

These should no longer apply to this project

### Volo

Following instructions [here](https://github.com/ossreleasefeed/Sandstone#for-sites-based-on-playdoh) 
I've installed volo and node-less and run
```
cd trophystore/trophystore
volo add ossreleasefeed/Sandstone/master#volofile
volo install_sandstone project=certmanager
```

I'm not yet sure how to indicate that this Django app now depends on `node-less` which provides `lessc`

### bcrypt

Playdoh requires py-bcrypt but doesn't install it
https://github.com/fwenzel/django-sha2/issues/14

I ran this in Ubuntu
```
sudo apt-get install python-bcrypt
```
