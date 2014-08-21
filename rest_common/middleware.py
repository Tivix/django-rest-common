import logging
import time

from django.conf import settings
from django.db import connection

from rest_framework.authtoken.models import Token


class APILogger(object):
    """
    configuration:

    + add "rest_common.middleware.APILogger" to MIDDLEWARE_CLASSES in settings
    + confgure your api logger in settings
    + setup API_LOGGER_NAME (default: 'api')


    example settings:

    MIDDLEWARE_CLASSES = [
        ...
        'rest_common.middleware.APILogger',
        ...
    ]

    LOGGING = {
        ...
        'handlers': {
            ...
            'api_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/api.log',
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'standard'
            },
            ...
        },
        'loggers': {
            ...
            'my-custom-logger-name': {
                'handlers': ['api_handler'],
                'level': 'INFO',
                'propagate': True,
            },
            ...
        }
    }

    API_LOGGER_NAME = 'my-custom-logger-name'
    """
    LOG = '%(PATH_INFO)s (%(REQUEST_METHOD)s, time: %(time)s, user id: %(user_id)s, db queries: %(db_queries)s): %(body)s'
    LOGGER_NAME = getattr(settings, 'API_LOGGER_NAME', 'api')
    context = None

    def is_api_request(self, request):
        """
        checks if request is an api request
        """
        return request.META['PATH_INFO'].startswith('/api/')

    def get_user_id(self, request):
        """
        get user:
        + from request
        + or using token from request header
        """
        user = getattr(request, 'user', None)
        if user and user.is_authenticated():
            return user.id
        try:
            key = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            token = Token.objects.get(key=key)
        except:
            return '-'
        else:
            return token.user.id

    def process_request(self, request):
        self.context = request.META.copy()
        self.context.update({
            'user_id': '-',
            'time': 'unknown',
            'body': '',
            'db_queries': '-'
        })

        if self.is_api_request(request):
            request.api_start_time = time.time()

            if request.method == 'GET':
                self.context.update({'body': 'DATA: ' + str(request.GET.dict())})
            elif request.method in ('POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'):
                if request.method == 'POST':
                    body = str(request.POST.dict())
                else:
                    # if request is PUT or PATCH we don't have data parsed in
                    # PUT or PATCH so we need to save body of request
                    body = getattr(request, 'body', '')
                self.context.update({'body': 'DATA: ' + body})

    def process_response(self, request, response):
        if self.is_api_request(request) and self.context:

            if getattr(request, 'api_start_time', None):
                t = time.time() - request.api_start_time
                self.context.update({'time': t})

            self.context.update({'user_id': self.get_user_id(request)})
            self.context['db_queries'] = len(connection.queries)

            logger = logging.getLogger(self.LOGGER_NAME)
            logger.info(self.LOG % self.context)
        request.api_start_time = None
        return response
