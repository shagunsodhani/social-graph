import time
from json import loads
import requests

class Github():
    '''
    '''

    def __init__(self):
        json_data=open('config/config.json').read()
        data = loads(json_data)
        self.token = str(data['github_access_token'])
        self.params = {'access_token':self.token}
        self.root_url = "https://api.github.com"

    def fetch_followers(self, user, depth = 2):
        '''
        '''
        self.followers = {}
        self.followers_list = []
        temp_list = [user]
        self.followers_list.append(temp_list)
        count = 0
        while count <= depth:
            temp_followers_list = []
            for user in self.followers_list[count]:
                if user not in self.followers:
                    url = self.root_url+"/users/"+user+"/followers"
                    response = requests.get(url, params = self.params)
                    r = response.json()
                    temp_list = []
                    for i in r:
                        login = str(i['login'])
                        temp_list.append(login)
                        temp_followers_list.append(i)
                    self.followers[user] = temp_list
                else:
                    for i in self.followers[user]:
                        temp_followers_list.append(i)
            self.followers_list.append(temp_followers_list)


g = Github()
g.fetch_followers(user = 'shagunsodhani')
for i in g.followers_list:
    print i
