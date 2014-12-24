import time
from json import loads
from collections import defaultdict
import matplotlib.pyplot as plt
import requests
import networkx as nx
import db

class Github():
    '''
    '''

    def __init__(self, offline = 1, log = 1):
        json_data=open('config/config.json').read()
        data = loads(json_data)
        self.token = str(data['github_access_token'])
        self.params = {'access_token':self.token}
        self.root_url = "https://api.github.com"
        self.options = {}
        self.options['offline'] = offline
        self.options['log'] = log 
        self.conn = db.connect()
        self.cursor = self.conn.cursor()

    @profile    
    def fetch_followers(self, user, depth = 2):
        '''
        '''
        self.followers = defaultdict(list)
        self.followers_list = []
        self.edge = []
        temp_list = [user]
        self.followers_list.append(temp_list)
        count = 0
        if self.options['offline'] == 0:
            while count <= depth:
                temp_followers_list = []
                for user in self.followers_list[count]:
                    if user not in self.followers:
                        print user
                        url = self.root_url+"/users/"+user+"/followers"
                        response = requests.get(url, params = self.params)
                        r = response.json()
                        temp_list = []
                        for i in r:
                            login = str(i['login'])
                            temp_list.append(login)
                            temp_followers_list.append(login)
                            self.edge.append((user, login))
                        self.followers[user] = temp_list
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
                print count, " insertions completed."
                sql = "DELETE FROM followers WHERE is_deleted != 0"
                db.write(sql, self.cursor, self.conn)
        else:
            sql="SELECT user1, user2 FROM followers WHERE is_deleted=0"
            result = db.read(sql, self.cursor)
            for i in result:
                user1 = i[0]
                user2 = i[1]
                self.followers[user1].append(user2)
            while count<=depth:
                temp_followers_list = []
                for user in self.followers_list[count]:
                    for i in self.followers[user]:
                        temp_followers_list.append(i)
                        self.edge.append((user, i))
                self.followers_list.append(temp_followers_list)
                count+=1

    # @profile
    def plot_followers(self, user, depth = 2):
        '''
        '''
        self.fetch_followers(user = user, depth = depth)
        g = nx.DiGraph()
        g.add_edges_from(self.edge)
        print "Number of Nodes ", g.number_of_nodes()
        print "Number of Edges ", g.number_of_edges()
        # g=nx.Graph()
        nx.draw_graphviz(g)
        plt.show()


if __name__ == "__main__":
    g = Github(offline = 1)
    g.fetch_followers(user = 'shagunsodhani', depth = 2)
    # g.fetch_followers(user = 'shagunsodhani', depth = 1)
    # g.plot_followers(user = 'shagunsodhani', depth = 1)
    # for i in g.followers_list:
    #     print i
