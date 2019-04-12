from py4j.java_gateway import get_field
from State import State
import numpy as np
import random

class ActionValue:

    def __init__(self,action_index,action_weight,value):
        self.action_index = action_index
        self.action_weight = action_weight
        self.value = value

    def GetActionIndex(self):
        return self.action_index

    def SetActionIndex(self,action_index):
        self.action_index = action_index

    def GetActionWeight(self):
        return self.action_weight

    def SetActionWeight(self,action_weight):
        self.action_weight  = action_weight



class RL(object):

    max_batch_size = 10000
    batch_update_size = 32


    def __init__(self, gateway,state,epsilon,discount_factor,alpha,lamb,feat_len,player_num,use_exp_replay):
        self.state = state
        self.simulator = self.state.game_data
        self.epsilon = epsilon
        self.alpha = alpha
        self.lamb = lamb
        self.trace = [0.0] * feat_len
        self.use_exp_replay = use_exp_replay
        self.player_num = player_num
        self.last_value = 0
        self.storage = []

    def FillTrace(self,feat):
        for i in range(feat):
            if (feat[i] > 0):
                trace[i] += 1

    def DecayTraces(self,feat):
        if self.lamb > 0:
            for i in range(feat):
                if (feat[i] > 0):
                    trace[i] = trace[i] * self.discount_factor * self.lamb
                elif feat[i] == 0:
                    trace[i] = 0
            return trace
        else:
            return feat

    def SetMultipleWeights(self,weights):
        self.actions_weights = weights

    def GetActionFromPolicy(self,reward):

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

    def Update(self,frame_data,reward,action_index):

        weight = self.actions_weights[action_index]
        features = self.state.GetFeatures(frame_data,reward)

        self.FillTrace(features)

        self.state.features = features

        next_action = self.GetActionFromPolicy(reward)

        active_features  = 0
        for i in range(len(features)):
            if features[i] == 1:
                active_features += 1

        new_alpha = 0
        if active_features == 0:
            new_alpha = self.alpha
        else:
            new_alpha = self.alpha / self.active_features
        
        td_target = reward + self.discount_factor * next_action.value
        delta = td_target = td_target - self.last_value
        factor_1  = new_alpha * delta

        self.UpdateWeights(weight,factor_1,self.state.last_features)

        if self.use_exp_replay:
            if len(self.storage) >= self.max_batch_size:
                self.BatchUpdates(batch_update_size)

            self.storage.add(Transition(self.state.last_features,factor_1,action_index))

        self.last_value = next_action.value
        self.state.last_features =  self.state.features

        return next_action


    def BatchUpdate(self,size):
        
    #storage size = self.max_batch_size
        int_set = set()

        while len(int_size) < size:
            random_int  = random.randint(0,(self.max_batch_size)) 
            int_set.add(rd)

        for el in int_set:
            transition = self.storage[el]
            weight = self.action_weights[transition.action]
            self.UpdateWeights(weight,transition.target,transition.features)

        
    def UpdateWeights(self,weights,factor,features):
        
        for i in range(len(weights)):
            weights[i] = weights[i] + features[i] * factor

    def GetDotProduct(self,q_action_index,reward,my_actions):

        weight = self.actions_weights[q_action_index]
        
        total = 0
        for i in range(len(weights)):
            total += weight[i] + self.state.features[i]

        return total
        
    def GetScore(self,frame_data,my_original_hp,op_original_hp):
        
        diff_my_hp = 0
        diff_op_hp = 0

        diff_my_hop = abs(frame_data.getCharacter(self.state.player_num).getHp() - my_original_hp)
        diff_op_hop = abs(frame_data.getCharacter(not self.state.player_num).getHp() - op_original_hp)

        if diff_my_hp == diff_op_hp and diff_my_hp != 0:
            return -1

        else:
            return diff_op_hp - diff_my_hp


            

            

            

        

