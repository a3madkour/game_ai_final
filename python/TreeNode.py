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

    def __init__(self,frame_data,parent,my_actions,op_actions,game_data,player_num,cc,selected_my_actions=None):

        print("Hi I am being called!")
        self.frame_data = frame_data
        self.parent = parent
        self.my_actions = my_actions
        self.op_actions = op_actions
        self.game_data = game_data
        self.player_num = player_num
        self.cc = cc

        self.children = []
        self.depth = 0
        self.games = -1
        self.ucb = 0.0
        self.score = 0.0

        self.selected_my_actions = selected_my_actions


        self.m_action = collections.deque()
        self.op_action = collections.deque()

        my_char = self.frame_data.getCharacter(self.player_num)
        op_char = self.frame_data.getCharacter(not self.player_num)

        self.my_original_hp = my_char.getHP()
        self.op_original_hp = op_char.getHP()

        if (self.parent != None):
            self.depth = self.parent.depth +1

    def MCTS(self):
        start = time.time()
        while(time.time() - start <= UCT_TIME):
            UCT()

        return getBestVisitAcion()

    def Playout(self):

        self.m_action.clear()
        self.op_action.clear()

        for action in self.selected_my_actions:
            self.m_action.append(action)

        for i in range(5-len(self.selected_my_actions)):
            index = random.randint(0,len(self.my_actions))
            self.m_action.append(self.my_actions[index])

        for i in range(5):
            index = random.randint(0,len(self.op_actions))
            self.op_action.append(self.op_actions[index])

        new_frame_data = self.simulator.simulate(self.frame_data,self.player_num,self.m_action,self.op_action,SIMULATION_TIME)

        return GetScore(new_frame_data)

    def UCT(self):
        selected_node = None
        bestUcb = -999999.0
        for child in self.children:
            if child.games == 0:
                child.ucb = 9999.0 + random.randint(50)
            else:
                child.ucb = self.GetUcb(child.score / child.games, games, child.games)

            if bestUcb < child.ucb:
                selected_node = child
                bestUcb = child.ucb

        score = 0.0
        if selected_node.games == 0:
            score = selected_node.playout()
        else:
            if not selected_node.children:
                if selected_node.depth < UCT_TREE_DEPTH:
                    if UCT_CREATE_NODE_THRESHOULD <= selected_node.games:
                        selected_node.CreateNode()
                        selected_node.isCreateNode = True
                        score = selected_node.UCT()
                    else:
                        score = selected_node.playout()
                else:
                    score = selected_node.playout()
            else:
                if selected_node.depth < UCT_TREE_DEPTH:
                    score = selected_node.UCT()
                else:
                    score = selected_node.playout()

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

            self.children.append(TreeNode(frameData,self,self.my_actions,self.op_actions,self.game_data,self.player_num,self.cc,my))

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
