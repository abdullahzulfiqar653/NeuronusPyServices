# home/test_utils.py

from rest_framework.test import APIClient

class CustomTestClient(APIClient):
    def __init__(self, host, *args, **kwargs):  # Make 'host' required
        if not host:
            raise ValueError("The 'host' parameter must be provided.")
        self.host = host
        super().__init__(*args, **kwargs)

    def _set_host(self, extra):
        if "HTTP_HOST" not in extra:
            extra["HTTP_HOST"] = self.host
        return extra

    def get(self, path, **extra):
        extra = self._set_host(extra)
        return super().get(path, **extra)

    def post(self, path, data=None, **extra):
        extra = self._set_host(extra)
        return super().post(path, data, **extra)

    def put(self, path, data=None, **extra):
        extra = self._set_host(extra)
        return super().put(path, data, **extra)
    
    def patch(self, path, data=None, **extra):
        extra = self._set_host(extra)
        return super().patch(path, data, **extra)

    def delete(self, path, **extra):
        extra = self._set_host(extra)
        return super().delete(path, **extra)
