from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from django.conf import settings


@dataclass(frozen=True)
class PalworldApiConfig:
    base_url: str
    username: str
    password: str
    timeout: float

    @classmethod
    def from_settings(cls):
        config = settings.PALWORLD_API
        return cls(
            base_url=config['BASE_URL'].rstrip('/'),
            username=config['USERNAME'],
            password=config['PASSWORD'],
            timeout=config['TIMEOUT'],
        )


class PalworldApiClient:
    def __init__(self, config=None):
        self.config = config or PalworldApiConfig.from_settings()

    def endpoint_url(self, path):
        return urljoin(f"{self.config.base_url}/", path.lstrip('/'))

    def get(self, path):
        request = Request(self.endpoint_url(path), method='GET')
        request.add_header('Accept', 'application/json')
        request.add_header(
            'Authorization',
            self._basic_auth_header(self.config.username, self.config.password),
        )

        try:
            with urlopen(request, timeout=self.config.timeout) as response:
                body = response.read().decode('utf-8')
                return {
                    'ok': True,
                    'status_code': response.status,
                    'data': json.loads(body) if body else None,
                }
        except HTTPError as error:
            return self._error_response(error.code, error.read().decode('utf-8', errors='replace'))
        except (TimeoutError, URLError) as error:
            return self._error_response(None, str(error))

    @staticmethod
    def _basic_auth_header(username, password):
        import base64

        token = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('ascii')
        return f'Basic {token}'

    @staticmethod
    def _error_response(status_code, message):
        return {
            'ok': False,
            'status_code': status_code,
            'error': message,
        }
