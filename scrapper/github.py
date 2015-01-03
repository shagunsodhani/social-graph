import os
import sys
import time
from json import loads
from collections import defaultdict

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if not path in sys.path:
    sys.path.insert(1, path)
del path

try:
    import database.mysql as db
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import requests
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import networkx as nx
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))


class Github():
    '''
    '''

    def __init__(self, log = 1):
        json_data=open('config/config.json').read()
        data = loads(json_data)
        self.token = str(data['github_access_token'])
        self.params = {'access_token':self.token, 'per_page':100}
        self.root_url = "https://api.github.com"
        self.options = {}
        self.options['log'] = log 
        self.conn = db.connect()
        self.cursor = self.conn.cursor()

    def fetch_followers(self, user, depth = 2):
        '''
        '''
        self.followers = defaultdict(list)
        self.follower_count = defaultdict(int)
        self.followers_list = []
        self.edge = []
        temp_list = [user]
        self.followers_list.append(temp_list)
        count = 0
        while count <= depth:
            temp_followers_list = []
            for user in self.followers_list[count]:
                if user not in self.followers:
                    print user
                    # https://api.github.com/users/shagunsodhani/followers?page=1&per_page=100
                    url = self.root_url+"/users/"+user+"/followers"
                    self.params['page']=1
                    response = requests.get(url, params = self.params)
                    r = response.json()
                    temp_list = []
                    while r:
                        for i in r:
                            login = str(i['login'])
                            temp_list.append(login)
                            temp_followers_list.append(login)
                            self.edge.append((user, login))
                        self.params['page']+=1
                        response = requests.get(url, params = self.params)
                        r = response.json()
                    self.followers[user] = temp_list
                    self.follower_count[user] = len(temp_list)
                else:
                    for i in self.followers[user]:
                        temp_followers_list.append(i)
            self.followers_list.append(temp_followers_list)
            count+=1
        if self.options['log'] == 1:
            sql = "UPDATE followers SET is_deleted = 2 WHERE is_deleted = 0"
            db.write(sql, self.cursor, self.conn)

            sql_base = "INSERT INTO followers (user1, user2, is_deleted) VALUES "
            sql = sql_base
            sql_end = " ON DUPLICATE KEY UPDATE is_deleted=0"
            count = 1
            for i in self.followers:
                for j in self.followers[i]:
                    sql+="(\'"+i+"\', \'"+j+"\', 0), "
                    count+=1
                    if(count%10000==0):
                        sql = sql[:-2]
                        sql+=sql_end
                        db.write(sql, self.cursor, self.conn)
                        print count, " insertions completed."
                        sql = sql_base
            sql = sql[:-2]
            sql+=sql_end
            db.write(sql, self.cursor, self.conn)
            print count-1, " insertions completed."
            sql = "DELETE FROM followers WHERE is_deleted != 0"
            db.write(sql, self.cursor, self.conn)

    def fetch_following(self, user, depth = 2):
        '''
        '''
        self.following = defaultdict(list)
        self.following_count = defaultdict(int)
        self.following_list = []
        self.edge = []
        temp_list = [user]
        self.following_list.append(temp_list)
        count = 0
        while count <= depth:
            temp_following_list = []
            for user in self.following_list[count]:
                if user not in self.following:
                    print user
                    # https://api.github.com/users/shagunsodhani/following?page=1&per_page=100
                    url = self.root_url+"/users/"+user+"/following"
                    self.params['page']=1
                    response = requests.get(url, params = self.params)
                    r = response.json()
                    temp_list = []
                    while r:
                        for i in r:
                            login = str(i['login'])
                            temp_list.append(login)
                            temp_following_list.append(login)
                            self.edge.append((user, login))
                        self.params['page']+=1
                        response = requests.get(url, params = self.params)
                        r = response.json()
                    self.following[user] = temp_list
                    self.following_count[user] = len(temp_list)
                else:
                    for i in self.following[user]:
                        temp_following_list.append(i)
            self.following_list.append(temp_following_list)
            count+=1
        if self.options['log'] == 1:
            sql = "UPDATE following SET is_deleted = 2 WHERE is_deleted = 0"
            db.write(sql, self.cursor, self.conn)

            sql_base = "INSERT INTO following (user2, user1, is_deleted) VALUES "
            sql = sql_base
            sql_end = " ON DUPLICATE KEY UPDATE is_deleted=0"
            count = 1
            for i in self.following:
                for j in self.following[i]:
                    sql+="(\'"+i+"\', \'"+j+"\', 0), "
                    count+=1
                    if(count%10000==0):
                        sql = sql[:-2]
                        sql+=sql_end
                        db.write(sql, self.cursor, self.conn)
                        print count, " insertions completed."
                        sql = sql_base
            sql = sql[:-2]
            sql+=sql_end
            db.write(sql, self.cursor, self.conn)
            print count-1, " insertions completed."
            sql = "DELETE FROM following WHERE is_deleted != 0"
            db.write(sql, self.cursor, self.conn)

    def fetch_repo_fork(self, user, depth = 2):
        '''
        '''
         # https://api.github.com/users/shagunsodhani/repos
        self.fork = defaultdict(list)
        self.fork_count = defaultdict(int)
        self.fork_list = []
        self.edge = []
        temp_list = [user]
        self.fork_list.append(temp_list)
        count = 0
        params = {}

        while count <= depth:
            temp_fork_list = []
            for user in self.fork_list[count]:
                if user not in self.fork:
                    print user
                    url = self.root_url+"/users/"+user+"/repos"
                    self.params['page']=1
                    response = requests.get(url, params = self.params)
                    r = response.json()
                    temp_list = []
                    while r:
                        for i in r:
                            print i['name']
                            url = self.root_url+"/repos/"+user+"/"+str(i['name'])+"/forks"
                            params['access_token']=self.token
                            params['page']=1
                            response = requests.get(url, params = params)
                            b = response.json()
                            if b:
                                # print response.url
                                # print b
                                for j in b:
                                    login = str(i['owner']['login'])
                                    # print login
                                    temp_list.append(login)
                                    temp_fork_list.append(login)
                                    self.edge.append((user, login))
                                    params['page']+=1
                                    response = requests.get(url, params = params)
                                    b = response.json()
                        self.params['page']+=1
                        response = requests.get(url, params = self.params)
                        r = response.json()
                    self.fork[user] = temp_list
                    self.fork_count[user] = len(temp_list)
                else:
                    for i in self.fork[user]:
                        temp_fork_list.append(i)
            self.fork_list.append(temp_fork_list)
            count+=1
        if self.options['log'] == 1:
            sql = "UPDATE fork SET is_deleted = 2 WHERE is_deleted = 0"
            db.write(sql, self.cursor, self.conn)

            sql_base = "INSERT INTO fork (user1, user2, is_deleted) VALUES "
            sql = sql_base
            sql_end = " ON DUPLICATE KEY UPDATE is_deleted=0"
            count = 1
            for i in self.fork:
                for j in self.fork[i]:
                    sql+="(\'"+i+"\', \'"+j+"\', 0), "
                    count+=1
                    if(count%10000==0):
                        sql = sql[:-2]
                        sql+=sql_end
                        db.write(sql, self.cursor, self.conn)
                        print count, " insertions completed."
                        sql = sql_base
            if(sql != sql_base):
                sql = sql[:-2]
                sql+=sql_end
                db.write(sql, self.cursor, self.conn)
                print count-1, " insertions completed."
            sql = "DELETE FROM fork WHERE is_deleted != 0"
            db.write(sql, self.cursor, self.conn)

if __name__ == "__main__":
    g = Github()
    g.fetch_repo_fork(user = 'shagunsodhani', depth = 0)
    # g.fetch_followers(user = 'shagunsodhani', depth = 0)
