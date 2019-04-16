from py4j.java_gateway import get_field



class State(object):
    #always assume we are ZEN
    features_num = 46

    def __init__(self,gateway,game_data,cc,player_num):

        self.cc = cc
        self.game_data = game_data
        self.player_num = player_num
        self.gateway = gateway
        # print("oh god why")
        self.ACTION = self.gateway.jvm.enumerate.Action
        self.features = [0.0] * self.features_num
        self.last_features = [0.0] * self.features_num
        self.distance = []
        self.energy = 0
        self.proj_num = 0
        self.my_last_pos = [0,0]
        self.op_last_pos = [0,0]
        self.close_proj = False
        self.op_motion = ''
        self.action_ground = []
        self.action_air = []
        self.option_general = ['OPTION_MCTS']
        self.option_air = []
        self.option_op_ground = ['OPTION_KICKER']
        self.option_op_air = ['OPTION_ANTIAIR']

        # print("player_num")
        # print(player_num)

        self.frame_data = self.gateway.jvm.struct.FrameData()
        # print(self.frame_data)

        self.my_char = self.frame_data.getCharacter(player_num)
        self.op_char = self.frame_data.getCharacter(not player_num)

        # print(self.my_char)
        # print(self.op_char)

        self.my_actions = []
        self.my_actions_index = []
        self.op_actions = []
        self.op_actions_index = []

    def Update(self,cc,frame_data,player_num):

        # print("update called sucessfully")
        cc.setFrameData(frame_data,player_num)
        self.frame_data = frame_data
        self.distance = [self.frame_data.getDistanceX(),self.frame_data.getDistanceY()]
        self.energy = self.frame_data.getCharacter(player_num).getEnergy()
        self.my_char = self.frame_data.getCharacter(player_num)
        self.op_char = self.frame_data.getCharacter(not player_num)
        self.diff_x = self.my_char.getX() - self.op_char.getX()
        self.enemy_speed =[self.op_char.getSpeedX(),self.op_char.getSpeedY()]

        self.my_skil_name = self.my_char.getAction().name()
        self.op_skil_name = self.op_char.getAction().name()


    def SetFeatures(self,features):
        self.last_features = self.features
        self.features = features


    def GetFeatures(self,frame_data,reward):

        # print("Get Features being called")
        
        my_char = frame_data.getCharacter(self.player_num)
        op_char = frame_data.getCharacter(not self.player_num)

        return_value = [0.0] * self.features_num


        is_front = my_char.isFront()
        op_is_front = op_char.isFront()

        self.proj_num = 0
        i = 0
        my_proj_num = 0
        op_proj_num = 0

        close_proj = False



        attacks = frame_data.getProjectiles()

        opp_skill_name = op_char.getAction().name()

        # print("setting up done!")

        # print("first if")
        if (not op_char.getState() == "AIR" and not op_char.getState() == "DOWN"):
            # print("passed?")
            return_value[i] = 1.0
            # print("i guess?")

        i+= 1

        # print("where?")
        if (op_char.getState() == "AIR"):
            return_value[i] = 1.0

        i+= 1

        # print("do you?")
        if (op_char.getState() == "DOWN"):
            return_value[i] = 1.0

        i+= 1

        # print("fail?")
        my_x = my_char.getX() + 200
        my_y = my_char.getY() 
        op_x = op_char.getX() + 200
        op_y = op_char.getY() 

        # print("is it here?")
        # print(is_front)
        # print(my_x)
        if is_front:
            my_x -= 80

        # print("op front")
        if op_is_front:
            op_x -= 80

        # print("or here here?")
        if my_x > 880:
            my_x = 880
            
        if op_x > 880:
            op_x = 880

        if my_x < 0:
            my_x = 0

        if op_x < 0:
            op_x = 0

        # print("is closer being calc")
        is_closer = abs(my_x - 440) < abs(op_x - 440)

        if is_closer:
            return_value[i] = 1

        i += 1

        # print("is closer being checked 2")
        if not is_closer:
            return_value[i] = 1

        i += 1

        if is_front:
            my_x -= 20
        else:
            my_x += 20

        if my_x <= 180:
            return_value[i] = 1

        i+= 1

        if my_x >= 700:
            return_value[i] = 1
        
        i += 1

        if my_x > 180 and my_x < 700:
            return_value[i] = 1

        i += 1 
        
        # print("fancy if start here")
        if (my_x >= 180 and my_x < 260) or (my_x >= 620 and my_x < 700):
            return_value[i] = 1

        i += 1 

        if (my_x >= 260 and my_x < 360) or (my_x >= 420 and my_x < 620):
            return_value[i] = 1

        i += 1 

        if (my_x >= 360 and my_x < 420): 
            return_value[i] = 1

        i += 1 


        if is_front:
            my_x += 20
        else:
            my_x -= 20


        # print("op but y")
        if (op_y >= 300 and op_y < 350): 
            return_value[i] = 1

        i += 1 

        if (op_y >= 250 and op_y < 300): 
            return_value[i] = 1

        i += 1 

        if (op_y >= 200 and op_y < 250): 
            return_value[i] = 1

        i += 1 

        if (op_y >= 150 and op_y < 200): 
            return_value[i] = 1

        i += 1 

        if (op_y >= 50 and op_y < 150): 
            return_value[i] = 1

        i += 1 


        if (op_y < 50): 
            return_value[i] = 1

        i += 1 
        
        # print("distances though")
        distance_x = abs(abs(my_x) - abs(op_x)) 
        distance_y = abs(abs(my_y) - abs(op_y)) 

        
        if distance_x <= 64:
            return_value[i] = 1

        i += 1

        
        if (distance_x > 64 and distance_x <= 84):
            return_value[i] = 1

        i += 1
        
        if (distance_x > 84 and distance_x <= 100):
            return_value[i] = 1

        i += 1
        
        if (distance_x > 100 and distance_x <= 190):
            return_value[i] = 1

        i += 1
        
        if (distance_x > 190 and distance_x <= 310):
            return_value[i] = 1

        i += 1
        
        if (distance_x > 310 ):
            return_value[i] = 1

        i += 1


        #mX= my_x, mY = my_y,mlx,mly = my_last_pos ,isfront,i
            
        # print("my_last_pos")
        # print(self.my_last_pos[1])
        # print(self.my_last_pos[0])
        # print("i: ",i)
        if my_y - self.my_last_pos[1] < 0:

            if my_x - self.my_last_pos[0] == 0:
                return_value[i] = 1

            # print("we good")
            i +=  1

            if is_front:
                if my_x - self.my_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1

            if not is_front:
                if my_x - self.my_last_pos[0] < 0:
                    return_value[i] = 1
            i +=  1

            if is_front:
                if my_x - self.my_last_pos[0] < 0:
                    return_value[i] = 1

            i +=  1

            if not is_front:
                if my_x - self.my_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1

            i += 5

            
        elif my_y - self.my_last_pos[1] > 0:
            i += 5
            if my_x - self.my_last_pos[0] == 0:
                return_value[i] = 1

            # print("we good")
            i +=  1

            if is_front:
                if my_x - self.my_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1

            if not is_front:
                if my_x - self.my_last_pos[0] < 0:
                    return_value[i] = 1
            i +=  1

            if is_front:
                if my_x - self.my_last_pos[0] < 0:
                    return_value[i] = 1
            i +=  1

            if not is_front:
                if my_x - self.my_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1

        # print(self.op_last_pos)
            
        # print("i: ",i)

        if op_y - self.op_last_pos[1] < 0:
            if op_x - self.op_last_pos[0] == 0:
                return_value[i] = 1

            i +=  1

            if op_is_front:
                if op_x - self.op_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1

            if not op_is_front:
                if op_x - self.op_last_pos[0] < 0:
                    return_value[i] = 1
            i +=  1

            if op_is_front:
                if op_x - self.op_last_pos[0] < 0:
                    return_value[i] = 1


            if not op_is_front:
                if op_x - self.op_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1

            i += 5

        elif op_y - self.op_last_pos[1] > 0:
            i += 5
            if op_x - self.op_last_pos[0] == 0:
                return_value[i] = 1

            i +=  1

            if op_is_front:
                if op_x - self.op_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1

            if not op_is_front:
                if op_x - self.op_last_pos[0] < 0:
                    return_value[i] = 1
            i +=  1

            if op_is_front:
                if op_x - self.op_last_pos[0] < 0:
                    return_value[i] = 1

            if not op_is_front:
                if op_x - self.op_last_pos[0] > 0:
                    return_value[i] = 1
            i +=  1


        # print("i: ",i)
        # print("looping through attacks")
        # print(attacks)
        for attack in attacks:

            if attack.isPlayerNumber():
                my_proj_num += 1
            else:
                op_proj_num += 1

            hit_area = attack.getCurrentHitArea()

            if is_front:
                if (hit_area.getLeft() < (my_x + 100)) and (hit_area.getLeft() > my_x ):
                    close_proj = True
            else:
                if (hit_area.getLeft() > (my_x - 100)) and (hit_area.getLeft() < my_x ):
                    close_proj = True

        
        # print("the loop is over")
        if close_proj:
            return_value[i] = 1
        i +=  1
        
        # print("close_prj")
        if my_proj_num > 1 :
            return_value[i] = 1

        i += 1

        if op_proj_num > 1:
            return_value[i] = 1

        i += 1


        self.my_last_pos = [my_x,my_y]
        self.op_last_pos = [op_x,op_y]

        self.features = return_value
        # print("so everything is good, I just need to check what is calling this")

        return self.features

    def SetActions(self,frame_data,player_num):
        #use this for op if we assume they do the same strategy i.e they consider the options we do under the same circumstances that we do
        # print("setActions is called!")
        my_char = frame_data.getCharacter(player_num)
        op_char = frame_data.getCharacter(not player_num)

        my_actions = []
        my_actions_index = []
        energy = my_char.getEnergy()
        # print("getting motion data")

        my_motion_data = self.game_data.getMotionData(player_num)


        # print("first if")
        # print("my_char: ",my_char)
        # print("my_char state: ",my_char.getState())
        # print("my_char state 2: ",str(my_char.getState()))
        if str(my_char.getState()) == "AIR":
            # print("for loop in the air")
            for i in range(len(self.action_air)):
                if abs(my_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_air[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    my_actions.append(self.action_air[i])
                    my_actions_index.append(i)

            for i in range(len(self.option_air)):
                my_actions.append(self.option_air[i])
                my_actions_index.append(i + len(self.action_air))
        else:
            # print("for loop in the ground")
            # print(self.action_ground)
            # print("the len:",len(self.action_ground))
            for i in range(len(self.action_ground)):
                # print("another if")
                if abs(my_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_ground[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    my_actions.append(self.action_ground[i])
                    my_actions_index.append(i + len(self.option_air)+ len(self.action_air))
                # print("the if is done!")

            # print("trying my luck with op_char")
            # print(op_char.getY())
            if op_char.getY() < 335:
                # print("the if is checking")
                for i in range(len(self.option_op_air)):
                    # print("for loop op air")
                    if frame_data.getDistanceX() < 150:
                        # print("frame data get Distance X")
                        my_actions.append(self.option_op_air[i])
                        my_actions_index.append(i + len(self.action_ground)+ len(self.option_air)+ len(self.action_air))
            else:
                # print("else")
                for i in range(len(self.option_op_ground)):
                    # print("for loop op ground")
                    my_actions.append(self.option_op_ground[i])
                    my_actions_index.append(i+ len(self.action_ground) + len(self.option_op_air)+ len(self.option_air)+ len(self.action_air))
        
        # print("op general")
        # print(self.option_general)
        for i in range(len(self.option_general)):
            # print("for loop op general")
            my_actions.append(self.option_general[i])
            my_actions_index.append(i+len(self.option_op_ground)+ len(self.action_ground) + len(self.option_op_air)+ len(self.option_air)+ len(self.action_air))

        if player_num:
            self.my_actions = my_actions
            self.my_actions_index = my_actions_index
        else:
            self.op_actions = my_actions
            self.op_actions_index = my_actions_index

        # print("my_actions: ",my_actions)

    def SetOpActions(self):

        self.op_actions = []
        self.op_actions_index = []

        energy = self.op_char.getEnergy()

        op_motion_data = self.game_data.getMotionData(self.player_num)

        if str(self.op_char.getState()) == "AIR":
            for i in range(len(self.action_air)):
                if abs(op_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_air[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    self.op_actions.append(self.action_air[i])
                    self.op_actions_index.append(i)
        else:
            if abs(op_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.sp_skill.name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                self.op_actions.append(self.sp_skill)
                self.op_actions_index.append(i+len(self.action_air))

            for i in range(len(self.action_ground)):
                if abs(op_motion_data[self.gateway.jvm.enumerate.Action.valueOf(self.action_ground[i].name()).ordinal()].getAttackStartAddEnergy()) <= energy:
                    self.op_actions.append(self.action_ground[i])
                    self.op_actions_index.append(i+len(self.action_air)+1)





        

