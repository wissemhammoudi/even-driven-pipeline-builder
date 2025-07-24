import requests
import json
from typing import Dict, Optional, List
from urllib.parse import urljoin

class SupersetClient:
    
    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None        
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._csrf_token = None
    
    def _get_csrf_token(self):
        if not self.access_token:
            if self.username and self.password:
                if not self.authenticate():
                    return None
            else:
                return None
            
        csrf_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }    
        try:
            csrf_response = self.session.get(
                f"{self.base_url}/api/v1/security/csrf_token/",
                headers=csrf_headers
            )
            if csrf_response.status_code == 200:
                csrf_token = csrf_response.json().get('result')
                self._csrf_token = csrf_token
                return csrf_token
            elif csrf_response.status_code == 401:
                if self.refresh_access_token():
                    csrf_headers['Authorization'] = f'Bearer {self.access_token}'
                    csrf_response = self.session.get(
                        f"{self.base_url}/api/v1/security/csrf_token/",
                        headers=csrf_headers
                    )
                    if csrf_response.status_code == 200:
                        csrf_token = csrf_response.json().get('result')
                        self._csrf_token = csrf_token
                        return csrf_token
                return None
            else:
                return None
        except Exception as e:
            return None
    
    def refresh_access_token(self) -> bool:
        if not self.refresh_token:
            return False
        
        try:
            response = self._make_request('POST', '/api/v1/security/refresh',
                                        json={'refresh_token': self.refresh_token})
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens.get('access_token')
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.get('headers', {})
        headers.update(self.headers)
        if endpoint != '/api/v1/security/login':
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            elif method.upper() in ['POST', 'PUT', 'DELETE'] and endpoint != '/api/v1/security/refresh':
                if self.username and self.password:
                    if self.authenticate():
                        headers['Authorization'] = f'Bearer {self.access_token}'
                    else:
                        mock_response = requests.Response()
                        mock_response.status_code = 401
                        mock_response._content = b'{"error": "Authentication required"}'
                        return mock_response
        
        if method.upper() in ['POST', 'PUT', 'DELETE'] and endpoint not in ['/api/v1/security/login', '/api/v1/security/refresh']:
            csrf_token = self._get_csrf_token()
            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
            else:
                mock_response = requests.Response()
                mock_response.status_code = 403
                mock_response._content = b'{"error": "CSRF token required"}'
                return mock_response
        
        kwargs['headers'] = headers

        response = self.session.request(method, url, **kwargs)
        
        if response.status_code == 401 and self.refresh_token and endpoint != '/api/v1/security/refresh':
            if self.refresh_access_token():
                headers['Authorization'] = f'Bearer {self.access_token}'
                if method.upper() in ['POST', 'PUT', 'DELETE']:
                    csrf_token = self._get_csrf_token()
                    if csrf_token:
                        headers['X-CSRFToken'] = csrf_token
                kwargs['headers'] = headers
                response = self.session.request(method, url, **kwargs)
        
        return response

    def get_user_id(self, username: str) -> Optional[int]:
        try:
            params = {
                'q': json.dumps({
                    'filters': [{
                        'col': 'username',
                        'opr': 'eq',
                        'value': username
                    }]
                })
            }
            
            response = self._make_request('GET', '/api/v1/security/users/', params=params)
            
            if response.status_code == 200:
                users_data = response.json()
                if users_data.get('result') and len(users_data['result']) > 0:
                    user = users_data['result'][0]
                    user_id = user.get('id')
                    return user_id
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            return None

    def create_user(self, username: str, email: str, first_name: str, 
                   last_name: str, password: str, roles: List[int], 
                   active: bool = True) -> Optional[int]:
        user_data = {
            "active": active,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "roles": roles,
            "username": username
        }
        
        response = self._make_request('POST', '/api/v1/security/users/', json=user_data)
        
        if response.status_code == 201:
            result = response.json()
            # Try both possible keys for id
            return result.get('id') or result.get('result', {}).get('id')
        else:
            return None
    
    def authenticate(self, username: str = None, password: str = None) -> bool:
        user = username or self.username
        pwd = password or self.password
        
        login_data = {
            'username': user,
            'password': pwd,
            'provider': 'db',
            'refresh': True
        }
        
        try:
            response = self._make_request('POST', '/api/v1/security/login', 
                                        json=login_data, headers=self.headers)
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens.get('access_token')
                self.refresh_token = tokens.get('refresh_token')
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def create_database_if_not_exists(self, database_name: str, sqlalchemy_uri: str, **kwargs) -> Optional[int]:
        response = self._make_request('GET', '/api/v1/database/')
        if response.status_code == 200:
            databases = response.json()
            if databases and databases.get('result'):
                for db in databases['result']:
                    if db.get('database_name') == database_name:
                        return db.get('id')
        database_data = {
            "database_name": database_name,
            "sqlalchemy_uri": sqlalchemy_uri,
            "cache_timeout": kwargs.get('cache_timeout', 0),
            "expose_in_sqllab": kwargs.get('expose_in_sqllab', True),
            "allow_run_async": kwargs.get('allow_run_async', False),
            "allow_csv_upload": kwargs.get('allow_csv_upload', False),
            "allow_ctas": kwargs.get('allow_ctas', False),
            "allow_cvas": kwargs.get('allow_cvas', False),
            "allow_dml": kwargs.get('allow_dml', False),
            "allow_multi_schema_metadata_fetch": kwargs.get('allow_multi_schema_metadata_fetch', False),
            "engine_params": kwargs.get('engine_params', {}),
            "extra": kwargs.get('extra', '{}'),
            "server_cert": kwargs.get('server_cert', ''),
            "impersonate_user": kwargs.get('impersonate_user', False),
            "encrypted_extra": kwargs.get('encrypted_extra', '{}'),
            "ssl_cert": kwargs.get('ssl_cert', ''),
            "ssl_key": kwargs.get('ssl_key', ''),
            "ssl_ca": kwargs.get('ssl_ca', '')
        }
        response = self._make_request('POST', '/api/v1/database/', json=database_data)
        if response.status_code == 201:
            result = response.json()
            return result.get('id') or result.get('result', {}).get('id')
        else:
            return None

    def create_dashboard(self, dashboard_title: str, **kwargs) -> Optional[int]:

        dashboard_data = {
            "dashboard_title": dashboard_title,
            "owners": kwargs.get('owners', []),
            "roles": kwargs.get('roles', []),
            "published": kwargs.get('published', True)
        }
        response = self._make_request('POST', '/api/v1/dashboard/', json=dashboard_data)
        if response.status_code == 201:
            result = response.json()
            return result.get('id') or result.get('result', {}).get('id')
        else:
            return None

    def get_dashboard_info(self, dashboard_id):
        resp = self._make_request('GET', f'/api/v1/dashboard/{dashboard_id}')
        if resp.status_code == 200:
            return resp.json().get('result', {})
        else:
            return None

    def update_dashboard_owners(self, dashboard_id: int, owner_ids: list[int], add: bool = True):
        dashboard_data = self.get_dashboard_info(dashboard_id)
        if not dashboard_data:
            return {
                "success": False,
                "error": f"Dashboard {dashboard_id} not found",
                "dashboard_id": dashboard_id
            }
        
        current_owners = dashboard_data.get('owners', [])
        current_owner_ids = [owner['id'] for owner in current_owners if isinstance(owner, dict) and 'id' in owner]
        current_owner_ids_set = set(current_owner_ids)
        new_owner_ids_set = set(owner_ids)
        
        if add:
            updated_owner_ids = list(current_owner_ids_set.union(new_owner_ids_set))
        else:
            updated_owner_ids = list(current_owner_ids_set.difference(new_owner_ids_set))
        
        filtered_data = {'owners': updated_owner_ids}
        response = self._make_request('PUT', f'/api/v1/dashboard/{dashboard_id}', json=filtered_data)
        if response.status_code in (200, 201):
            return {"success": True, "dashboard_id": dashboard_id, "owners": updated_owner_ids}
        else:
            return {
                "success": False,
                "error": f"Failed to update owners for dashboard {dashboard_id}: {response.text}",
                "dashboard_id": dashboard_id
            }
