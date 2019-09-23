#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 15:11:03 2019

@author: Scott
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:49:56 2019

@author: Scott
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 19:00:34 2019

@author: Scott
"""

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt


# Total population, N.
N = 100
# Initial number of infected and the probability of a node being absoultely susceptible or not susceptible. 

n  = 99     #Total number of Suceptibles
r0 = 0      #Initally Recovered nodes
p  = 0.25   #Probabilty of a node not having the ability to recover. 

s0 = np.random.binomial(n, p)
S0 = n - s0 - r0
ρs  = s0/(S0+ s0)


i0 = np.random.binomial(N-n, p)
I0 = N - n - r0 - i0
ρi  = i0/(I0+ i0)


# Initial conditions vector 
y0 = (S0, I0, s0, i0, r0)

# Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
τ, γ = 0.05, 0.5
# A grid of time points (in days)
t = np.linspace(0, 10, 160)
    
# The SIR model differential equations.
def deriv(y, t, N, τ, γ):
    S, I, s, i, r = y
    
    SI = S*I
    Si = S*i
    sI = s*I
    si = s*i
    
    dS      = -τ*( SI + Si ) 
    dI      =  τ*( SI + Si ) - γ*I
    di      =  τ*( sI + si )
    ds      = -τ*( sI + si )  
    dr      = γ*I
    return(dS, dI, ds, di, dr)



# Integrate the SIR equations over the time grid, t.
ret = odeint(deriv, y0, t, args=(N, τ, γ))
S, I, s, i, r = ret.T

# Plot the data on three separate curves for S(t), I(t) and R(t)
fig = plt.figure(facecolor='w')
ax = fig.add_subplot(111, axisbelow=True)
#ax.plot(t, (S)/100, 'b', alpha=0.5, lw=2, label='Susceptible')
#ax.plot(t, (I)/100, 'r', alpha=0.5, lw=2, label='Infected')
#ax.plot(t, (s)/100, 'b', alpha=0.5, lw=2, label='Susceptible')
#ax.plot(t, (i)/100, 'r', alpha=0.5, lw=2, label='Infected')

ax.plot(t, (S+s)/100, 'g', alpha=0.5, lw=2, label='Total Susceptible')
ax.plot(t, (I+i)/100, 'r', alpha=0.5, lw=2, label='Total Infected')
ax.plot(t,   (r)/100, 'b', alpha=0.5, lw=2, label='Remaining Infected')



#ax.plot(t, R/1000, 'g', alpha=0.5, lw=2, label='Recovered with immunity')

ax.set_xlabel('Time /days')
ax.set_ylabel('Number (1000s)')
#ax.set_ylim(0,1.1)
ax.yaxis.set_tick_params(length=0)
ax.xaxis.set_tick_params(length=0)
ax.grid(b=True, which='major', c='w', lw=2, ls='-')
legend = ax.legend()
legend.get_frame().set_alpha(0.8)

#for spine in ('top', 'right', 'bottom', 'left'):
    #ax.spines[spine].set_visible(False)
    
plt.show()