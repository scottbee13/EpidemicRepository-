#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 00:35:49 2019

@author: Scott
"""

import networkx as nx
import numpy as np
import itertools 
import sys 


def CharacterDifferenceSIR(a,b):
    #Detect the Number of difference between 2 strings and tell what type of connection is required. 
    CharacterDiff = 0 
    DifferenceLocation = -1
    ConnectionType = "NoConnection"
    if len(a) != len(b):
        print("Error: The length of these strings are no the same.")
        sys.exit()
    else:
        for i in range(len(b)): 
            if int(list(a)[i]) != int(list(b)[i]):
                total = int(list(a)[i]) + int(list(b)[i]) 
                if total == 1 or total == 3:
                    CharacterDiff += 1
                    
                    if CharacterDiff >= 2:
                        CharacterDiff, DifferenceLocation, ConnectionType = -1,-1, "NoConnection"
                        break
                    
                    else:
                        DifferenceLocation = i
                        if   int(list(a)[i]) == 1:
                            ConnectionType = "Recovery"
                        elif int(list(a)[i]) == 0:
                                ConnectionType = "Infection" 
                        else:
                            CharacterDiff, DifferenceLocation, ConnectionType = -1,-1, "NoConnection"
                            break
                else:
                    CharacterDiff += 1

                
            
    return([CharacterDiff, DifferenceLocation, ConnectionType])


"""Graph we wish to gather the Jointly Markov Chain for"""

"""Square"""
ConnectionMatrix =  nx.Graph()
ConnectionMatrix.add_edges_from([(1,2),(2,3),(3,0),(0,1)])

"""Triangle"""
ConnectionMatrix =  nx.Graph()
ConnectionMatrix.add_edges_from([(0,1),(1,2),(2,0)])

"""Link"""
ConnectionMatrix =  nx.Graph()
ConnectionMatrix.add_edges_from([(0,1),(1,0)])

Beta  = 0.15
Gamma = 0.6
StateNumber = 3


#Test - Max Number of Nodes and States
NodeNumber = len(ConnectionMatrix.nodes())


if NodeNumber > 25 or StateNumber > 3:
    print("This model only works for small number of nodes and States.  Remember that the number of states in the extended Markov Chain is StateNumber ** (Number of Nodes)." )
    print("In this model you would have " + str(StateNumber ** NodeNumber) + " number of possible states.")

""" Construction of the Joint Markov Chain"""

JointMarkovChain = nx.DiGraph()

#Collection of the states
NodeList = list(itertools.product(*[[0,1,2]]*NodeNumber))

JointMarkovChain.add_nodes_from(NodeList)


for elem in NodeList:
    NodeStatus       = elem
    SusceptibleNodes = []
    InfectedNodes    = []
    RecoveryNodes    = []

    
    for Node in range(len(NodeStatus)):
        Status = list(NodeStatus)
        if int(Status[Node]) == 1:
            InfectedNodes.append(Node) 
        elif int(Status[Node]) ==2:
            RecoveryNodes.append(Node)
        else:
            SusceptibleNodes.append(Node)
            
    TotalProbabiltyOfChange = len(InfectedNodes)*Gamma

    JointMarkovChain.node[NodeStatus]["TotalProbabilty"] = round(TotalProbabiltyOfChange,4)

    
    if InfectedNodes == []:                
        JointMarkovChain.add_edge(NodeStatus,NodeStatus,weight = 1)
        JointMarkovChain.node[NodeStatus]["TotalProbabilty"] = 1
        
    else:
        for Node in range(len(NodeList)):
            [CharDif, PostionDif, ConnectionType] = CharacterDifferenceSIR(NodeStatus,NodeList[Node])
            if CharDif == 1 and ConnectionType != "NoConnection":
                if ConnectionType == "Recovery":
                    JointMarkovChain.add_edge(NodeStatus,NodeList[Node], weight = round(Gamma,4))
    
                else:   
                    InfectedNeighbours = 0 
                    for attachment in ConnectionMatrix.neighbors(PostionDif):
                        if attachment in InfectedNodes:
                            InfectedNeighbours +=1
                           
                    if InfectedNeighbours > 0:
                        JointMarkovChain.add_edge(NodeStatus,NodeList[Node], weight = round((InfectedNeighbours * Beta), 4))
                        JointMarkovChain.node[NodeStatus]["TotalProbabilty"]  += round((InfectedNeighbours * Beta), 4)
    
    if NodeStatus == NodeList[-1]:
        JointMarkovChain.node[NodeList[-1]]["TotalProbabilty"] = round(NodeNumber * Gamma,4) 


Ndim = range(len(NodeList))

for i,j in itertools.product(Ndim ,Ndim):
    if JointMarkovChain.has_edge(NodeList[i],NodeList[j]):
        Probability = JointMarkovChain[NodeList[i]][NodeList[j]]['weight']/JointMarkovChain.node[NodeList[i]]["TotalProbabilty"] 
        JointMarkovChain[NodeList[i]][NodeList[j]]['weight'] = round(Probability,4)






for i in Ndim:
    print(JointMarkovChain.node[NodeList[i]]["TotalProbabilty"] )
    

print(nx.adjacency_matrix(JointMarkovChain))

NodeList
pos = {
 (0, 0, 0):(0,0),
 (0, 0, 1):(1,0),
 (0, 0, 2):(1,3),
 (0, 1, 0):(1,1),
 (0, 1, 1):(2,0),
 (0, 1, 2):(2,3),
 (0, 2, 0):(1,4),
 (0, 2, 1):(2,4),
 (0, 2, 2):(2,5),
 (1, 0, 0):(1,2),
 (1, 0, 1):(2,1),
 (1, 0, 2):(2,6),
 (1, 1, 0):(2,2),
 (1, 1, 1):(3,0),
 (1, 1, 2):(3,1),
 (1, 2, 0):(2,7),
 (1, 2, 1):(3,2),
 (1, 2, 2):(3,3),
 (2, 0, 0):(1,5),
 (2, 0, 1):(2,8),
 (2, 0, 2):(2,10),
 (2, 1, 0):(2,9),
 (2, 1, 1):(3,4),
 (2, 1, 2):(3,5),
 (2, 2, 0):(3,6),
 (2, 2, 1):(3,7),
 (2, 2, 2):(4,0)} 
labels = nx.get_edge_attributes(JointMarkovChain,'weight')
nx.draw_networkx(JointMarkovChain,edge_labels=labels,pos=pos)

Totalweight = 0
for i,j in itertools.product(Ndim ,Ndim):
    if JointMarkovChain.has_edge(NodeList[i],NodeList[j]):
        Totalweight += JointMarkovChain[NodeList[i]][NodeList[j]]['weight']
        

NodeListArrangement = NodeList[1:]
Q  = nx.adjacency_matrix(JointMarkovChain,nodelist= NodeListArrangement ).todense()[:7,:7]
R = nx.adjacency_matrix(JointMarkovChain,nodelist= NodeListArrangement ).todense()[:7,7]
        
Q = np.array([[0.3,0.3,0.3,0.05],[0.2,0.3,0.35,0.1],[0.2,0.3,0.35,0.1],[0.1,0.1,0.1,0.39]])
R = np.array([[0.05,0],[0.05,0],[0.05,0],[0.01,0.3]])

        
""" Fundamental Matrix Section """

def expected_steps_fast(Q):
    I = np.identity(Q.shape[0])
    FundamentalMatrix = np.linalg.inv(I-Q)
    
    return(FundamentalMatrix)
    
    
    
FM = expected_steps_fast(Q)   
FM = np.matmul(FM,R)