#https://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php
import sys
from functools import total_ordering
import numpy as np


@total_ordering
class Vertex:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxsize
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        #print(self)
        return self.adjacent.keys()

    def delete_vertex(self, n):
        self.adjacent.pop(n)  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

    def set_distance(self, dist):
        self.distance = dist

    def get_distance(self):
        return self.distance
    
    def is_in(self, n):
        if n in self.adjacent.keys():
            return True
        else:
            return False

    def set_previous(self, prev):
        self.previous = prev

    def set_visited(self):
        self.visited = True

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.distance == other.distance
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.distance < other.distance
        return NotImplemented

    def __hash__(self):
        return id(self)

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def out_of_neighbor(self,ip):
        if len(self.vert_dict[ip].get_connections()) == 0:
            return True
        else:
            return False

    def lim_of_neighbours(self,ip):
        return len(self.vert_dict[ip].get_connections())
        

    def remove_peer_lig(self,n):
        for value in self.vert_dict.values():
            for w in value.get_connections():
                if w.is_in(self.get_vertex(n)):
                    w.delete_vertex(self.get_vertex(n))
        self.vert_dict.pop(n)
        
                    
    def delete_graph(self):
        self.vert_dict.clear()
        self.num_vertices = 0
        

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    def set_previous(self, current):
        self.previous = current

    def get_previous(self, current):
        return self.previous
    
    def print_graph(self):
        for v in self:
            for w in v.get_connections():
                vid = v.get_id()
                wid = w.get_id()
                print ('( %s , %s, %f)'  % ( vid, wid, v.get_weight(w))) 
                

    def get_graph_em_forma_de_array(self):
        array_topologia = []
        x = 0
        for v in self:
            for w in v.get_connections():
                vid = v.get_id()
                wid = w.get_id()
                array_topologia.append(( vid, wid, v.get_weight(w)))         
        return array_topologia
    
    def remove_peer(self, vertex):
        topologia = self.get_graph_em_forma_de_array()
        new_topologia = []
        x = 0
        while x < len(topologia):
            if(topologia[x][0] == vertex or topologia[x][1] == vertex):
                pass
            else:
                new_topologia.append((topologia[x][0],topologia[x][1],topologia[x][2]))
            x = x + 1
        print("new")
        print(new_topologia)
        return new_topologia


def shortest(v, path):
    ''' make shortest path from v.previous'''
    if v.previous:
        path.append(v.previous.get_id())
        shortest(v.previous, path)
    return

import heapq

def dijkstra(aGraph, start):
    #print ('''Dijkstra's shortest path''')
    # Set the distance for the start node to zero 
    start.set_distance(0)

    # Put tuple pair into the priority queue
    unvisited_queue = [(v.get_distance(),v) for v in aGraph]
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue):
        # Pops a vertex with the smallest distance 
        uv = heapq.heappop(unvisited_queue)
        current = uv[1]
        current.set_visited()

        #for next in v.adjacent:
        for next in current.adjacent:
            # if visited, skip
            if next.visited:
                continue
            new_dist = current.get_distance() + current.get_weight(next)
            
            if new_dist < next.get_distance():
                next.set_distance(new_dist)
                next.set_previous(current)
                #print ('updated : current = %s next = %s new_dist = %s' \
                #        %(current.get_id(), next.get_id(), next.get_distance()))
            #else:
                #print ('not updated : current = %s next = %s new_dist = %s' \
                #        %(current.get_id(), next.get_id(), next.get_distance()))

        # Rebuild heap
        # 1. Pop every item
        while len(unvisited_queue):
            heapq.heappop(unvisited_queue)
        # 2. Put all vertices not visited into the queue
        unvisited_queue = [(v.get_distance(),v) for v in aGraph if not v.visited]
        heapq.heapify(unvisited_queue)

def routing_table_calculation(array_topologia, node):
       
    nodesArray = [0]
    l = 0
    k = 0
    t = 0
    igual = 0
    
    for x in array_topologia:
        while k < len(nodesArray):
            if( array_topologia[t][0] == nodesArray[k] or array_topologia[t][1] == nodesArray[k]):
                igual = 1
            k += 1
            #print(k)
        if(igual == 0):
            nodesArray.append(array_topologia[t][0])
            #print(nodesArray)
        igual = 0
        k  = 0
        t += 1
    
    l = 0
    k = 0
    t = 0
    igual = 0
    
    for x in array_topologia:
        while k < len(nodesArray):
            if(array_topologia[t][1] == nodesArray[k]):
                igual = 1
            k += 1
            #print(k)
        if(igual == 0):
            nodesArray.append(array_topologia[t][1])
            #print(nodesArray)
        igual = 0
        k  = 0
        t += 1
        
    nodesArray.remove(0)
    #print(nodesArray)

    g = Graph()

    l = 0
    for x in nodesArray:
        g.add_vertex(nodesArray[l])
        l +=1
    l = 0
    for x in array_topologia:
        g.add_edge(array_topologia[l][0],array_topologia[l][1],array_topologia[l][2])
        l +=1
    #nodesArray = ['10.0.0.1','10.0.0.2','10.0.0.3','10.0.0.4','10.0.0.5','10.0.0.6']
    routing_table =[ [ 0 for i in range(2) ] for j in range(len(nodesArray)) ]
    #print ('Graph data:')
    for v in g:
        for w in v.get_connections():
            vid = v.get_id()
            wid = w.get_id()
           # print ('( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w)))
    y = 0
    z = 0
    k = 0
    for x in nodesArray:            
        dijkstra(g, g.get_vertex(node)) 
        target = g.get_vertex(nodesArray[y])
        path = [target.get_id()]
        shortest(target, path)      
        #print ('The shortest path to '+arraysOfnodes[y]+' : %s' %(path[::-1]))
        #print ('Next hop : %s' %(path[len(path)-2]))
        routing_table[z][k] = nodesArray[y]
        routing_table[z][k + 1] = path[(len(path)-2)]
        k = 0
        z = z + 1
        y = y +1

    return routing_table


                        


