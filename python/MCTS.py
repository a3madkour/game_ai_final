from py4j.java_gateway import get_field
import collections
from TreeNode import TreeNode
import math

class MCTS(object):

    FRAME_AHEAD = 14
    DEBUG_MODE = True

    def __init__(self, gateway):
        self.gateway = gateway
        self.my_actions = []
        self.op_actions = []
        self.ACTION = self.gateway.jvm.enumerate.Action


    def close(self):
        pass

    def getInformation(self, frame_data):
        # Load the frame data every time getInformation gets called
            self.frame_data = frame_data
            self.cc.setFrameData(self.frame_data, self.player_num)
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
            self.input_key = self.gateway.jvm.struct.Key()
            self.frame_data = self.gateway.jvm.struct.FrameData()
            self.cc = self.gateway.jvm.aiinterface.CommandCenter()
            self.player_num = player_num
            self.game_data = game_data
            self.simulator = self.game_data.getSimulator()
            self.is_game_just_started = True
            print("MY self char")
            self.my_char = self.frame_data.getCharacter(self.player_num)
            print(self.my_char)
            self.op_char = self.frame_data.getCharacter(not self.player_num)

            self.action_air = [ self.ACTION.AIR_GUARD , self.ACTION.AIR_A ,self.ACTION.AIR_B ,self.ACTION.AIR_DA, self.ACTION.AIR_DB ,self.ACTION.AIR_FA ,self.ACTION.AIR_FB ,self.ACTION.AIR_UA ,self.ACTION.AIR_UB ,self.ACTION.AIR_D_DF_FA ,self.ACTION.AIR_D_DF_FB ,self.ACTION.AIR_F_D_DFA ,self.ACTION.AIR_F_D_DFB ,self.ACTION.AIR_D_DB_BA , self.ACTION.AIR_D_DB_BB]

            self.action_ground = [ self.ACTION.STAND_D_DB_BA, self.ACTION.BACK_STEP,self.ACTION.FORWARD_WALK,self.ACTION.DASH,self.ACTION.JUMP,self.ACTION.FOR_JUMP,
                    self.ACTION.BACK_JUMP,self.ACTION.STAND_GUARD,self.ACTION.CROUCH_GUARD,self.ACTION.THROW_A,self.ACTION.THROW_B,self.ACTION.STAND_A,self.ACTION.STAND_B,
                    self.ACTION.CROUCH_A,self.ACTION.CROUCH_B,self.ACTION.STAND_FA,self.ACTION.STAND_FB,self.ACTION.CROUCH_FA,self.ACTION.CROUCH_FB,self.ACTION.STAND_D_DF_FA,
                    self.ACTION.STAND_D_DF_FB,self.ACTION.STAND_F_D_DFA,self.ACTION.STAND_F_D_DFB,self.ACTION.STAND_D_DB_BB]

            self.sp_skill = self.ACTION.STAND_D_DF_FC

            self.my_motion_data = self.game_data.getMotionData(self.player_num)
            self.op_motion_data = self.game_data.getMotionData(not self.player_num)




            return 0

    def input(self):
        # The input is set up to the global variable input_key
            # which is modified in the processing part
            return self.input_key

    def processing(self):
        # First we check whether we are at the end of the round
            if self.frame_data.getEmptyFlag() or self.frame_data.getRemainingFramesNumber() <= 0:
                self.is_game_just_started = True
                return
            if not self.is_game_just_started:
                # Simulate the delay and look ahead 2 frames. The simulator class exists already in FightingICE
                self.frame_data = self.simulator.simulate(self.frame_data, self.player_num, None, None, self.FRAME_AHEAD)
            else:
                # If the game just started, no point on simulating
                    self.is_game_just_started = False
            self.cc.setFrameData(self.frame_data, self.player_num)
            # distance = self.frame_data.getDistanceX()
            # energy = my.getEnergy()
            # my_x = my.getX()
            # my_state = my.getState()
            # opp_x = opp.getX()
            # opp_state = opp.getState()
            # xDifference = my_x - opp_x
            if self.cc.getSkillFlag():
                # If there is a previous "command" still in execution, then keep doing it
                    self.input_key = self.cc.getSkillKey()
                    return
            # We empty the keys and cancel skill just in case
            self.input_key.empty()
            self.cc.skillCancel()

            # print("calling MCTS Prep")
            self.MCTSPrepare()
            # print("okay calling root_node")
            # print(self.simulator_ahead_frame_data)
            # print(self.my_actions)
            # print(self.op_actions)
            # print(self.game_data)
            # print(self.player_num)
            
            root_node = TreeNode(self.gateway,self.simulator_ahead_frame_data,None,self.my_actions,self.op_actions,self.game_data,self.player_num,self.cc)
            # print("root node created")

            # print("MCTS being called")
            best_action = root_node.MCTS()
            # print("MCTS is done?")
            # print("best_action: ",best_action)
            # print(self.DEBUG_MODE)

            # print(root_node)

            if self.DEBUG_MODE:
                print(root_node)
                # print("please work")

            # print("best_action : ")
            # print(best_action)
            # print("picked action: ",best_action.name())
            self.cc.commandCall(best_action.name())

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
