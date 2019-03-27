from py4j.java_gateway import get_field
import collections
import time
import random
import math

class TreeNode(object):

    UCT_TIME = 165 * 100000
    UCB_C = 3.0
    UCT_TREE_DEPTH = 2
    UCT_CREATE_NODE_THRESHOULD = 10
    SIMULATION_TIME = 60
    DEBUG_MODE = True

    def __init__(self,gateway,frame_data,parent,my_actions,op_actions,game_data,player_num,cc,selected_my_actions=None):

        self.frame_data = frame_data
        self.parent = parent
        self.my_actions = my_actions
        self.op_actions = op_actions
        self.game_data = game_data
        self.simulator = self.game_data.getSimulator()
        self.player_num = player_num
        self.gateway = gateway
        self.cc = cc

        self.children = []
        self.depth = 0
        self.games = -1
        self.ucb = 0.0
        self.score = 0.0
        self.selected_my_actions = self.gateway.jvm.java.util.ArrayDeque()

        self.selected_my_actions = selected_my_actions
        self.m_action = self.gateway.jvm.java.util.ArrayDeque()
        self.op_action = self.gateway.jvm.java.util.ArrayDeque()


        my_char = self.frame_data.getCharacter(self.player_num)
        op_char = self.frame_data.getCharacter(not self.player_num)

        self.my_original_hp = my_char.getHp()
        self.op_original_hp = op_char.getHp()

        if (self.parent != None):
            self.depth = self.parent.depth +1

    def MCTS(self):
        print("time to figure out what time is!")
        print(time.time())
        print("okay")
        start = time.time()

        while(time.time() - start <= self.UCT_TIME):
            print("calling UCT")
            self.UCT()

        return self.getBestVisitAcion()

    def Playout(self):


        print("Playout being called ")

        print("clearing my acitons")
        self.m_action.clear()
        print("clearing op acitons")
        self.op_action.clear()

        print("checking selected_my_actions")
        print("selected my actions: ",self.selected_my_actions)
        for action in self.selected_my_actions:
            self.m_action.append(action)

        print("I mean the first for loop passed")
        print("let's check shall we: ", len(self.selected_my_actions))
        for i in range(5-len(self.selected_my_actions)):
            print("the second for loop passed")
            index = random.randint(0,len(self.my_actions)-1)
            print("Our index: ",index)
            print("Our #my actions: ",len(self.my_actions))
            self.m_action.append(self.my_actions[index])
            print("m actions: ",self.m_action)

        print("a fallen world they say")
        for i in range(5):
            print("the third for loop passed")
            index = random.randint(0,len(self.op_actions)-1)
            print("Our index: ",index)
            print("Our #my actions: ",len(self.op_actions))
            self.op_action.append(self.op_actions[index])
            print("op actions: ",self.op_action)

        print("calling new frame data")
        print(self.frame_data)
        print(self.player_num)
        print(self.m_action)
        print(self.op_action)
        print(self.SIMULATION_TIME)
        print(self.simulator)
        print(self.frame_data, self.player_num, None, None, 17)
        print("why stuff")
        
        # new_frame_data = self.simulator.simulate(self.frame_data,self.player_num,self.m_action,self.op_action,self.SIMULATION_TIME)
        new_frame_data = self.simulator.simulate(self.frame_data,self.player_num,self.m_action,self.op_action,self.SIMULATION_TIME)

        print("new frame data succefull!")

        return self.GetScore(new_frame_data)

    def UCT(self):
        print("UCT being called: ")
        selected_node = None
        bestUcb = -999999.0
        print("for loop: ")
        if self.children:
            for child in self.children:
                print("we failed")
                if child.games == 0:
                    print("child has no games")
                    child.ucb = 9999.0 + random.randint(50)
                else:
                    print("get ucb failed")
                    child.ucb = self.GetUcb(child.score / child.games, games, child.games)

                if bestUcb < child.ucb:
                    selected_node = child
                    bestUcb = child.ucb
        else:
            selected_node = self

        score = 0.0
        print("checking if selected node: ")
        if selected_node.games == 0:
            print("rollout")
            score = selected_node.Playout()
        else:
            print("the if statement failed")
            if not selected_node.children:
                print("selected node does not have any children")
                if selected_node.depth <self.UCT_TREE_DEPTH:
                    print("depth is less than the preset value")
                    if self.UCT_CREATE_NODE_THRESHOULD <= selected_node.games:
                        print("the thresholdis less than the number of games")
                        print("calling create node")
                        selected_node.CreateNode()
                        selected_node.isCreateNode = True
                        score = selected_node.UCT()
                    else:
                        print("doing a playout")
                        score = selected_node.Playout()
                else:
                    print("doing a playout 2")
                    score = selected_node.Playout()
            else:
                if selected_node.depth < self.UCT_TREE_DEPTH:
                    score = selected_node.UCT()
                else:
                    score = selected_node.Playout()

        selected_node.games += 1
        selected_node.score += score

        if self.depth == 0:
            self.games += 1

        return score
    
    def CreateNode(self):

        for i in range(len(self.my_actions)):

            my = collections.deque()

            for action in self.selected_my_actions:
                my.append(action)

            my.append(self.my_actions[i])

            self.children.append(TreeNode(self.gateway,self.frame_data,self.my_actions,self.op_actions,self.game_data,self.player_num,self.cc,my))

    def GetBestVisitAction(self):
        
        selected = -1
        best_games = -9999.0

        for i in range(len(self.children)):
            if DEBUG_MODE:
                print("Score is : ", self.children[i].score / self.children[i].games, ", Number of trials: " ,self.children[i].games, ", UCB: ", self.children[i].ucb, ", Action: ",self.my_actions[i]) 

            if best_games < self.children[i].games:
                best_games = self.children[i].games
                selected = i
        
        if DEBUG_MODE:
            print("Selected my_actions: ",self.my_actions[selected], ", Total number of trials: ",self.games)
            print()
        
        return self.my_actions[selected]

    def GetBestScoreAction(self):

        selected = -1
        best_score = -9999.0

        for i in range(len(self.children)):

            print("Score is : ", self.children[i].score / self.children[i].games, ", Number of trials: " ,self.children[i].games, ", UCB: ", self.children[i].ucb, ", Action: ",self.my_actions[i]) 

            mean_score = self.children[i].score / self.children[i].games 
            if best_score < mean_score:
                best_score = mean_score
                selected = i

        print("Selected my_actions: ",self.my_actions[selected], ", Total number of trials: ",self.games)
        print()

        return self.my_actions[selected]

    def GetScore(self,frame_data):
        #basic evaluation score
        my_char = self.frame_data.getCharacter(self.player_num)
        op_char = self.frame_data.getCharacter(not self.player_num)

        return (my_char.getHP() - self.my_original_hp ) - (op_char.getHP() - self.op_original_hp) 

    def GetUCB(self,score,n,ni):
        return self.score  + self.UCB_C + math.sqrt( (2.0 * math.log(n) )/ ni )

    def __str__(self):
        print("Total number of trails: ", self.games)

        for i in range(len(self.children)):
            print("Child ",i," : Trials: ", self.children[i].games, " ,Depth: ", self.children[i].depth," ,score: ", self.children[i].score/ self.children[i].games," UCB: ", self.children[i].ucb)

        print()

        for child in self.children:
            if(child.isCreateNode):
                print(child)






if __name__ == "__main__":
    print( 5>2 and 5 or 2)
