#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 15:58:13 2019

@author: Scott
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Driven SIR Epidemic Model 

function fast SIR(G,τ, γ, initial infecteds, tmax) times, S, I, R ← [0], [|G|], [0], [0]
    Q ← empty priority queue
for u in G.nodes do
    u.status ← susceptible
    u.pred inf time ← ∞ for u in initial infecteds do
    
Event ← {node: u, time: 0, action: transmit} u.pred inf time ← 0
add Event to Q

while Q is not empty do
    Event ← earliest remaining event in Q if Event.action is transmit then ◃ ordered by time
       if Event.node.status is susceptible then
process trans SIR(G, Event.node, Event.time, τ, γ, times, S, I, R, Q, tmax)
else
process rec SIR(Event.node, Event.time, times, S, I, R) return times, S, I, R
"""
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt 
import sys
from datetime import datetime


def Event_Driven_Probabilistic_SIR(G, Recovery_Probabilty, τ, γ, initial_infecteds, tmax, seed_value = 100):

    """
    G - Networkx graph
    τ - per Edge Infection Rate
    γ - Recovery  Rate
    tmax - Maximum time for the model to run
    initial_infecteds - Initial number of infected. 
    
    """
    
    """Set up Inital Values"""
    Checks = True
    np.random.seed(seed_value)
    RepcoveryProbabilty = np.random.RandomState(seed_value)
    times, S, I, R , N = [0], [len(list(G.nodes()))-initial_infecteds], [initial_infecteds], [0], range(len(list(G.nodes())))
    Infected_Nodes = list(np.random.choice(list(N),initial_infecteds, replace = False))
    Susceptible_Nodes   = []
    Recovered_Nodes     = []
    
    """Priority Queue """
    dtype = [('NodeLabel', float), ('Time', float), ('EventType', float)]
    #[('Arthur', 1.8, 41), ('Lancelot', 1.9, 38),('Galahad', 1.7, 38)]
    Priority_Queue = np.array([], dtype=dtype)
    
    
    for nodes in N:
        #Sets up the Recovery type of the node
        if Recovery_Probabilty < RepcoveryProbabilty.uniform():
            G.node[nodes]["Recovery_Type"] = "Recovery"
        else:
            G.node[nodes]["Recovery_Type"] = "Non_Recovery"

        if nodes not in Infected_Nodes: 
            G.node[nodes]["Status"] = "Susceptible"
            Susceptible_Nodes.append(nodes)
            G.node[nodes]["Predicted_Infection_Time"] = tmax
        else: 
            G.node[nodes]["Status"] = "Infected"
            G.node[nodes]["Predicted_Infection_Time"] = 0

            
    for nodes in Infected_Nodes:  
        #Sets up the Recovery time depended on its type
        if G.node[nodes]["Recovery_Type"] == "Recovery":
            Recovery_Time = times[-1] + np.random.exponential(1/γ)
            G.node[nodes]["Recovery_Time"] = Recovery_Time
            event = np.array([(nodes, Recovery_Time, 2)],  dtype=dtype)
            Priority_Queue = np.append(Priority_Queue, event)
        else:
            G.node[nodes]["Recovery_Time"] = tmax
            
            
            
        for neighbour in G.neighbors(nodes):
            if G.node[neighbour]["Status"] == "Susceptible":
                Infection_Time = times[-1] + np.random.exponential(1/τ)
                if Infection_Time < G.node[nodes]["Recovery_Time"]:
                    G.node[neighbour]["Predicted_Infection_Time"] = Infection_Time
                    #Infection is type 1 and Recovery is type 2
                    event = np.array([(neighbour, Infection_Time, 1)],  dtype=dtype)
                    Priority_Queue = np.append(Priority_Queue, event)
                
                
    Priority_Queue = np.sort(Priority_Queue, order='Time')  
    S.append(len(Susceptible_Nodes))
    I.append(len(Infected_Nodes))
    R.append(len(Recovered_Nodes)) 
    times.append(0) 
    
    while Priority_Queue.size != 0:
    
        CurrentEvent = Priority_Queue[0]
        Priority_Queue = Priority_Queue[1:]
        CurrentTime = CurrentEvent[1]

        
        """
        Event Key
        1.0 = Infection
        2.0 = Recovery
        """
        
        if CurrentEvent[2] == 1.0:
            
            
            #If susceptible we add recovery time to queue and add potential infected nodes to queue
            if G.node[CurrentEvent[0]]["Status"] == "Susceptible":
                #We set the nodes new status and recovery time
                G.node[CurrentEvent[0]]["Status"] = "Infected"
                Susceptible_Nodes.remove(int(CurrentEvent[0]))
                Infected_Nodes.append(CurrentEvent[0])
                
                if  G.node[CurrentEvent[0]]["Recovery_Type"] == "Recovery":
                    Recovery_Time = CurrentTime + np.random.exponential(1/γ)
                    G.node[CurrentEvent[0]]["Recovery_Time"] = Recovery_Time
                    event = np.array([(CurrentEvent[0], Recovery_Time, 2)],  dtype=dtype)
                    idx = Priority_Queue['Time'].searchsorted(Recovery_Time)
                    Priority_Queue = np.concatenate((Priority_Queue[:idx], event, Priority_Queue[idx:]))
                else:
                    G.node[CurrentEvent[0]]["Recovery_Time"] = tmax
                
                for neighbour in G.neighbors(CurrentEvent[0]):
                    if G.node[neighbour]["Status"] == "Susceptible":
                        Infection_Time = CurrentTime + np.random.exponential(1/τ)
                        if Infection_Time < G.node[CurrentEvent[0]]["Recovery_Time"]:
                            if Infection_Time < G.node[neighbour]["Predicted_Infection_Time"]:
                                G.node[neighbour]["Predicted_Infection_Time"] = Infection_Time
                                #Infection is type 1 and Recovery is type 2
                                event = np.array([(neighbour, Infection_Time, 1)],  dtype=dtype)
                                idx = Priority_Queue['Time'].searchsorted(Infection_Time)
                                Priority_Queue = np.concatenate((Priority_Queue[:idx], event, Priority_Queue[idx:]))
                #Saving Values             
                TempS = len(Susceptible_Nodes)
                TempI = len(Infected_Nodes) 
                TempR = len(Recovered_Nodes)
                
                if TempS + TempI + TempR != len(list(N)):
                    print("Unfortunately, S + I + R does not equal N.")
                    
                if not (S[-1] == TempS and TempI == I[-1] and TempR == R[-1] ):
                    S.append(len(Susceptible_Nodes))
                    I.append(len(Infected_Nodes))
                    R.append(len(Recovered_Nodes))
                    times.append(CurrentTime) 
                    
        else:
            """A Node is Recovered"""
            if G.node[CurrentEvent[0]]["Status"] == "Infected":
                if G.node[CurrentEvent[0]]["Recovery_Type"] == "Recovery":
                    G.node[CurrentEvent[0]]["Status"] = "Recovered"
                    Infected_Nodes.remove(int(CurrentEvent[0]))
                    Recovered_Nodes.append((int(CurrentEvent[0])))
                    
                    #Saving Values             
                    TempS = len(Susceptible_Nodes)
                    TempI = len(Infected_Nodes) 
                    TempR = len(Recovered_Nodes)
                    
                    if TempS + TempI + TempR != len(list(N)):
                        print("Unfortunately, S + I + R does not equal N.")
                    
                       
                    if not (S[-1] == TempS and TempI == I[-1] and TempR == R[-1] ):
                        S.append(len(Susceptible_Nodes))
                        I.append(len(Infected_Nodes))
                        R.append(len(Recovered_Nodes))
                        times.append(CurrentTime) 
                else:
                    print(CurrentEvent[0])
                    sys.exit
               
            else:
               print("Error: node trying to recover before Infected!")
               sys.exit
               
        if Checks == True:
            """ Recording values"""
            if Priority_Queue.size > 1:
                if np.diff(Priority_Queue['Time']).any()<=0:
                    print("Error: Queue is not sorted!")
                    print(Priority_Queue['Time'])
                    sys.exit
        
        for x in Priority_Queue:
            if G.node[x[0]]["Recovery_Type"] == "Non_Recovery" and x[2] == 2.0:
                print("yes")
                print(x)
            

            
    return(times, S, I, R)




Recovery_Probabilty = 0.1
G = nx.erdos_renyi_graph(1000, 0.1)
initial_infecteds = 1
τ, γ = 0.1, 4.0
seed_value = 101
tmax = 20


times, S, I, R  = Event_Driven_Probabilistic_SIR(G, Recovery_Probabilty, τ, γ, initial_infecteds, tmax, seed_value = 100)

plt.plot( times,I, 'red')
plt.plot( times,S, 'Green')
plt.plot( times,R, 'Blue')

print("S = " + str(S[-1]))
print("I = " + str(I[-1]))
print("R = " + str(R[-1]))

times, S, I, R  = Event_Driven_SIR(G, τ, γ, initial_infecteds , tmax, seed_value = 100) 

plt.plot( times,I, 'red')
plt.plot( times,S, 'Green')
plt.plot( times,R, 'Blue')

print("S = " + str(S[-1]))
print("I = " + str(I[-1]))
print("R = " + str(R[-1]))