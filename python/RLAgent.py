from py4j.java_gateway import get_field
from State
import numpy as np
import random

class ActionValue:

    def __init__(self,action_index,action_weight,value):
        self.action_index = action_index
        self.action_weight = action_weight
        self.value - value

    def GetActionIndex(self):
        return self.action_index

    def SetActionIndex(self,action_index):
        self.action_index = action_index

    def GetActionWeight(self):
        return self.action_weight

    def SetActionWeight(self,action_weight):
        self.action_weight  = action_weight



class RLAgent(object):
    def __init__(self, gateway,state,epsilon,discount_factor,alpha,lamb,feat_len,player_num,use_exp_replay,debug):
        self.state = state
        self.simulator = self.state.game_data
        self.epsilon = epsilon
        self.alpha = alpha
        self.lamb = lamb
        self.debug = debug
        self.trace = [0.0] * feat_len
        self.use_exp_replay = use_exp_replay
        self.player_num = player_num

    def FillTrace(self,feat):
        for i in range(feat):
            if (feat[i] > 0):
                trace[i] += 1

    def DecayTraces(self,feat):
        if self.lamb > 0:
            for i in range(feat):
                if (feat[i] > 0):
                    trace[i] = trace[i] * self.discount_factor * self.lamb
                else if feat[i] == 0:
                    trace[i] = 0
            return trace
        else:
            return feat

    def SetMultipleWeights(weights):
        self.actions_weights = weights

    def GetActionFromPolicy(reward):

        my_actions = []
        my_orginial_hp = self.state.my_char.getHp()
        my_op_orginial_hp = self.state.op_char.getHp()

        prob = random.random()

        if prob <= self.epsilon:

            random_action_index = random.randint(0,(self.state.my_actions))
            my_actions = []

            random_action = self.state.my_actions[random_action_index]

            my_actions.add(random_action)


            q_val = self.GetDotProduct(random_action,reward,my_actions)

            action =  ActionValue(random_action_index,self.state.my_actions_index[random_action_index],q_val)

            return action
        
        max_q_val = - float("inf")
        chosen_action = 0
        chosen_action_index = 0
        for i in range(self.state.my_actions_index):
            my_actions = []
            my_actions.append(self.state.my_actions[i])
            q_val = self.GetDotProduct(self.state.my_actions_index,reward,my_actions)
            if q_val > max_q_val:
                chosen_action = self.my_actions_index[i]
                chosen_action_index = i
                max_q_val = q_val

        return ActionValue(chosen_action_index,chosen_action,max_q_val)

            

        

