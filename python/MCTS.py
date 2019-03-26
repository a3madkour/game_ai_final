from py4j.java_gateway import get_field
import collections
import TreeNode
import math

class MCTS(object):

    FRAME_AHEAD = 14
    DEBUG_MODE = True

    def __init__(self, gateway):
        self.gateway = gateway
        self.my_actions = collections.deque()
        self.op_actions = collections.deque()


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
            self.my_char = self.frame_data.getCharacter(self.player_num)
            self.op_char = self.frame_data.getCharacter(not self.player_num)
            self.action_air = ["AIR_GUARD","AIR_A","AIR_B","AIR_DA","AIR_DB","AIR_FA","AIR_FB","AIR_UA",
                    "AIR_UB","AIR_D_DF_FA","AIR_D_DF_FB","AIR_F_DF_DFA","AIR_F_D_DFB","AIR_D_DB_BA",
                    "AIR_D_DB_BB"]
            self.action_ground [ "STAND_D_DB_BA", "BACK_STEP","FORWARD_WALK","DASH","JUMP","FOR_JUMP",
                    "BACK_JUMP","STAND_GUARD","CROUCH_GUARD","THROW_A","THROW_B","STAND_A","STAND_B",
                    "CROUCH_A","CROUCH_B","STAND_FA","STAND_FB","CROUCH_FA","CROUCH_FB","STAND_D_DF_FA",
                    "STAND_D_DF_FB","STAND_F_D_DFA","STAND_F_D_DFB","STAND_D_DB_BB"]
            self.sp_skill = "STAND_D_DF_FC"

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
                    self.frame_data = self.simulator.simulate(self.frame_data, self.player_num, None, None, FRAME_AHEAD)
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

            self.MCTSPrepare()
            root_node = TreeNode(self.simulator_ahead_frame_data,None,self.my_actions,self.op_actions,self.game_data,self.player_num,self.cc)

            best_action = root_node.MCTS()
            if self.DEBUG_MODE:
                print(root_node)

            self.cc.commandCall(best_action)

    def MCTSPrepare(self):
        self.simulator_ahead_frame_data = self.simulator.simulate(self.frame_data, self.player_num, None, None, FRAME_AHEAD)

        self.my_char = self.simulator_ahead_frame_data.getCharacter(self.player_num)
        self.op_char =  self.simulator_ahead_frame_data.getCharacter(not self.player_num)

        self.SetMyAction()
        self.SetOpAction()

    def SetMyAction(self):

        self.my_actions.clear()

        energy = self.my_char.getEnergy()

        #actions.add(self.gateway.jvm.enumerate.Action.STAND_A)

        if self.my_char == "AIR":
            for i in range(len(self.action_air)):
                if math.abs(self.my_motion_data   )
        

    class Java:
            implements = ["aiinterface.AIInterface"]


if __name__ == "__main__":
    print("Hi")
