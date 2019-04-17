from py4j.java_gateway import get_field
import collections
import time
import random
import math

class TreeNode(object):

    UCT_TIME = 0.01
    UCB_C = 3.0
    UCT_TREE_DEPTH = 2
    UCT_CREATE_NODE_THRESHOULD = 10
    SIMULATION_TIME = 60
    DEBUG_MODE = True

    def __init__(self,gateway,frame_data,parent,my_actions,op_actions,game_data,player_num,cc,selected_my_actions= None):

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
        self.games = 0
        self.ucb = 0.0
        self.score = 0.0
        self.is_create_node = False

        # print("where do I fail?")
        if selected_my_actions == None:
            selected_my_actions = []

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
        # print("time to figure out what time is!")
        # print(time.time())
        # print("okay")
        start = time.time()

        while(time.time() - start <= self.UCT_TIME):
            # print("calling UCT")
            # print(time.time() - start <= self.UCT_TIME)
            # print(time.time() - start)
            # print(self.UCT_TIME)

            self.UCT()
            # print("UCT IS GOOD SO WHT IS THE PROBLEM MAAAAAN")

        return self.GetBestVisitAction()

    def Playout(self):


        # print("Playout being called ")

        # print("clearing my acitons")
        self.m_action.clear()
        # print("clearing op acitons")
        self.op_action.clear()

        # print("checking selected_my_actions")
        # print("selected my actions: ",self.selected_my_actions)
        for i in range(len(self.selected_my_actions)):
            self.m_action.add(self.selected_my_actions[i])

        # print("I mean the first for loop passed")
        # print("let's check shall we: ", len(self.selected_my_actions))
        for i in range(10-len(self.selected_my_actions)):
            # print("the second for loop passed")
            index = random.randint(0,len(self.my_actions)-1)
            # print("Our index: ",index)
            # print("Our #my actions: ",len(self.my_actions))
            # print(self.my_actions[0])
            # print(self.m_action)
            self.m_action.add(self.my_actions[index])
            # print("m actions: ",self.m_action)

        # print("a fallen world they say")
        for i in range(10):
            # print("the third for loop passed")
            index = random.randint(0,len(self.op_actions)-1)
            # print("Our index: ",index)
            # print("Our #my actions: ",len(self.op_actions))
            self.op_action.add(self.op_actions[index])
            # print("op actions: ",self.op_action)

        # print("calling new frame data")
        # print(self.frame_data)
        # print(self.player_num)
        # print(self.m_action)
        # print(self.op_action)
        # print(self.SIMULATION_TIME)
        # print(self.simulator)
        # print(self.frame_data, self.player_num, None, None, 17)
        # print("why stuff")
        
        # new_frame_data = self.simulator.simulate(self.frame_data,self.player_num,self.m_action,self.op_action,self.SIMULATION_TIME)
        new_frame_data = self.simulator.simulate(self.frame_data,self.player_num,self.m_action,self.op_action,self.SIMULATION_TIME)

        print("new frame data succefull!")

        return self.GetScore(new_frame_data)

    def UCT(self):
        # print("UCT being called: ")
        selected_node = None
        bestUcb = -999999.0
        # print("do we have children ")
        if self.children:
            # print("we have children")
            for child in self.children:
                # print("we have children")
                if child.games == 0:
                    # print("child has no games")
                    # print("hello: ",random.randint(0,2))
                    child.ucb = 9999.0 + random.randint(0,50)
                    # print("setting child ucb: ")
                else:
                    # print("get ucb failed")
                    child.ucb = self.GetUCB(child.score / child.games, self.games, child.games)
                    # print("child ucb works?")

                if bestUcb < child.ucb:
                    selected_node = child
                    bestUcb = child.ucb
        else:
            # print("we do not have children")
            selected_node = self

        score = 0.0
        # print("checking if selected node: ")
        if selected_node.games == 0:
            # print("rollout")
            score = selected_node.Playout()
        else:
            # print("the if statement failed")
            if not selected_node.children:
                # print("selected node does not have any children")
                if selected_node.depth < self.UCT_TREE_DEPTH:
                    # print("depth is less than the preset value")
                    if self.UCT_CREATE_NODE_THRESHOULD <= selected_node.games:
                        # print("the thresholdis less than the number of games")
                        # print("calling create node")
                        selected_node.CreateNode()
                        selected_node.is_create_node = True
                        score = selected_node.UCT()
                    else:
                        # print("doing a playout")
                        score = selected_node.Playout()
                else:
                    # print("doing a playout 2")
                    score = selected_node.Playout()
            else:
                if selected_node.depth < self.UCT_TREE_DEPTH:
                    score = selected_node.UCT()
                else:
                    score = selected_node.Playout()

        # print("we passed all the ifs yay!")
        selected_node.games += 1
        # print("added the current score to the node's score")
        selected_node.score += score
        # print("and it worked? checking depth")

        if self.depth == 0:
            # print("depth")
            self.games += 1
        # print("depth is fine and so is games")

        return score
    
    def CreateNode(self):
        # print("Create Node is being called")

        for i in range(len(self.my_actions)):
            # print("is something wrong")

            my_selected_actions = []
            
            # print(self.selected_my_actions)

            for action in self.selected_my_actions:

                # print("action, let's see if this works :",action)
                my_selected_actions.append(action)

            # print("adding the action")
            my_selected_actions.append(self.my_actions[i])


            child_node = TreeNode(self.gateway,self.frame_data,self,self.my_actions,self.op_actions,self.game_data,self.player_num,self.cc,my_selected_actions)
            self.children.append(child_node)

    def GetBestVisitAction(self):

        # print("GetBestVisitAction is called")
        
        selected = 0
        best_games = -9999.0

        # print("starting for loop")
        # print("self.children: ",self.children)

        for i in range(len(self.children)):
            # print("for loop starting")
            if self.DEBUG_MODE:
                # print("we are in debug mode so we are printing")
                # print("score: ",self.children[i].score )
                # print("games: ",self.children[i].games )
                # print("ucb: ",self.children[i].ucb )
                # print("actions: ",self.my_actions[i])
                if self.children[i].games !=0:
                    print("Score is : ", (self.children[i].score / self.children[i].games), ", Number of trials: " , self.children[i].games , ", UCB: ", self.children[i].ucb, ", Action: ",self.my_actions[i]) 
                else:
                    print("Score is : ", 0, ", Number of trials: " , self.children[i].games , ", UCB: ", self.children[i].ucb, ", Action: ",self.my_actions[i]) 


            if best_games < self.children[i].games:
                best_games = self.children[i].games
                selected = i
        
        # print("self action: ",self.my_actions)
        # print("selected: ", selected)
        
        # if self.DEBUG_MODE:
        #     print("Selected my_actions: ",self.my_actions[selected], ", Total number of trials: ",self.games)
        #     print()

        # print(self.my_actions)
        # print(selected)
        
        return self.my_actions[selected]

    def GetBestScoreAction(self):

        selected = 0
        best_score = -9999.0

        for i in range(len(self.children)):

            if self.children[i].games !=0:
                print("Score is : ", (self.children[i].score / self.children[i].games), ", Number of trials: " , self.children[i].games , ", UCB: ", self.children[i].ucb, ", Action: ",self.my_actions[i]) 
            else:
                print("Score is : ", 0, ", Number of trials: " , self.children[i].games , ", UCB: ", self.children[i].ucb, ", Action: ",self.my_actions[i]) 


            mean_score = self.children[i].score / self.children[i].games 
            if best_score < mean_score:
                best_score = mean_score
                selected = i

        print("Selected my_actions: ",self.my_actions[selected], ", Total number of trials: ",self.games)
        print()

        return self.my_actions[selected]

    def GetScore(self,frame_data):
        #basic evaluation score
        # print("basic eval is being called")
        my_char = self.frame_data.getCharacter(self.player_num)
        op_char = self.frame_data.getCharacter(not self.player_num)

        # print("we got this far")

        score =(my_char.getHp() - self.my_original_hp ) - (op_char.getHp() - self.op_original_hp)  

        # print("score is good!")

        return score

    def GetUCB(self,score,n,n_i):
        # print("GET UCB BEING CALLED")
        # print("score: ",self.score)
        # print("usb_c: ",self.UCB_C)
        # print("log stuff",math.log(n))
        # print("n_i: ",n_i)
        #
        return self.score  + self.UCB_C + math.sqrt( (2.0 * math.log(n) )/ n_i )

    def __str__(self):
        string = ""
        string += "Total number of trails: "+ str(self.games) + '\n'

        # print("going through the children")

        for i in range(len(self.children)):
            if self.children[i].games != 0:
                string += "Child "+  str(i)+" : Trials: " +  str(self.children[i].games) + " ,Depth: " + str(self.children[i].depth) + " ,score: " +  str(self.children[i].score/ self.children[i].games) + " UCB: " + str(self.children[i].ucb) + '\n'
            else:
                string += "Child "+  str(i)+" : Trials: " +  str(self.children[i].games) + " ,Depth: " + str(self.children[i].depth) + " ,score: " +  "0" + " UCB: " + str(self.children[i].ucb) + '\n'


        # print("going through the children worked")


        string += '\n'



        if self.children:
            for child in self.children:
                if(child.is_create_node):
                    string += str(child)

        # print("root node printing works!!!!!")

        return string



if __name__ == "__main__":
    print( 5>2 and 5 or 2)
