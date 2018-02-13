import pygame, sys, os
import numpy as np
import atexit
import random
import time
import math
from math import fabs

from ale_python_interface import ALEInterface

key_action_tform_table = (
0, #00000 none
2, #00001 up
5, #00010 down
2, #00011 up/down (invalid)
4, #00100 left
7, #00101 up/left
9, #00110 down/left
7, #00111 up/down/left (invalid)
3, #01000 right
6, #01001 up/right
8, #01010 down/right
6, #01011 up/down/right (invalid)
3, #01100 left/right (invalid)
6, #01101 left/right/up (invalid)
8, #01110 left/right/down (invalid)
6, #01111 up/down/left/right (invalid)
1, #10000 fire
10, #10001 fire up
13, #10010 fire down
10, #10011 fire up/down (invalid)
12, #10100 fire left
15, #10101 fire up/left
17, #10110 fire down/left
15, #10111 fire up/down/left (invalid)
11, #11000 fire right
14, #11001 fire up/right
16, #11010 fire down/right
14, #11011 fire up/down/right (invalid)
11, #11100 fire left/right (invalid)
14, #11101 fire left/right/up (invalid)
16, #11110 fire left/right/down (invalid)
14  #11111 fire up/down/left/right (invalid)
)


STATES = {
    'Init':0,
    'Alive':5000,
    'Dead':-500,
    'NotMoving':-2,
    'MoveFW':1,
    'MoveBW':-10,
    'Score':10,    
    'GotHit':-50,  
    'GotBlocked':-50,
    'GotUnblocked':200,      
}



class KungFuMaster(object):

    def __init__(self, rom= '/home/josema/AI/ALE/Arcade-Learning-Environment/Roms/kung_fu_master.bin', trainsessionname='test'):

        self.agent = None
        self.isAuto = True
        self.gui_visible = False
        self.userquit = False
        self.optimalPolicyUser = False  # optimal policy set by user
        self.trainsessionname = trainsessionname
        self.elapsedtime = 0 # elapsed time for this experiment
        

        self.keys = 0 
        
        # Configuration
        self.pause = False # game is paused
        self.debug = False
        
        self.sleeptime = 0.0
        self.command = 0
        self.iteration = 0
        self.cumreward = 0
        self.cumreward100 = 0 # cum reward for statistics
        self.cumscore100 = 0 
        self.ngoalreached = 0
        self.max_level = 1
        
        self.hiscore = 0
        self.hireward = -1000000
        self.resfile = open("data/"+self.trainsessionname +".dat","a+")

        
        self.legal_actions = 0
        self.rom=rom
        self.key_status = []
        
    def init(self, agent):  # init after creation (uses args set from cli)
        self.ale = ALEInterface()
        self.ale.setInt('random_seed', 123)
        ram_size = self.ale.getRAMSize()
        self.ram = np.zeros((ram_size),dtype=np.uint8)
        
        if (self.gui_visible):        
	    os.environ['SDL_VIDEO_CENTERED']='1'
            if sys.platform == 'darwin':
                pygame.init()
                self.ale.setBool('sound', False) # Sound doesn't work on OSX
            elif sys.platform.startswith('linux'):
                pygame.init()
                         
                self.ale.setBool('sound', True)
                self.ale.setBool('display_screen', False)
               
        self.ale.loadROM(self.rom)
        self.legal_actions=self.ale.getLegalActionSet()

        if (self.gui_visible):
            (self.screen_width,self.screen_height) = self.ale.getScreenDims()
            print("width/height: " +str(self.screen_width) + "/" + str(self.screen_height))
            
            (display_width,display_height) = (1024,420)
            self.screen = pygame.display.set_mode((display_width,display_height))
            
            pygame.display.set_caption("Reinforcement Learning - Sapienza - Jose M Salas")
            self.numpy_surface = np.zeros((self.screen_height,self.screen_width,3), dtype=np.uint8)
            
            self.game_surface = pygame.Surface((self.screen_width,self.screen_height))
            
            pygame.display.flip()
            #init clock
            self.clock = pygame.time.Clock()
        

        
        self.agent = agent
        self.nactions = len(self.legal_actions)  # 0: not moving, 1: left, 2: right, 3: up, 4: down
        for i in range(self.nactions):
            self.key_status.append(False)
            
        print(self.nactions)
#        ns = 89999 # Number of statuses if we use enemy type ram info without level number
#FINAL        ns = 489999 # Number of statuses if we use enemy type ram info
        ns = 4899999 # Number of statuses if we use enemy type ram info

#        ns = 48999
        print('Number of states: %d' %ns)
        self.agent.init(ns, self.nactions) # 1 for RA not used here

    def initScreen(self):
         
        if (self.gui_visible):        
            if sys.platform == 'darwin':
                pygame.init()
                self.ale.setBool('sound', False) # Sound doesn't work on OSX
            elif sys.platform.startswith('linux'):
                pygame.init()
               
               
                
                self.ale.setBool('sound', True)
                self.ale.setBool('display_screen', False)
        if (self.gui_visible):
            (self.screen_width,self.screen_height) = self.ale.getScreenDims()
            print("width/height: " +str(self.screen_width) + "/" + str(self.screen_height))
            
            (display_width,display_height) = (1024,420)
            self.screen = pygame.display.set_mode((display_width,display_height))
            
            pygame.display.set_caption("Reinforcement Learning - Sapienza - Jose M Salas")
            self.numpy_surface = np.zeros((self.screen_height,self.screen_width,3), dtype=np.uint8)
            
            self.game_surface = pygame.Surface((self.screen_width,self.screen_height))
            
            pygame.display.flip()
            #init clock
            self.clock = pygame.time.Clock()
        
    def reset(self):
        self.pos_x = 0
        self.pos_y = 0
        # Kung fu master observations
        self.enemy_pos = 0
        self.n_enemies=0
        self.my_pos = 0
        self.danger_pos=0
        self.danger_type=0
        self.enemy_type=0 # 0, 1, 2, 3, 80, 81, 82, 40
        self.blocked=0
        self.prev_blocked=0
        self.hold_hit=0
        self.time_left1=0
        self.time_left2=0
        self.my_energy=39
        self.previous_my_energy=39
        self.lifes=3
        self.previous_lifes=3
        self.got_hit=0
        self.got_blocked=0
        self.got_unblocked=0
        self.still_blocked=False
        self.starting_pos = 0
        self.level=1
        
        

        self.score = 0
        self.cumreward = 0
        self.cumscore = 0
        self.action_reward=0
        
        self.current_reward = 0 # accumulate reward over all events happened during this action until next different state

        self.prev_state = None # previous state
        self.firstAction = True # first action of the episode
        self.finished = False # episode finished
        self.newstate = True # new state reached
        self.numactions = 0 # number of actions in this episode
        self.iteration += 1

        self.agent.optimal = self.optimalPolicyUser or (self.iteration%100)==0 # False #(random.random() < 0.5)  # choose greedy action selection for the entire episode

    def pair_function(self):
        # Combine the number of enemies, player blocked and danger type information into 7 different states 
        if self.n_enemies > 0:
            self.danger_type=0
       # print (str(self.n_enemies) + " - " + str(self.danger_type) + ' - ' + str(self.blocked))
        pair = (int)((0.5*(self.n_enemies+self.danger_type)*(self.n_enemies+self.danger_type+1)+self.danger_type+1)*(1-(self.blocked/128)))
        if pair > 8:
            return 5 #game not started yet
        else:
            return pair

    def enemy_type_s(self):
        if self.enemy_type>127:
            return (self.enemy_type - 128 + 4)
        elif self.enemy_type == 64:
            return 8
        else:
            return self.enemy_type
        

        
    def getstate(self):

#        print ('enemy type: ' + str(self.enemy_type_s()) + 'level: ' + str(self.level -1) )
        x = (int)((self.level-1)*1000000 + self.pair_function()*100000 + (self.enemy_type_s()*10000) +  np.rint(self.my_pos/32)*1000 +  np.rint(self.enemy_pos/32)*100 + np.rint(self.danger_pos/32)*10 + np.rint(self.hold_hit/16))  
#3FINAL        x = (int)((self.enemy_type_s()*1000) + (self.level-1)*100000 + self.pair_function()*10000 + np.rint(self.enemy_pos/32)*100 + np.rint(self.danger_pos/32)*10 + np.rint(self.hold_hit/16))   

#2NO LEVEL        x = (int)((self.enemy_type_s()*1000) + self.pair_function()*10000 + np.rint(self.enemy_pos/32)*100 + np.rint(self.danger_pos/32)*10 + np.rint(self.hold_hit/16))   
#1NO ENEMY TYPE        x = (int)((self.level-1)*10000 + self.pair_function()*1000 + np.rint(self.enemy_pos/32)*100 + np.rint(self.danger_pos/32)*10 + np.rint(self.hold_hit/16))   


        return x


    def goal_reached(self):
        
        #return (self.my_energy>0 and self.time_left1==0 and self.time_left2<5) #and self.my_energy==39)
        return (self.level==5)
    
   
        
    def update(self, a):
        
        self.command = a
        # Update RAM
        self.ale.getRAM(self.ram)
        
        # Get info from RAM
        self.enemy_pos = self.ram[72]
        self.n_enemies = self.ram[91]
        self.danger_pos = self.ram[73]
        self.my_pos = self.ram[74]
        self.hold_hit = self.ram[77]
        
        self.enemy_type=self.ram[54]
        
        if self.level<self.ram[31]:
            self.starting_pos = self.ram[74]
        self.level=self.ram[31]
        self.max_level = max(self.level, self.max_level)
        
        
        # Danger/Enemy position:
        # 49 = no danger
        # 50 = danger approaching from left
        # 208 = danger approaching from right
         
        # ram[96] = 6, danger comes from top
        # ram[96] = 29, danger comes from bottom
        # ram[96] = 188, none
        if self.ram[96] == 6:
            self.danger_type = 0
        elif self.ram[96] == 29:
            self.danger_type = 1
        else:
            self.danger_type = 2

        self.time_left1= self.ram[27]
        self.time_left2= self.ram[28]

        self.previous_my_energy=self.my_energy
        self.my_energy= self.ram[75]

        if self.my_energy< self.previous_my_energy and not self.still_blocked and self.ram[34]==0: 
            self.got_hit=STATES['GotHit']
        else:
            self.got_hit=0

        self.previous_lifes = self.lifes
        self.lifes = self.ram[29]
        self.prev_blocked = self.blocked
        self.blocked = self.ram[61]
        if self.blocked > self.prev_blocked and not self.still_blocked:
            self.got_blocked = STATES['GotBlocked']
            self.still_blocked = True
            self.got_unblocked=0
        elif self.blocked < self.prev_blocked and self.still_blocked:
            self.got_unblocked = STATES['GotUnblocked']
            self.still_blocked=False
            self.got_blocked=0
        else:
            self.got_blocked=0
            self.got_unblocked=0
            
        

#        print ('enemy_pos=' +str(self.enemy_pos) + ' - danger_pos=' + str(self.danger_pos) + ' - my_position=' 
#               + str(self.my_pos) + ' - my_energy=' + str(self.my_energy) + ' - blocked=' + str(self.blocked) + ' - danger_type=' + str(self.danger_type))


        self.prev_state = self.getstate() # remember previous state
        
        # print " == Update start ",self.prev_state," action",self.command 
        
        self.current_reward = 0 # accumulate reward over all events happened during this action until next different state
        #print('self.current_reward = 0')
        self.numactions += 1 # total number of actions axecuted in this episode
        
        # while (self.prev_state == self.getstate()):
 
            
        if (self.firstAction):
            self.starting_pos = self.ram[74]
            self.firstAction = False
            self.current_reward = self.ale.act(a)
        else:
            self.current_reward = self.ale.act(a)

        if self.ram[34]==0:  #only when playing 
            if (a == 3 and self.starting_pos < self.my_pos) or (a == 4 and self.starting_pos > self.my_pos):
                self.action_reward = STATES['MoveFW']
            elif (a == 3 and self.starting_pos > self.my_pos) or (a == 4 and self.starting_pos < self.my_pos):
                self.action_reward = STATES['MoveBW']
            else:
                	self.action_reward = STATES['NotMoving']
        
        self.score+= self.current_reward
        self.current_reward += self.action_reward
        
#        print('score= ' + str(self.score) + ' current reward=' +str(np.rint(self.current_reward))+ ' - energy=' + str(self.my_energy/39.0) +
#        ' - got_hot='+ str(self.got_hit) + ' - got_blocked='  + str(self.got_blocked) + ' - got_unblocked=' + str(self.got_unblocked))
        # check if episode terminated
        
        #self.draw_screen
        
        if self.goal_reached():
            self.current_reward += STATES['Alive']
            self.ngoalreached += 1
            #self.ale.reset_game()
            self.finished = True

        if (self.ale.game_over()):
            self.current_reward += STATES['Dead']
            if self.level>1:
                print('game over in level ' + str(self.level))
            if self.my_energy >0 and self.lifes==3:
                print('Game over alive????')
            self.ale.reset_game()

            self.finished = True
        if self.level>2:
            if self.gui_visible == False:
                self.gui_visible = True
                self.initScreen()   
        #print " ** Update end ",self.getstate(), " prev ",self.prev_state
        


    def input(self):
        self.isPressed = False
        if self.gui_visible:

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:
                        self.pause = not self.pause
                        print "Game paused: ",self.pause
                    elif event.key == pygame.K_a:
                        self.isAuto = not self.isAuto
                        self.sleeptime = int(self.isAuto)*0.07
                    elif event.key == pygame.K_s:
                        self.sleeptime = 1.0
                        self.agent.debug = False
                    elif event.key == pygame.K_d:
                        self.sleeptime = 0.07
                        self.agent.debug = False
                    elif event.key == pygame.K_f:
                        self.sleeptime = 0.005
                        self.agent.debug = False
                    elif event.key == pygame.K_g:
                        self.sleeptime = 0.0
                        self.agent.debug = False
                    elif event.key == pygame.K_o:
                        self.optimalPolicyUser = not self.optimalPolicyUser
                        print "Best policy: ",self.optimalPolicyUser
                    elif event.key == pygame.K_q:
                        self.userquit = True
                        print "User quit !!!"
                    else:

                        pressed = pygame.key.get_pressed()


                        self.keys=0
                        self.keys |= pressed[pygame.K_UP]
                        self.keys |= pressed[pygame.K_DOWN]  <<1
                        self.keys |= pressed[pygame.K_LEFT]  <<2
                        self.keys |= pressed[pygame.K_RIGHT] <<3
                        self.keys |= pressed[pygame.K_z] <<4
                        self.command = key_action_tform_table[self.keys]
                        self.key_status[self.command] = True
                
                if event.type == pygame.KEYUP:
                    pressed = pygame.key.get_pressed()


                    self.keys=0
                    self.keys |= pressed[pygame.K_UP]
                    self.keys |= pressed[pygame.K_DOWN]  <<1
                    self.keys |= pressed[pygame.K_LEFT]  <<2
                    self.keys |= pressed[pygame.K_RIGHT] <<3
                    self.keys |= pressed[pygame.K_z] <<4
                    self.command = key_action_tform_table[self.keys]
                    self.key_status[self.command] = False
                    if not (True in self.key_status):
                        self.command =0
                       


        return True

    def getUserAction(self):
        return self.command

    def getreward(self):
        
        r = np.rint(self.current_reward) + self.got_hit + self.got_blocked + self.got_unblocked - np.rint(self.blocked/128)
        self.cumreward += r
 
        return r


    def print_report(self, printall=False):
        toprint = printall
        ch = ' '
        if (self.agent.optimal):
            ch = '*'
            toprint = True
      
        s = 'Iter %6d, sc: %3d, l: %d,  na: %4d, r: %5d %c' %(self.iteration, self.score, self.level, self.numactions, self.cumreward, ch)

        if self.score > self.hiscore:
            self.hiscore = self.score
            s += ' HISCORE '
            toprint = True
        if self.cumreward > self.hireward:
            self.hireward = self.cumreward
            s += ' HIREWARD '
            toprint = True

        if (toprint):
            print(s)

        self.cumreward100 += self.cumreward
        self.cumscore100 += self.score
        numiter = 100
        if (self.iteration%numiter==0):
            #self.doSave()
            pgoal = float(self.ngoalreached*100)/numiter
            print('----------------------------------------------------------------------------------------------------------------------')
            print("%s %6d avg last 100: reward %d | score %.2f | level %d | p goals %.1f %%" %(self.trainsessionname, self.iteration,self.cumreward100/100, float(self.cumscore100)/100, self.max_level, pgoal))
            print('----------------------------------------------------------------------------------------------------------------------')
            self.cumreward100 = 0  
            self.cumscore100 = 0 
            self.ngoalreached = 0

        sys.stdout.flush()
        
        self.resfile.write("%d,%d,%d,%d\n" % (self.score, self.cumreward, self.goal_reached(),self.numactions))
        self.resfile.flush()


    def draw(self):
        if self.gui_visible:
            
            self.screen.fill((0,0,0))
            
            self.ale.getScreenRGB(self.numpy_surface)        
      
            pygame.surfarray.blit_array(self.game_surface, np.transpose(self.numpy_surface,(1,0,2)))
    #        pygame.pixelcopy.array_to_surface(self.game_surface, np.transpose(self.numpy_surface,(1,0,2)))
            self.screen.blit(pygame.transform.scale2x(pygame.transform.scale(self.game_surface,(self.screen_height,self.screen_height))),(0,0))
    
    
        
            #Display ram bytes
            font = pygame.font.SysFont("Ubuntu Mono",32)
            text = font.render("RAM: " ,1,(255,208,208))
            self.screen.blit(text,(430,10))
        
            font = pygame.font.SysFont("Ubuntu Mono",25)
            height = font.get_height()*1.2
        
            line_pos = 40
            ram_pos = 0
            while(ram_pos < 128):
                ram_string = ''.join(["%02X "%self.ram[x] for x in range(ram_pos,min(ram_pos+16,128))])
                text = font.render(ram_string,1,(255,255,255))
                self.screen.blit(text,(440,line_pos))
                line_pos += height
                ram_pos +=16
                
            #display current action
            font = pygame.font.SysFont("Ubuntu Mono",32)
            text = font.render("Current Action: " + str(self.command) ,1,(208,208,255))
            height = font.get_height()*1.2
            self.screen.blit(text,(430,line_pos))
            line_pos += height
        
            #display reward
            font = pygame.font.SysFont("Ubuntu Mono",30)
            text = font.render("Total Reward: " + str(self.cumreward) ,1,(208,255,255))
            self.screen.blit(text,(430,line_pos))
        
            pygame.display.flip()
#            clock.tick(60.)
        else:
            return 0

    def quit(self):
        self.resfile.close()
        pygame.quit()

