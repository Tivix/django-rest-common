import json
from datetime import datetime, date, time

from django.conf import settings
from django.test.client import Client, MULTIPART_CONTENT


class APIClient(Client):
    """
    Client with two new request methods needed for API tests
    """

    def patch(self, path, data='', content_type=MULTIPART_CONTENT, follow=False,
        **extra):
        return self.generic('PATCH', path, data, content_type, **extra)

    def options(self, path, data='', content_type=MULTIPART_CONTENT,
        follow=False, **extra):
        return self.generic('OPTIONS', path, data, content_type, **extra)


class CustomJSONEncoder(json.JSONEncoder):
    """
    Convert datetime/date objects into isoformat
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        else:
            return super(CustomJSONEncoder, self).default(obj)


class APITestMixin(object):
    """
    base for API tests:

    + easy request calls, f.e.:
        self.post(url, data)
        self.get(url)
        self.patch(url, data)

    + easy check response status, f.e.:
        self.post(url, data, status_code=201)
        self.get(url, status_code=404)
    """

    JSON_ENCODER = CustomJSONEncoder

    def send_request(self, request_method, *args, **kwargs):
        request_func = getattr(self.client, request_method)
        status_code = None

        if not 'content_type' in kwargs and request_method != 'get':
            kwargs['content_type'] = 'application/json'

        # dump data to json
        if 'data' in kwargs and request_method != 'get' and \
            kwargs['content_type'] == 'application/json':
            data = kwargs.get('data', '')
            kwargs['data'] = json.dumps(data, cls=self.JSON_ENCODER)

        # if status_code is passed, then check status code in response against
        # this value
        if 'status_code' in kwargs:
            status_code = kwargs.pop('status_code')

        if hasattr(self, 'token'):
            kwargs['HTTP_AUTHORIZATION'] = 'Token %s' % self.token

        # send request
        self.response = request_func(*args, **kwargs)


        is_json = bool(filter(lambda x: 'json' in x, self.response._headers['content-type']))
        if is_json and self.response.content:
            self.response.json = json.loads(self.response.content)
        else:
            self.response.json = {}
        if status_code:
            self.assertEqual(self.response.status_code, status_code)

        return self.response

    def post(self, *args, **kwargs):
        return self.send_request('post', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.send_request('get', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.send_request('patch', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.send_request('put', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.send_request('delete', *args, **kwargs)

    def options(self, *args, **kwargs):
        return self.send_request('options', *args, **kwargs)

    def init(self):
        settings.DEBUG = True
        self.client = APIClient()
