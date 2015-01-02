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
        self.params = {'access_token':self.token, 'per_page':100}
        self.root_url = "https://api.github.com"
        self.options = {}
        self.options['offline'] = offline
        self.options['log'] = log 
        self.conn = db.connect()
        self.cursor = self.conn.cursor()

    # @profile    
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
        if self.options['offline'] == 0:
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
        else:
            sql="SELECT user1, user2 FROM followers WHERE is_deleted=0"
            result = db.read(sql, self.cursor)
            for i in result:
                # user1 = i[0]
                # user2 = i[1]
                # self.followers[user1].append(user2)
                self.followers[i[0]].append(i[1])
            while count<=depth:
                temp_followers_list = []
                for user in self.followers_list[count]:
                    for i in self.followers[user]:
                        temp_followers_list.append(i)
                        self.edge.append((user, i))
                self.followers_list.append(temp_followers_list)
                count+=1
            for i in self.followers:
                self.follower_count[i] = len(self.followers[i])
    # @profile
    def gen_graph(self, user, depth = 2):
        '''
        '''
        self.fetch_followers(user = user, depth = depth)
        self.g = nx.DiGraph()
        self.g.add_edges_from(self.edge)
        # for i in self.g.node:
        #     print i
        #     print self.follower_count[i]
        #     self.g.node[i]['weight'] = self.follower_count[i]
        self.max_followers =  max(self.follower_count.values())    
        print "Number of Nodes ", self.g.number_of_nodes()
        print "Number of Edges ", self.g.number_of_edges()

    def plot_followers(self):
        '''
        '''
        node_size = []
        node_color = []
        for i in self.g.nodes():
            if self.follower_count[i] == 0:
                node_color.append('r')
                node_size.append(150)
            else:
                node_size.append(300*float(self.follower_count[i])/self.max_followers)
                print (300*float(self.follower_count[i])/self.max_followers)
                print i
                print self.follower_count[i]
                print "\n"
                node_color.append('b')

        nx.draw_graphviz(self.g, with_labels = False, linewidth = 0.1, node_size = node_size, node_color = node_color)
        plt.show()

    def print_distance_measures(self):
        '''
        '''
        print type(nx.center(self.g))
    

if __name__ == "__main__":
    g = Github(offline = 0)
    # g.fetch_followers(user = 'shagunsodhani', depth = 1)
    # g.fetch_followers(user = 'shagunsodhani', depth = 1)
    g.gen_graph(user = 'shagunsodhani', depth = 5)
    g.plot_followers()
    # g.print_distance_measures()
    # self.pyplot
    # for i in g.followers_list:
    #     print i
