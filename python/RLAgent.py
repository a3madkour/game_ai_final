from py4j.java_gateway import get_field
import collections
from TreeNode import TreeNode
from State import State
from RL import RL, ActionValue
import math

class RLAgent(object):

    FRAME_AHEAD = 14
    DEBUG_MODE = True
    epsilon = 0.01
    gamma = 0.95
    alpha = 0.2
    lamb = 0.1
    action_weights_number = 6
    use_exp_replay = False


    def __init__(self, gateway):
        self.gateway = gateway
        self.my_actions = []
        self.op_actions = []
        self.ACTION = self.gateway.jvm.enumerate.Action


    def close(self):
        pass

    def getInformation(self, frame_data):
        # Load the frame data every time getInformation gets called
            self.state.frame_data = frame_data
            self.frame_data = frame_data
            self.cc.setFrameData(self.frame_data, self.player_num)
            self.state.my_char = self.frame_data.getCharacter(self.player_num)
            self.state.op_char = self.frame_data.getCharacter(not self.player_num)
            self.my_char = self.frame_data.getCharacter(self.player_num)
            self.op_char = self.frame_data.getCharacter(not self.player_num)

    # please define this method when you use FightingICE version 3.20 or later
    def roundEnd(self, x, y, z):
        print(x)
        print(y)
        print(z)

    # please define this method when you use FightingICE version 4.00 or later
    def getScreenData(self, sd):
        pass


    def initialize(self, game_data, player_num):
        # Initializng the command center, the simulator and some other things
            print("Initializing")
            self.input_key = self.gateway.jvm.struct.Key()
            self.frame_data = self.gateway.jvm.struct.FrameData()
            self.cc = self.gateway.jvm.aiinterface.CommandCenter()
            self.simulate_time = 60
            self.player_num = player_num
            self.game_data = game_data
            self.simulator = self.game_data.getSimulator()
            print("making the state")
            self.state  = State(self.gateway,game_data,self.cc,player_num)
            self.is_game_just_started = True
            print("making the action")
            self.current_action = ActionValue(0,0,0)
            print("action is okay!")
            self.weight_path_p1 = None
            self.weight_path_p2 = None
            self.in_behaviour = False

            
            self.my_last_hp = 0
            self.op_last_hp = 0
            
            print("creating the agent")

            print(self.gateway)
            print(self.state)
            print(self.epsilon)
            print(self.gamma)
            print(self.alpha)
            print(self.lamb)
            print("state stuff")
            print(self.state.features_num)
            print(self.state.player_num)
            print(self.use_exp_replay)


            self.agent = RL(self.gateway,self.state,self.epsilon,self.gamma,self.alpha,self.lamb,self.state.features_num,self.state.player_num,self.use_exp_replay)


            self.action_air = [ self.ACTION.AIR_GUARD , self.ACTION.AIR_A ,self.ACTION.AIR_B ,self.ACTION.AIR_DA, self.ACTION.AIR_DB ,self.ACTION.AIR_FA ,self.ACTION.AIR_FB ,self.ACTION.AIR_UA ,self.ACTION.AIR_UB ,self.ACTION.AIR_D_DF_FA ,self.ACTION.AIR_D_DF_FB ,self.ACTION.AIR_F_D_DFA ,self.ACTION.AIR_F_D_DFB ,self.ACTION.AIR_D_DB_BA , self.ACTION.AIR_D_DB_BB]

            self.action_ground = [ self.ACTION.STAND_D_DB_BA, self.ACTION.BACK_STEP,self.ACTION.FORWARD_WALK,self.ACTION.DASH,self.ACTION.JUMP,self.ACTION.FOR_JUMP,
                    self.ACTION.BACK_JUMP,self.ACTION.STAND_GUARD,self.ACTION.CROUCH_GUARD,self.ACTION.THROW_A,self.ACTION.THROW_B,self.ACTION.STAND_A,self.ACTION.STAND_B,
                    self.ACTION.CROUCH_A,self.ACTION.CROUCH_B,self.ACTION.STAND_FA,self.ACTION.STAND_FB,self.ACTION.CROUCH_FA,self.ACTION.CROUCH_FB,self.ACTION.STAND_D_DF_FA,
                    self.ACTION.STAND_D_DF_FB,self.ACTION.STAND_F_D_DFA,self.ACTION.STAND_F_D_DFB,self.ACTION.STAND_D_DB_BB]

            self.sp_skill = self.ACTION.STAND_D_DF_FC

            self.my_motion_data = self.game_data.getMotionData(self.player_num)
            self.op_motion_data = self.game_data.getMotionData(not self.player_num)
            self.my_actions = []
            self.op_actions = []

            self.agent.epsilon = self.epsilon
            
            multi_feat = []
            for i in range(self.action_weights_number):
                feat = [0.0] * self.state.features_num
                print(feat)
                multi_feat.append(feat)

            self.agent.SetMultipleWeights(multi_feat)



            return 0

    def input(self):
        # The input is set up to the global variable input_key
            # which is modified in the processing part
            return self.input_key

    def processing(self):
        # First we check whether we are at the end of the round
            # print("processing ")
            if self.frame_data.getEmptyFlag() or self.frame_data.getRemainingFramesNumber() <= 0:
                # print("in the first if")
                self.is_game_just_started = True
                return
            if not self.is_game_just_started:
                # print("in the second if")
                # Simulate the delay and look ahead 2 frames. The simulator class exists already in FightingICE
                self.frame_data = self.simulator.simulate(self.frame_data, self.player_num, None, None, self.FRAME_AHEAD)
            else:
                # If the game just started, no point on simulating
                    self.is_game_just_started = False
            print("we got passed the if statements ")
            self.cc.setFrameData(self.frame_data, self.player_num)
            print("state updating!")
            self.state.Update(self.cc,self.frame_data,self.player_num)
            print("state updates!")
            
            # distance = self.frame_data.getDistanceX()
            # energy = my.getEnergy()
            # my_x = my.getX()
            # my_state = my.getState()
            # opp_x = opp.getX()
            # opp_state = opp.getState()
            # xDifference = my_x - opp_x
            print("starting the second set of ifs")
            if self.cc.getSkillFlag():
                # If there is a previous "command" still in execution, then keep doing it
                    self.input_key = self.cc.getSkillKey()
                    return
            # We empty the keys and cancel skill just in case
            print("the if is done!")
            self.input_key.empty()
            self.cc.skillCancel()


            print("setting actions for the state")

            self.state.SetActions(self.frame_data,self.player_num)

            print("setting actions for the state done!")

            print("retrying reward")

            reward = abs(self.op_last_hp - self.state.op_char.getHp()) - abs(self.my_last_hp - self.state.my_char.getHp())


            print("it is the HP isn't it")
            self.my_last_hp = self.state.my_char.getHp()
            self.op_last_hp = self.state.op_char.getHp()


            print("nope maybe next_action?")
            next_action = self.agent.Update(self.frame_data,reward,self.current_action.action_weight)
            print("nope")

            self.current_action = next_action
            print("trying to get chosen_action")
            print(self.state.my_actions)
            print(self.current_action)
            print(self.current_action.action_index)
            chosen_action = self.state.my_actions[self.current_action.action_index]
            print("and success!")

            print("and now execting the action")
            self.ExecuteOption(chosen_action)



    def ExecuteOption(self,action):
        print(action)
        if type(action) is str:
            print("action is a string")
            action_name = action
        else:
            action_name = action.name()

        selected_action = self.ACTION.NEUTRAL
        print("starting the ifs")
        if "OPTION" in action_name:
            print("it is an option")
            if "CAUTIOUS" in action_name:
                print("I am cautious")
                self.action_air = [self.ACTION.AIR_GUARD]
                print("done with air")
                self.action_ground = [self.ACTION.DASH,self.ACTION.NEUTRAL,self.ACTION.STAND_A,self.ACTION.CROUCH_B,self.ACTION.THROW_A,self.ACTION.STAND_B,self.ACTION.CROUCH_A]
                print("done with ground")
                self.op_action_air = [self.ACTION.AIR_B, self.ACTION.AIR_DB,self.ACTION.AIR_FB]
                self.op_action_ground = [self.ACTION.STAND,self.ACTION.DASH,self.ACTION.STAND_A,self.ACTION.CROUCH_B,self.ACTION.STAND_B]
                self.simulate_time = 60
            elif "KICKER" in action_name: 
                print("I am kicker")
                self.action_air = [self.ACTION.AIR_GUARD]
                print("done with air")
                self.action_ground = [self.ACTION.STAND,self.ACTION.DASH,self.ACTION.FORWARD_WALK,self.ACTION.CROUCH_A,self.ACTION.CROUCH_B,self.ACTION.CROUCH_FB,self.ACTION.STAND_D_DB_BB]
                print("done with ground")
                self.op_action_air = [self.ACTION.AIR_B, self.ACTION.AIR_DB,self.ACTION.AIR_FB]
                print("done with option air")
                self.op_action_ground = [self.ACTION.STAND,self.ACTION.DASH,self.ACTION.CROUCH_FB]
                print("done with option ground")
                self.simulate_time = 60
            elif "ESCAPER" in action_name:
                print("I am escaper")
                self.action_air = [self.ACTION.AIR_GUARD]
                print("done with air")
                self.action_ground = [self.ACTION.BACK_STEP,self.ACTION.JUMP,self.ACTION.NEUTRAL,self.ACTION.BACK_JUMP,self.ACTION.FOR_JUMP]
                print("done with ground")
                self.op_action_air = [self.ACTION.AIR_B, self.ACTION.AIR_DB,self.ACTION.AIR_FB]
                print("done with option air")
                self.op_action_ground = [self.ACTION.STAND_A, self.ACTION.STAND_FA, self.ACTION.STAND_FB, self.ACTION.CROUCH_FB,self.ACTION.STAND_B]
            elif "ATTACKER" in action_name:
                print("I am attacker")
                self.action_air = [self.ACTION.AIR_GUARD]
                print("done with air")
                self.action_ground = [self.ACTION.NEUTRAL, self.ACTION.DASH,self.ACTION.AIR_FA,self.ACTION_THROW_A,self.ACTION.STAND_B,self.ACTION.STAND_A,self.ACTION.CROUCH_A]
                print("done with ground")
                self.op_action_air = [self.ACTION.AIR_B, self.ACTION.AIR_DB,self.ACTION.AIR_FB]
                self.op_action_ground = [self.ACTION.DASH, self.ACTION.STAND ]
                print("done with option ground")
                self.simulate_time = 60
            elif "GRABBER" in action_name:
                print("I am grabber")
                self.action_air = [self.ACTION.AIR]
                print("done with air")
                self.action_ground = [self.ACTION.FORWARD_WALK,self.ACTION.DASH,self.ACTION.STAND_A,self.ACTION.THROW_A]
                print("done with ground")
                self.op_action_air = [self.ACTION.AIR]
                print("done with option air")
                self.op_action_ground = [self.ACTION.STAND,self.ACTION.DASH,self.ACTION.STAND_A]
                print("done with option ground")
                self.simulate_time = 20

            elif "ANTIAIR" in action_name:
                print("I am antiair")

                self.action_air = [self.ACTION.AIR_GUARD]
                print("done with air")
                self.action_ground = [self.ACTION.FORWARD_WALK,self.ACTION.CROUCH_FA,self.ACTION.STAND_FB]
                print("done with ground")
                self.op_action_air = [self.ACTION.NEUTRAL]
                print("done with option air")
                self.op_action_ground = [self.ACTION.NEUTRAL]
                print("done with option ground")
                self.simulate_time = 20

            elif "STOMPER" in action_name:
                print("I am stomper")

                self.action_air = [self.ACTION.AIR_F_D_DFB,self.ACTION.AIR_D_DB_BA,self.ACTION.AIR_FB,self.ACTION.AIR_DB, self.ACTION.AIR_B]
                print("done with air")
                self.action_ground = [self.ACTION.NEUTRAL, self.ACTION.THROW_A]
                print("done with ground")
                self.op_action_air = [self.ACTION.AIR]
                print("done with option air")
                self.op_action_ground = [self.ACTION.NEUTRAL]
                print("done with option ground")
                self.simulate_time = 30

            elif "AIRDOMINATOR" in action_name:
                print("I am airdominator")

                self.action_air = [self.ACTION.AIR_A,self.ACTION.AIR_B,self.ACTION.AIR_FA,self.ACTION.AIR_FB]
                print("done with air")
                self.action_ground = [self.ACTION.NEUTRAL]
                print("done with ground")
                self.op_action_air = [self.ACTION.AIR]
                print("done with option air")
                self.op_action_ground = [self.ACTION.NEUTRAL]
                print("done with option ground")
                self.simulate_time = 30


                self.simulate_time = 60

            elif "MCTS" in action_name:
                print("I am MCTS")
                self.action_air = [ self.ACTION.AIR_GUARD , self.ACTION.AIR_A ,self.ACTION.AIR_B ,self.ACTION.AIR_DA, self.ACTION.AIR_DB ,self.ACTION.AIR_FA ,self.ACTION.AIR_FB ,self.ACTION.AIR_UA ,self.ACTION.AIR_UB ,self.ACTION.AIR_D_DF_FA ,self.ACTION.AIR_D_DF_FB ,self.ACTION.AIR_F_D_DFA ,self.ACTION.AIR_F_D_DFB ,self.ACTION.AIR_D_DB_BA , self.ACTION.AIR_D_DB_BB]
                print("done with air")

                self.action_ground = [ self.ACTION.STAND_D_DB_BA, self.ACTION.BACK_STEP,self.ACTION.FORWARD_WALK,self.ACTION.DASH,self.ACTION.JUMP,self.ACTION.FOR_JUMP,
                        self.ACTION.BACK_JUMP,self.ACTION.STAND_GUARD,self.ACTION.CROUCH_GUARD,self.ACTION.THROW_A,self.ACTION.THROW_B,self.ACTION.STAND_A,self.ACTION.STAND_B,
                        self.ACTION.CROUCH_A,self.ACTION.CROUCH_B,self.ACTION.STAND_FA,self.ACTION.STAND_FB,self.ACTION.CROUCH_FA,self.ACTION.CROUCH_FB,self.ACTION.STAND_D_DF_FA,
                        self.ACTION.STAND_D_DF_FB,self.ACTION.STAND_F_D_DFA,self.ACTION.STAND_F_D_DFB,self.ACTION.STAND_D_DB_BB]
                print("done with ground")
                
                self.op_action_air = self.action_air
                print("done with option air")
                self.op_action_ground = self.action_ground
                print("done with option ground")
                self.simulate_time = 60

            self.MCTSPrepare()

            root_node = TreeNode(self.gateway,self.simulator_ahead_frame_data,None,self.my_actions,self.op_actions,self.game_data,self.player_num,self.cc)

            best_action = root_node.MCTS()
            self.cc.commandCall(best_action.name())
        elif "EXP" in action_name:
            if (not self.ACTION.NEUTRAL in attack_name):
                self.cc.commandCall(attack_name)


            




                    







    def MCTSPrepare(self):
        # print(self.FRAME_AHEAD)
        self.simulator_ahead_frame_data = self.simulator.simulate(self.frame_data, self.player_num, None, None, self.FRAME_AHEAD)


        self.my_char = self.simulator_ahead_frame_data.getCharacter(self.player_num)
        self.op_char =  self.simulator_ahead_frame_data.getCharacter(not self.player_num)

        # print("Getting my actions")
        self.SetMyAction()
        # print("Getting op actions")
        self.SetOpAction()

    def SetMyAction(self):


        # print("clearing my actions")

        self.my_actions = []

        # print("getting eneregy")

        energy = self.my_char.getEnergy()

        #actions.add(self.gateway.jvm.enumerate.Action.)

        # print("checkig if AIR ")
        if str(self.my_char.getState()) == "AIR":
            # print("start of the for loop")
            for i in range(len(self.action_air)):
                # print("checking if we have enough energy")
                if abs(self.my_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_air[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    self.my_actions.append(self.action_air[i])
        else:
            # print("we are not in the air ")
            # print("checking the motion stuff")
            move_index = self.gateway.jvm.enumerate.Action.valueOf(self.sp_skill.name()).ordinal()
            # print("trying motion data: ",abs(self.my_motion_data[move_index].getAttackStartAddEnergy()))
            if abs(self.my_motion_data[move_index].getAttackStartAddEnergy()) <= energy:
                # print("the if worked")
                self.my_actions.append(self.sp_skill)
                # print("so did the append!")

            for i in range(len(self.action_ground)):
                if abs(self.my_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_ground[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    self.my_actions.append(self.action_ground[i])

    def SetOpAction(self):

        self.op_actions = []

        energy = self.op_char.getEnergy()


        if str(self.op_char.getState()) == "AIR":
            for i in range(len(self.action_air)):
                if abs(self.op_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_air[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    self.op_actions.append(self.action_air[i])
        else:
            if abs(self.op_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.sp_skill.name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                self.op_actions.append(self.sp_skill)

            for i in range(len(self.action_ground)):
                if abs(self.op_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_ground[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    self.op_actions.append(self.action_ground[i])


    class Java:
            implements = ["aiinterface.AIInterface"]


if __name__ == "__main__":
    print("Hi")
