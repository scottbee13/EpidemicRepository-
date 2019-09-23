#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gillespie Version of the SIR model 

function Gillespie network epidemic(G, τ, γ, initial infections, tmax)
times, S, I, R ← [0], [|G|-len(initial infections)], [len(initial infections)], [0]
infected nodes ← initial infections
at risk nodes ← uninfected nodes with infected neighbours
for each node u in at risk nodes do
infection rate[u] = τ× number of infected neighbours
total infection rate ← ∑u∈at risk nodes infection rate[u],
total recovery rate ← γ× len(infected nodes)
total rate ← total transmission rate + total recovery rate
time ← exponential variate(total rate)
while time< tmax and total rate> 0 do
r = uniform random(0,total rate)
if r <total recovery rate then
u = random.choice(infected nodes)
remove u from infected nodes
reduce infection rate[v] for u’s susceptible neighbours v
else
choose u from at risk nodes with probability infection rate[u]
total infection rate .
remove u from at risk nodes
add u to infected nodes
for susceptible neighbours v of u do
if v not in at risk nodes then
add v to at risk nodes
update infection rate[v]
update times, S, I, and R
update total recovery rate, total infection rate, and total rate
time ← time + exponential variate(total rate)
return times, S, I, R
"""
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt 
import sys

G = nx.complete_graph(300)
initial_infecteds = 1
τ, γ = 0.1, 1
seed_value = 100
tmax = 20

def Gillespie_network_epidemic_SIR(G, τ, γ, initial_infecteds , tmax, seed_value = 100):
    
    """
    G - Networkx graph
    τ - per Edge Infection Rate
    γ - Recovery  Rate
    tmax - Maximum time for the model to run
    initial_infecteds - Initial number of infected. 
    
    """
    
    """Set up Inital Values"""
    np.random.seed(seed_value)
    times, S, I, R , N = [0], [len(list(G.nodes()))-initial_infecteds], [initial_infecteds], [0], range(len(list(G.nodes())))
    Infected_Nodes = np.random.choice(list(N),initial_infecteds, replace = False)
    Susceptible_Nodes   = []
    Recovered_Nodes     = []
    
    for nodes in N:
        if nodes in Infected_Nodes:
            G.node[nodes]["Status"] = "Infected"
        else: 
            G.node[nodes]["Status"] = "Susceptible"
            Susceptible_Nodes.append(nodes)
            
            
    """ Gathers the rates used in the algorthim."""        
    Total_Infection_Rate, Total_Recovery_Rate, Total_Rate, Time, Infection_Rate, at_risk_nodes  =  Gillespie_Rates(G, Infected_Nodes, τ, γ)

 
    
    while times[-1] < tmax and Total_Rate > 0:
    
        r = np.random.uniform(0,Total_Rate)
        
        if r < Total_Recovery_Rate :
            """Node will Recover"""
            Recovering_Node = np.random.choice(Infected_Nodes)
            Infected_Nodes  = np.delete(Infected_Nodes, list(Infected_Nodes).index(Recovering_Node))
            Recovered_Nodes = np.append(Recovered_Nodes, Recovering_Node)
            
            
        else:
            """Node will be Infected"""
            Total_Sum, weights, NodeLabels = 0, [], []
            for node in Infection_Rate:
                Total_Sum += node[2]
                NodeLabels.append(node[0])
                weights.append(node[2])
                
            weights = [node_weight/Total_Sum for node_weight in weights]
            ChosenNode = np.random.choice(NodeLabels, p=weights)
            
            G.node[ChosenNode]["Status"] = "Infected"
            Infected_Nodes      = np.append(Infected_Nodes, ChosenNode )
            Susceptible_Nodes   = np.delete(Susceptible_Nodes, list(Susceptible_Nodes).index(ChosenNode))
           
            for node in G.neighbors(ChosenNode):
                if node not in at_risk_nodes:
                    Infection_Rate.append([node, τ, 1 ])
                    at_risk_nodes.append(node)
                else:
                    for node in  Infection_Rate:
                        if node[0] == ChosenNode:
                            node[2] += 1
             
        Total_Infection_Rate,Total_Recovery_Rate,Total_Rate, Time, Infection_Rate, at_risk_nodes   =  Gillespie_Rates(G, Infected_Nodes, τ, γ)
  
        if len(Susceptible_Nodes) + len(Infected_Nodes) + len(Recovered_Nodes) != len(list(N)):
            print("Unfortunately, S + I + R does not equal N.")
            
        S.append(len(Susceptible_Nodes))
        I.append(len(Infected_Nodes))
        R.append(len(Recovered_Nodes))
   
        times.append(times[-1] + Time) 
      
    return(times, S, I, R)



def At_Risk_Nodes(G, Infected_Nodes):
    """This function gathers all susceptible nodes attached to infected nodes"""
    at_risk_nodes = []
    for nodes in G.nodes():
        if G.node[nodes]["Status"] == "Susceptible":
            for infected in Infected_Nodes:
                if infected in G.neighbors(nodes):
                    at_risk_nodes.append(nodes)
             
    at_risk_nodes = list(set(at_risk_nodes))
    return(at_risk_nodes)
    
    
def Gillespie_Rates(G, Infected_Nodes, τ, γ):
    
    #Returns a list of nodes connected to infected nodes
    at_risk_nodes = At_Risk_Nodes(G, Infected_Nodes)
    
    Infection_Rate = []
    for nodes in at_risk_nodes:
        number_of_infected_neighbours = 0
        for neighbour in G.neighbors(nodes):
            if G.node[neighbour]["Status"] == "Infected":
                number_of_infected_neighbours += 1
                
        Infection_Rate.append([nodes, τ * number_of_infected_neighbours, number_of_infected_neighbours])
    

    Total_Infection_Rate = 0
    for Infection_force in Infection_Rate:    
        Total_Infection_Rate += Infection_force[1]
        
    Total_Infection_Rate    = round( Total_Infection_Rate, 4)
    Total_Recovery_Rate     = γ*len(Infected_Nodes)
    Total_Rate              = Total_Infection_Rate + Total_Recovery_Rate
    
    if Total_Rate >0:
        Time                = np.random.exponential(1/Total_Rate)
    else:
        Time = 0

    return(Total_Infection_Rate, Total_Recovery_Rate, Total_Rate, Time, Infection_Rate, at_risk_nodes)
    
    


times, S, I, R  = Gillespie_network_epidemic_SIR(G, τ, γ, initial_infecteds , tmax, seed_value = 100)  
plt.plot( times,I, 'red')
plt.plot( times,S, 'Green')
plt.plot( times,R, 'Blue')

    
