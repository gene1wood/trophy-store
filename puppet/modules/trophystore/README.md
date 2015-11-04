# trophystore

#### Table of Contents

1. [Description](#description)
2. [Setup - The basics of getting started with trophystore](#setup)
    * [What trophystore affects](#what-trophystore-affects)
    * [Setup requirements](#setup-requirements)
    * [Beginning with trophystore](#beginning-with-trophystore)
3. [Usage - Configuration options and additional functionality](#usage)
4. [Reference - An under-the-hood peek at what the module is doing and how](#reference)
5. [Limitations - OS compatibility, etc.](#limitations)
6. [Development - Guide for contributing to the module](#development)

## Description

The trophystore puppet module deploys the Trophy Store application and
configures it on a [RedHat Derivative](https://en.wikipedia.org/wiki/Red_Hat_Enterprise_Linux_derivatives#List_of_Red_Hat_Enterprise_Linux_derivatives).

## Setup

### Setup Requirements **OPTIONAL**

The trophystore module depends on the following other modules having been
installed.

    puppet module install puppetlabs-stdlib
    puppet module install puppetlabs-mysql
    puppet module install puppetlabs-apache
    puppet module install treydock-scl

### Beginning with trophystore 

Configure the parameters by creating a hiera config file.

    vi /var/lib/hiera/common.yaml

Here is an example config

    trophystore::db_password: Pnw1ZHgcYdNio7YLmVwYHT/RuovyYCFSjNsYJex76Y8=
    trophystore::db_root_password: BAF54Z/+MOxutmCs669jWt/XyohfQKgaO7QwZaAUi2M=
    trophystore::hmac_secret: eMHNpUfCKCSoKMr0oBK+yKzHsFg6KgNe0IJXVPdSHm8=
    trophystore::django_secret: QrHxNUnBxQ/WZ8zDRMb+61/LuOUrSIkjyWDdfcWHnWQ=
    trophystore::site_name: trophystore.example.com
    trophystore::app_config:
      destinations: 
        zlb1.example.com: 
          type: stingray
          hostname: zlb1.example.com
          username: trophystore
          password: "my_ZLB_passw0rd"
          description: zlb1.example.com
      certificate_authorities:
          digicert:
              type: digicert
              account_id: 012345
              api_key: abcdefghijklmnopqrstuvwxyz012345
      users:
        - jdoe@example.com
        - jroe@mozilla.com
    trophystore::ssl_key_content: '-----BEGIN RSA PRIVATE KEY-----
    
      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
    
      -----END RSA PRIVATE KEY-----'
    trophystore::ssl_cert_content: '-----BEGIN CERTIFICATE-----
    
      MIIEsjCCApoCAQEwDQYJKoZIhvcNAQEFBQAwIzEhMB8GA1UEAwwYaW50ZXJtZWRp
    
      YXRlLmV4YW1wbGUuY29tMB4XDTEzMDIyMjIyNDcwOVoXDTE4MDIyMTIyNDcwOVow
    
      GzEZMBcGA1UEAwwQdGVzdC5leGFtcGxlLmNvbTCCAiIwDQYJKoZIhvcNAQEBBQAD
    
      ggIPADCCAgoCggIBANtN16kUaeySGXtzhF5OZ93Xp1+pA99AkWYdEDLoeEPfpc8A
    
      npU0CLg74wLqC0bTTgxj7y689fw315jegFjWsG5GaBk/aFYSCp2NclnjThsGRls/
    
      5mE5w4lJlK7FurFKNwPYNDFRgsrEhPcFBe/u0UZBHZoefuCgyws1y1Lrds9mvVWn
    
      EokXPirLHokfy8CTNeASkoEXKnmKtz5DC+RHmacp+nYT8/dGfX2ETiq/Weo9y/yC
    
      HhFpj1+SvmN/f9ay3+l9hZmiuBHlzJgt5n7xhXMGgz2j8fKZSdz8WDMYITIKQoSN
    
      KLhrsswyXG12pjdY/UWqbP9YJ+JD22gPOv5/T4tezSr54G6GnBf0fX86SxdVJtiC
    
      Q5Fq9qk5L+n37YYc4ONixfhcw5C8p/ClAQIt80mAiiuYcNLcN8RJLZnKvvbN4puK
    
      EAXF2hA7cBFbPAJy9/ms/Revbw3nvU6P80aQrMfyiHlOFKov4QLNwx34XOYa3deL
    
      LOy6zyxG+JyHXDS59En1e6up7B+lzmcc4IFzX7VbXkpAisllXutzM0uRz/M9M395
    
      kenGdQDaQ6JLnt9l+tS2iPVAfmG3ZuqAAhfb1B25w7MeQdwqVVWBMexoaX5z1OT+
    
      gitC1h+oFj/ak4784OYMvQPMi79oztuxZYL88xDhcwWOo73DL+y/zkvI5DbrAgMB
    
      AAEwDQYJKoZIhvcNAQEFBQADggIBABmZbSGWE5CeLjhyKVuQI6pRZxuIGPu14tvF
    
      B+zq6elkkPYVs/Z6XLdZZGOORX+qHLTAbdnlAxTbNfE1edMIUvGgVDgm/rMhArF1
    
      7o9LzqlgMEeJJf2Lzl4p06KNLOILt6DrLEeS2tzZAMeWDQJgPe/mXt9DOtuoP+C0
    
      ynDgn/zlXdAkqI1cUwDG3vTlsbWjjHTDp/3k90Qkgxg+cCwDdKQf59pA3cvgMZOv
    
      K7U/y1W6iQmekn1j+1XruicHt0yhTSMV/ufmTGBlSnufIc3UbcJqLVLOTK2j70X8
    
      RIS5NsWZ4Jzt+BJO90QcDFFXwpMWL81080XBtlL5D/3WFkyBnduScHZa6RQtpMIw
    
      GslP0Z1ECObj4CxAOAxYEQlKtIFbqV6f4NIxNT/Leihx9S5IVVUAhkeAJqoYTr5R
    
      XzNyhCf0pPCEwlwGzSEMy1IK0eQ2BaNBZSWVMChJW5lpJVU8AMcZ9ye33OywxkSz
    
      7681ZfRPFcCj0e3EcCCQJuQ69fSpiq4pqveTehwSrr7oxn/BnY0MqVNrkrNKEMwy
    
      Qrl3Z0B8gQrDNnA1CPgWBHl4Bz2ppMYaGGbOhNuGr6mDZPJsmV0nod7UFeAlOa+2
    
      OQNvs1LqDdlS398Nh8bhl00gkTiUIsf3I9TTmV7QGa0dS99W1pKtm3Tka831AreH
    
      9PZH15Pd
    
      -----END CERTIFICATE-----'

