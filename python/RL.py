from py4j.java_gateway import get_field
from State import State
import numpy as np
import random

class ActionValue:

    def __init__(self,action_index,action_weight,value):
        self.action_index = action_index
        self.action_weight = action_weight
        self.value = value
        # print("the init is done")

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


    def __init__(self, gateway,state,epsilon,gamma,alpha,lamb,feat_len,player_num,use_exp_replay):

        # print("Initialize Agent")
        self.state = state
        # print("setting up simulator")
        self.simulator = self.state.game_data.getSimulator()
        self.epsilon = epsilon
        self.alpha = alpha
        self.lamb = lamb
        self.gamma = gamma
        self.trace = [0.0] * feat_len
        self.use_exp_replay = use_exp_replay
        self.player_num = player_num
        self.last_value = 0
        self.storage = []

    def FillTrace(self,feat):
        # print("Fill trace being called")
        # print(len(feat))
        # print(len(self.trace))
        for i in range(len(feat)):
                self.trace[i] += 1

    def DecayTraces(self,feat):
        if self.lamb > 0:
            for i in range(feat):
                if (feat[i] > 0):
                    self.trace[i] = self.trace[i] * self.gamma * self.lamb
                elif feat[i] == 0:
                    self.trace[i] = 0
            return self.trace
        else:
            return feat

    def SetMultipleWeights(self,weights):
        self.actions_weights = weights

    def GetActionFromPolicy(self,reward):

        # print("Get Action From Policy is being called")
        my_actions = []
        my_orginial_hp = self.state.my_char.getHp()
        my_op_orginial_hp = self.state.op_char.getHp()



        prob = random.random()

        # print("setting up vars is done")
        # print(prob)
        # print(self.epsilon)

        if prob <= self.epsilon:

            # print("in if, i.e. we are exploring")


            random_action_index = random.randint(0,len(self.state.my_actions)-1)

            # print("random_action_index: ",random_action_index)
            my_actions = []

            # print("random_action: ",self.state.my_actions)
            random_action = self.state.my_actions[random_action_index]
            # print("random_action: ",random_action)

            my_actions.append(random_action)

            # print("my_actions: ",my_actions)


            # print("getting the dot product")
            q_val = self.GetDotProduct(random_action_index,reward,my_actions)

            # print("random_action_index: ",random_action_index)
            # print("self.state.my_actions_index[random_action_index]: ",self.state.my_actions_index[random_action_index])
            # print("q_val",q_val)
            action =  ActionValue(random_action_index, self.state.my_actions_index[random_action_index] ,q_val)

            return action
        
        max_q_val = - float("inf")
        # print("max q val:", max_q_val)
        chosen_action = 0
        chosen_action_index = 0
        # print("starting the for loop")
        # print(self.state.my_actions_index)
        # print(len(self.state.my_actions_index))
        for i in range(len(self.state.my_actions_index)):
            # print(self.state.my_actions)
            my_actions = []
            my_actions.append(self.state.my_actions[i])
            # print(self.state.my_actions_index[i])
            # print("Get dot product being called")
            q_val = self.GetDotProduct(self.state.my_actions_index[i],reward,my_actions)
            # print("if being called")
            # print(q_val,"the max", max_q_val)
            if q_val > max_q_val:
                # print("we are in the if")
                # print(i)
                # print(i)
                # print(self.state.my_actions_index[i])
                chosen_action = self.state.my_actions_index[i]
                chosen_action_index = i
                max_q_val = q_val

        # print("returning")
        # print(chosen_action)
        # print(chosen_action_index)
        # print(max_q_val)
        return ActionValue(chosen_action_index,chosen_action,max_q_val)

    def Update(self,frame_data,reward,action_index):


        # print("Update being called")

        weight = self.actions_weights[action_index]
        # print("calling get features being ")
        features = self.state.GetFeatures(frame_data,reward)
        # print("back from get features being ")


        # print("calling Fill Trace")

        self.FillTrace(features)

        # print("back from Fill Trace")

        self.state.features = features

        # print("calling get action from policy")
        next_action = self.GetActionFromPolicy(reward)

        # print("back from get action from policy")

        active_features  = 0
        # print(features)
        # print(len(features))
        for i in range(len(features)):
            if features[i] == 1:
                active_features += 1

        new_alpha = 0
        # print("new_alpha: ",new_alpha)
        if active_features == 0:
            new_alpha = self.alpha
        else:
            # print(self.alpha)
            # print(active_features)
            new_alpha = self.alpha / active_features
            # print(new_alpha)
        
        # print("calc stuff")
        # print(reward)
        # print(self.gamma)
        # print(next_action.value)
        td_target = reward + self.gamma * next_action.value
        # print("td_target: ",td_target)
        delta =  td_target - self.last_value
        factor_1  = new_alpha * delta

        # print("calling update weights")

        self.UpdateWeights(weight,factor_1,self.state.last_features)

        # print("back from update weights")

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

        # print("GET DOT PRODUCT called")
        # print(self.actions_weights)
        # print(q_action_index)
        weight = self.actions_weights[q_action_index]
        # print("weight: ",weight)
        
        total = 0
        # print(len(weight))
        # print(weight)
        # print(self.state.features)
        # print(len(self.state.features))
        # print("now going through the loop")
        for i in range(len(weight)):
            # print(i,": i")
            total += weight[i] + self.state.features[i]

        # print("loop: ",total)
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


            

            

            

        

