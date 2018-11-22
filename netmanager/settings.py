# -*- coding: utf-8 -*-

# flask core settings
DEBUG = True
TESTING = False
SECRET_KEY = 'qh\x98\xc4o\xc4]\x8f\x8d\x93\xa4\xec\xc5\xfd]\xf8\xb1c\x84\x86\xa7A\xcb\xc0'
PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30

# flask wtf settings
WTF_CSRF_ENABLED = True

# project settings
PROJECT_PASSWORD_HASH_METHOD = 'pbkdf2:sha1'
PROJECT_SITE_NAME = u'Flask Example'
PROJECT_SITE_URL = u'http://127.0.0.1:6000'
PROJECT_SIGNUP_TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # in seconds
PROJECT_RECOVER_PASSWORD_TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # in seconds

API_ENDPOINT = 'https://dev-netsoa.vestas.net/netmanager/1.0.0/'
API_test_ENDPOINT = 'https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/'

# ADE application name
ADE_ENVIRONMENT_NAME = "develop"
ADE_TIMEZONE = 'Europe/Copenhagen'
