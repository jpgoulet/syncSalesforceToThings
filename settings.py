import keyring
import json
from datetime import datetime

class Settings(object):
    """Settings for syncTasks"""
    def __init__(self):
        super(Settings, self).__init__()
        
        with open('settings.json', 'r') as file:
            data = json.loads(file.read())
            self._user = data['user']
            self._email = data['email']
            self._url = data['base_url']
            self._area = data['area']
            self._lastTimestamp = datetime.strptime(data['lastTimestamp'],'%Y-%m-%dT%H:%M:%S.%f')
            

    def writeToFile(self):
        with open('settings.json', 'w') as file:
            data = {}
            data['user'] = self._user
            data['email'] = self._email
            data['base_url'] = self._url
            data['area'] = self._area
            data['lastTimestamp'] = self._lastTimestamp.isoformat()
            
            json.dump(data, file)
    
    
    @property
    def user(self):
        return self._user
        
        
    @property
    def email(self):
        return self._email
        
        
    @property
    def url(self):
        return self._url
        
        
    @property
    def area(self):
        return self._area
        
    
    @property
    def password(self):
        return keyring.get_password("salesforce", self.email)
        
        
    @property
    def token(self):
        return keyring.get_password("salesforce_token", self.email)
        
        
    @property
    def lastTimestamp(self):
        return self._lastTimestamp
    
    @lastTimestamp.setter
    def lastTimestamp(self, value):
        self._lastTimestamp = value
    
    

settings = Settings()