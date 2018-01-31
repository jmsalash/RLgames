#!/bin/env/python

import os
import thread
import time

def doExperiment(game, gameext, rows, cols, agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, expid_from, exp_id_to):

    gameshortname = game[0]
    agentshortname = agent[0]
    gamecfg = '%s%s' %(game,gameext) 
    basetrainfilename = '%s%d%d%s_%s' %(gameshortname, rows, cols, gameext, agentshortname)
    if (gamma<1):
        basetrainfilename = basetrainfilename + '_g0%d' %(int(gamma*100))
    if (epsilon>0):
        basetrainfilename = basetrainfilename + '_e0%d' %(int(epsilon*100))
    if (lambdae>0):
        basetrainfilename = basetrainfilename + '_l0%d' %(int(lambdae*100))
    if (alpha>0):
        basetrainfilename = basetrainfilename + '_a0%d' %(int(alpha*100))
    if (nstep>1):
        basetrainfilename = basetrainfilename + '_n%d' %(nstep)

    for i in range(expid_from, exp_id_to+1):
        cmd = "xterm -geometry 100x20+0+20 -e \"python game.py %s %s %s_%02d -rows %d -cols %d -gamma %f -epsilon %f -lambdae %f -alpha %f -nstep %d -niter %d -maxtime %d\" " %(gamecfg,agent,basetrainfilename,i,rows,cols, gamma,epsilon,lambdae,alpha,nstep,niter,maxtime)
        # use -hold and & at the end for parallel execution and monitoring
        print cmd
        os.system(cmd)
        #thread.start_new_thread( os.system, (cmd,) )
        time.sleep(1)



agent = 'Sarsa'
gamma = 0.99
epsilon = 0.2
lambdae = -1
alpha = 0.1
nstep = 500
niter = -1

rows = 4
cols = 4
        
# main

maxtime = 600

doExperiment('Breakout','NRA', rows, cols, agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 1, 1) 

maxtime = 120

#doExperiment('Breakout','BFNRA', rows, cols, agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 1, 3) 





#maxtime = 1200

#doExperiment('Breakout','2D',agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 1, 7) 

#doExperiment('Breakout','2DC',agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 1, 7) 

agent = 'Q'

#doExperiment('Breakout','2',agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 2, 3) 

#doExperiment('Breakout','2C',agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 1, 3) 

#doExperiment('Breakout','2D',agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 2, 3) 

#doExperiment('Breakout','2DC',agent, gamma, epsilon, lambdae, alpha, nstep, niter, maxtime, 1, 3) 


