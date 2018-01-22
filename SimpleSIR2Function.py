# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 21:43:51 2018

@author: stb
"""


import networkx as nx
import random
import numpy
from operator import itemgetter
import matplotlib.pyplot as plt
import datetime

def SIRModel( beta = .1, gamma = .01, Susceptible = 1000, Infected = 1, Recovered = 0, seed = 123):
    """This is a simple SIR function, that spreads along our genertated network"""
    #Set up initial Conditions
    t = 0

    #List for tracking state numbers for each discrete time step.
    SusceptibleList = []
    InfectedList = []
    RecoveredList = []
    NewlyInfectedList = []
    RecoveryTimeslist = []

    #Construct our graph
    #We will obviously chaneg this and add in our multilayer network later.
    p = .02
    k = 5
    n = Susceptible
    graph = nx.newman_watts_strogatz_graph(n, k, p, seed=seed)
    # =============================================================================
    #       n (int) – The number of nodes
    #       k (int) – Each node is joined with its k nearest neighbors in a ring topology.
    #       p (float) – The probability of rewiring each edge
    #       seed (int, optional) – Seed for random number generator (default=None)
    # =============================================================================

    #Adjancey list of lists, required so each node infects the next node.
    adjacencyList = []
    [adjacencyList.append([i]+list(graph.neighbors(i))) for i in graph.node()]

    #Assign our seed value
    numpy.random.seed(seed)

    #Setting all node to Susceptible
    SusceptibleList = list(graph.node())

    """ This Section infects our intial I number of nodes"""
    IntailInfected = Infected

    for i in range(0,IntailInfected):
        #Randomly infect a node
        InfectedAgent = numpy.random.randint(0,graph.number_of_nodes())

        #Moving node lists
        InfectedList.append(InfectedAgent)
        SusceptibleList.remove(InfectedAgent)

        #Calculate Recovery Time
        recoveryTime = t + numpy.random.geometric(gamma, size=None)

        """Infection Rate"""
        #more efficient than looping over and drawing a random number every time.
        #use 1/gamma to get the expected duration of infectiousness
        #Geometric Distrubiton
        #constant
        #exponentially distributed recovery times
        #normally distributed with mean 1/g

        NewlyInfectedList.append(['Intial', InfectedAgent, t, recoveryTime])
        RecoveryTimeslist.append([InfectedAgent,recoveryTime])


    """ This Section sets an intial number of nodes as Recoverd."""
    #Tbh, this bit isnt really necesary but thought I would include it for completeness.
    for i in range(0,Recovered):
        #Randomly infect a node
        RecoveredAgent = random.randint(0,graph.number_of_nodes())

        #Moving node lists
        RecoveredList.append(RecoveredAgent)
        SusceptibleList.remove(RecoveredAgent)

        NewlyInfectedList.append(['Intial Recovery', RecoveredAgent, t, t])

    #Sort the NewlyInfectedList by recovery time.
    sorted(NewlyInfectedList, key=itemgetter(3))

    """ Main Loop, Cylces through each nodes and infect the others"""
    t=1
    while len(SusceptibleList)>0:
        #We first cycle through each infected node,Where we infect
        #its susceptible neighbour if we acheive or required beta result.
        for iagent in InfectedList:
            for agent in adjacencyList[iagent]:
                if agent in SusceptibleList:
                    if (random.random() < beta):
                        #We then infect this node.
                        SusceptibleList.remove(agent)
                        #Gather its recovery time
                        recoveryTime = t + numpy.random.geometric(gamma, size=None)
                        #Append this info to the appropiate list
                        NewlyInfectedList.append([iagent, agent, t, recoveryTime])
                        RecoveryTimeslist.append([agent,recoveryTime])
                        RecoveryTimeslist=sorted(RecoveryTimeslist, key=itemgetter(1))

         #Add all the newly infected nodes to our infected list.
        [InfectedList.append(i[1]) for i in  NewlyInfectedList if i[2]==t]

        """ Recovery Section"""
        if len(RecoveryTimeslist)>0:
            #need to change this section into a list check that stops the first time it doesnt work
            for RecoveredAgent in RecoveryTimeslist:
                RecoveryTimeslist=sorted(RecoveryTimeslist, key=itemgetter(1))
                if RecoveredAgent[1]>t:
                    break
                elif RecoveredAgent[1] == t:
                    #Moving node lists
                    InfectedList.remove(RecoveredAgent[0])
                    RecoveredList.append(RecoveredAgent[0])
                    RecoveryTimeslist.remove(RecoveredAgent)

        #Move the time on one step.
        t+=1

    """imputs this data as metadata on the graph"""
    for node in NewlyInfectedList:
        graph.node[node[1]]['Infectedby']= node[0]
        graph.node[node[1]]['InfectedTime']= node[2]
        graph.node[node[1]]['RecoveryTime']= node[3]

    return NewlyInfectedList


def StatusPerTime(NewlyInfectedList):
    max=0
    for i in NewlyInfectedList:
        if i[3] > max:
            max=i[3]

    RecoveredperTime = []
    recoverednumber = 0
    for t in range(max+1):
        for node in NewlyInfectedList:
            if node[3]==t:
                recoverednumber+=1
        RecoveredperTime.append(recoverednumber)

    infectednumber=0
    InfectedperTime=[]
    for t in range(max+1):
        for node in NewlyInfectedList:
            if node[2]==t:
                infectednumber+=1
        InfectedperTime.append(infectednumber- RecoveredperTime[t])


    SusceptibleperTime=[]
    for i in range(max+1):
        SusceptibleperTime.append(len(NewlyInfectedList) - InfectedperTime[i] - RecoveredperTime[i])

    output=[]
    for i in range(max+1):
        output.append([SusceptibleperTime[i],InfectedperTime[i],RecoveredperTime[i] ])
    return output

"""Plots our Status Information"""
def PlotStatus(StatusInfo):
    t=range(len(StatusInfo))
    InfectedNumbers = []
    RecoveredNumbers = []
    SusceptibleNumbers = []

    for i in StatusInfo:
        InfectedNumbers.append(i[1])
        RecoveredNumbers.append(i[2])
        SusceptibleNumbers.append(i[0])

    plt.plot(t,InfectedNumbers,'red')
    plt.plot(t,RecoveredNumbers,'blue')
    plt.plot(t,SusceptibleNumbers,'green')
    plt.show()


SirInfo = SIRModel(beta=0.25, gamma = 0.05, Susceptible = 100, Infected = 2, Recovered = 0, seed=123)

StatusInfo= StatusPerTime(SirInfo)

PlotStatus(StatusInfo)


""" Gif Creation """
""" This section saves a pic at each stage and makes them into a gif"""
""" Tbh, not that useful but i wanted to see if all the steps it took made sense"""

import imageio
def ConstructGif(SirInfo,graph):
    max=0
    for i in SirInfo:
        if i[3] > max:
            max=i[3]

    for t in range(max):
        ColourList=[]
        for node in SirInfo:
            #We colour the node red if it is infected.
            if graph.node[node[1]]['InfectedTime'] <= t and t < graph.node[node[1]]['RecoveryTime']:
                ColourList.append('red')
            elif graph.node[node[1]]['RecoveryTime']<=t:
                ColourList.append('blue')
            else:
                ColourList.append('green')

        Name='t = '+str(t)
        nx.draw(graph,nx.circular_layout(graph,scale = 0.25), node_color=ColourList)
        plt.savefig(Name+'.png',bbox_inches='tight')

    images=[]
    duration=[]
    for t in range(max):
        if t <13:
            duration.append(0.5)
        else:
            duration.append(0.10)

        Name='t = '+str(t)
        images.append(imageio.imread(Name+'.png'))
    output_file = 'Gif-%s.gif' % datetime.datetime.now().strftime('%Y-%M-%d-%H-%M-%S')
    imageio.mimsave(output_file, images, duration=duration)

    return 1