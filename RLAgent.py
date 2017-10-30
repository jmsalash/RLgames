import pygame, sys
import numpy as np
import random
import time
import math
from math import fabs


class RLAgent():

    def __init__(self):
        self.command = 0
        self.alpha = 0.5 # -1: adative
        self.gamma = 1.0
        self.epsilon = -1 #  -1: adaptive
        self.optimal = False
        self.episode = []
        self.iteration = 0
        self.debug = False
        self.name = 'RL'

        
    def init(self, nstates, nactions):
        self.Q = np.zeros((nstates,nactions))
        self.Visits = np.zeros((nstates,nactions))
        self.nactions = nactions

    def savedata(self):
         return [self.Q, self.Visits]
         
    def loaddata(self,data):
         self.Q = data[0]
         self.Visits = data[1]
         
        
    def getQ(self, x, a):
        return self.Q[x,a]

    def getQA(self, x):
        return self.Q[x,:]
        
    def setQ(self, x, a, q):
        self.Q[x,a] = q

    def incVisits(self, x, a):
        self.Visits[x,a] += 1
        # print "Visits ",x," <- ",self.Visits[x,:]

    def getVisits(self, x, a):
        return self.Visits[x,a]

    def getSumVisits(self, x):
        return np.sum(self.Visits[x,:])


    def choose_action(self, x):  # choose action from state x

        if (self.epsilon < 0):
            s = self.iteration #getSumVisits(x)
            k = 0.01 # decay weight 
            deltaS = 5000 # 0.5 value
            ee = math.exp(-k*(s-deltaS))
            epsilon = 0.9 * (1.0 - 1.0 / (1.0 + ee)) + 0.05
            #print "  -- visits = ",s,"  -- epsilon = ",epsilon
        else:
            epsilon = self.epsilon
        
        if ((not self.optimal) and random.random()<epsilon):
            # Random action
            com_command = random.randint(0,self.nactions-1)
        else:
            # Choose the action that maximizes expected reward.            
            Qa = self.getQA(x)
            va = np.argmax(Qa)
            
            maxs = [i for i,v in enumerate(Qa) if v == va]
            if len(maxs) > 1:
                if self.command in maxs:
                    com_command = self.command
                elif self.optimal:
                    com_command = maxs[0]
                else:
                    com_command = random.choice(maxs)
            else:
                com_command = va

        return com_command

        
    def decision(self, x):
        
        a = self.choose_action(x)
        if self.debug:
            print "Q: ",x," -> ",self.getQA(x)
            print "Decision: ",x,"  -> ",a

        return a
        
    def notify(self, x, a, r, x2):

        if (self.debug):
            print "Q update ",x," r: ",r
        
        self.episode.append((x,a,r))
        
        self.updateQ(x,a,r,x2)


    def getActionValue(self, x2):
        print("ERROR: function getActionValue not implemented")
        return 0

        
    def updateQ(self,x,a,r,x2,a2=None):
    
        if (self.optimal):  # executes best policy, no updates
            return

        # Q of current state
        prev_Q = self.getQ(x,a)
        
        if (not a2 is None):
            # a2 given
            vQa = self.getQ(x2,a2)
        else:
            vQa = self.getActionValue(x2)

        
        if (self.debug):
            print ' == ',x,' A: ',a,' -> r: ',r,' -> ',x2,'  A: ',a2,' prev_Q: ', prev_Q, '  vQa: ', vQa
            print ' == Q update Q ',x,',',a,' <-  ...  Q ',x2,',',a2,' = ', vQa

        if (self.alpha>=0):
            alpha = self.alpha
        else:
            self.incVisits(x,a)
            k = 1
            s = self.getVisits(x,a)
            alpha = 1.0/s # math.sqrt(s)
    
        # print "alpha = ",alpha
        # print "gamma = ",self.gamma
        
        q = prev_Q + alpha * (r + self.gamma * vQa - prev_Q)
        self.setQ(x,a,q)
        

                
    def updateQ_episode(self):
    
        if (self.optimal):  # executes best policy, no updates
            return

        # update all states in this episode
        if (self.debug):
            print self.episode
        k = len(self.episode)-1
        sa1=self.episode[k]
        x1 = sa1[0] # current state
        a1 = sa1[1] # current action
        if (self.debug):
            print x1,' ',a1,'    Q: ', self.getQ(x1,a1) 
        k -= 1
        while (k>=0): # visit states in reverse order
            sa1=self.episode[k]
            sa2=self.episode[k+1]
            x1 = sa1[0] # current state
            a1 = sa1[1] # current action
            r1 = sa1[2] # reward
            x2 = sa2[0] # next state
            a2 = sa2[1] # next action

            self.updateQ(x1,a1,r1,x2,a2)
            
            if (self.debug):
                print x1,' A: ',a1,' -> r: ',r1,' -> ',x2,'   Q: ', self.getQ(x1,a1) 
                
            k -= 1
        if (self.debug):
            sys.exit(1)            

    def notify_endofepisode(self, iter):
        self.iteration = iter
        self.updateQ_episode()
        self.episode = []


class QAgent(RLAgent):

    def __init__(self):
        RLAgent.__init__(self)

    def getActionValue(self, x2):
        # Q-learning
        maxQa = max(self.getQA(x2)) 
        return maxQa


class SarsaAgent(RLAgent):

    def __init__(self):
        RLAgent.__init__(self)

    def getActionValue(self, x2):
        # Sarsa
        sarsa_a = self.choose_action(x2)
        sarsaQa = self.getQ(x2,sarsa_a) 
        return sarsaQa
        