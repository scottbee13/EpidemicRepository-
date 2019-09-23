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


def CharacterDifference(a,b):
    #Detect the Number of difference between 2 strings.
    CharacterDiff = 0 
    DifferenceLocation = -1
    if len(a) != len(b):
        print("Error: The length of these strings are no the same.")
        sys.exit()
    else:
        for i in range(len(b)): 
            if list(a)[i] != list(b)[i]:
                CharacterDiff += 1
                DifferenceLocation = i
            
    return([CharacterDiff, DifferenceLocation])


"""Graph we wish to gather the Jointly Markov Chain for"""
ConnectionMatrix =  nx.Graph()
ConnectionMatrix.add_edges_from([(1,2),(2,3),(3,0),(0,1)])

ConnectionMatrix =  nx.Graph()
ConnectionMatrix.add_edges_from([(0,1),(1,2),(2,0)])


Beta  = 0.15
Gamma = 0.6
StateNumber = 2


#Test - Max Number of Nodes and States
NodeNumber = len(ConnectionMatrix.nodes())
StateNumber = 2

if NodeNumber > 25 or StateNumber > 3:
    print("This model only works for small number of nodes and States.  Remember that the number of states in the extended Markov Chain is StateNumber ** (Number of Nodes)." )
    print("In this model you would have " + str(StateNumber ** NodeNumber) + " number of possible states.")

""" Construction of the Joint Markov Chain"""

JointMarkovChain = nx.DiGraph()

#Collection of the states
NodeList = []
for states in range(StateNumber**len(ConnectionMatrix.nodes())):
    Label = format(int(str(bin(states))[2:]), "0" + str(NodeNumber) + "d")
    NodeList.append(Label)

JointMarkovChain.add_nodes_from(NodeList)

  
           

for elem in NodeList:
    
    
    NodeStatus       = elem
    SusceptibleNodes = []
    InfectedNodes    = []
    #RecoveryNodes    = []

    
    for Node in range(len(NodeStatus)):
        Status = list(NodeStatus)
        if int(Status[Node]) == 1:
            InfectedNodes.append(Node) 
    
    TotalProbabiltyOfChange = len(InfectedNodes)*Gamma
    JointMarkovChain.node[NodeStatus]["TotalProbabilty"] = round(TotalProbabiltyOfChange,4)
            
        #elif Status ==2:
            #RecoveryNodes.append(Node)
            
    #Add recovery values to the joint markov change
    
    if InfectedNodes == []:                
        JointMarkovChain.add_edge(NodeStatus,NodeStatus,weight = 1)
        JointMarkovChain.node[NodeStatus]["TotalProbabilty"] = 1
        
    else:
        for Node in range(len(NodeList)):
            if NodeStatus > NodeList[Node]:
                [CharDif, PostionDif] = CharacterDifference(NodeStatus,NodeList[Node])
                if CharDif == 1:
                    JointMarkovChain.add_edge(NodeStatus,NodeList[Node], weight = round(Gamma,4))
    
            else:   
                [CharDif, PostionDif] = CharacterDifference(NodeStatus,NodeList[Node])
                if CharDif == 1:
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
    JointMarkovChain.node[NodeList[i]]["TotalProbabilty"]  = round(JointMarkovChain.node[NodeList[i]]["TotalProbabilty"] , 4)
    print(JointMarkovChain.node[NodeList[i]]["TotalProbabilty"] )
    

print(nx.adjacency_matrix(JointMarkovChain))




Totalweight = 0
for i,j in itertools.product(Ndim ,Ndim):
    if JointMarkovChain.has_edge(NodeList[i],NodeList[j]):
        Totalweight += JointMarkovChain[NodeList[i]][NodeList[j]]['weight']
        
        
NodeListArrangement = NodeList[1:]
#NodeListArrangement = NodeList[1:]+ [NodeList[0]]
Q  = nx.adjacency_matrix(JointMarkovChain,nodelist= NodeListArrangement ).todense()
R = nx.adjacency_matrix(JointMarkovChain,nodelist= NodeListArrangement ).todense()
 
"""       
Q = np.array([[0.3,0.3,0.3,0.05],[0.2,0.3,0.35,0.1],[0.2,0.3,0.35,0.1],[0.1,0.1,0.1,0.39]])
R = np.array([[0.05,0],[0.05,0],[0.05,0],[0.01,0.3]])
"""
        
""" Fundamental Matrix Section """

def expected_steps_fast(Q):
    I = np.identity(Q.shape[0])
    FundamentalMatrix = np.linalg.inv(I-Q)
    
    return(FundamentalMatrix)
    
    
    
FM = expected_steps_fast(Q)   
FM = np.matmul(FM,R)