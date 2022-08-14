from tdmclient import ClientAsync, aw
from tdmclient.atranspiler import ATranspiler
class Thymio:
    MAX_SPEED = 90
    MIN_SPEED = 40
    def __init__(self):
        self.__isfwd = 0
        self.__speed = 50
        self.__node = None
        self.__client = ClientAsync()
        self.__build_cmd_map()
    def __build_cmd_map(self):
        # Last item in each entry of the map is related to hand gesture
        self.__cmd_map = {
            'fwd': ['start', 'move', 'come','come here', 'forward', 'one'],
            'back': ['back', 'backward', 'go back', 'four'],
            'right': ['right', 'two'],
            'left': ['left', 'lift', 'three'],
            'stop': ['stop', 'stopped', 'hold', 'stuff', 'five'],
            'speed': ['speed', 'speed up', 'fast', 'faster', 'quick', 'fist'],
            'slow': ['slow', 'slower', 'calm down', 'slow down', 'y'],
        }
    def start(self):
        self.__node = Thymio.__lock_robot__(self.__client)
        if self.__node is not None:
            Thymio.__play_system_sound(self.__node, 0)
            return 1
        else:
            return 0
    def circle_coloring(self, colors):
        if self.__node is None:
            print('Error: Robot is not initialized or not connected')
            return -1
        v = {
            'leds.circle': [
                colors[0], colors[1], colors[2], colors[3], colors[4],
                colors[5], colors[6], colors[7]
            ],
        }
        Thymio.__set_vars__(self.__node, v)
        return 1
    def coloring(self, r, g, b, istop=True):
        if self.__node is None:
            print('Error: Robot is not initialized or not connected')
            return -1
        v = {}
        if istop == True:
            v = { 'leds.top': [r, g, b], }
        else:
            v = {'leds.bottom': [r, g, b], }
        Thymio.__set_vars__(self.__node, v)
        return 1
    def __any_a_in_b__(self,a,b):
        return any(x in b for x in a)
    @property
    def speed(self):
        return self.__speed
    @speed.setter
    def speed(self, speed):
        self.__speed = speed
    @property
    def is_forward(self):
        return self.__isfwd > 0
    @property
    def is_moving(self):
        return self.__isfwd != 0
    def __lock_robot__(client):
        node = aw(client.wait_for_node())
        aw(node.lock())
        return node
    def __set_vars__(node, vars):
        aw(node.set_variables(vars))
    def __move_robot__(node, left, right):
        v = {
            "motor.left.target": [left],
            "motor.right.target": [right],
        }
        Thymio.__set_vars__(node, v)
    def __stop_robot__(node):
        Thymio.__move_robot__(node, 0, 0)
    def __play_system_sound(node, i):
        p='nf_sound_system(' + str(i) + ')'
        pp=ATranspiler.simple_transpile(p)
        aw(node.compile(pp))
        aw(node.run())
    def on_command(self, cmd):
        if self.__node is None:
            print('Error: Robot is not initialized or not connected')
            return -1
        if cmd is None or cmd == '':
            print('Error: Empty command')
            return -1
        self.coloring(0, 255, 0)
        #the dictation sometimes add "the" to the command
        cmd = cmd.split(' ')
        #speed up
        if self.__any_a_in_b__(cmd,self.__cmd_map['speed'])==True:
            if self.is_moving:
                #Thymio.__play_system_sound(self.__node, 4)
                self.speed += 20
                self.speed = min(Thymio.MAX_SPEED, self.speed)
                #keep moving fwd/back
                Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                      self.__isfwd * self.__speed)
                self.circle_coloring([100, 100, 100, 100, 100, 100, 100, 100])
        #slow down
        elif self.__any_a_in_b__(cmd,self.__cmd_map['slow'])==True:
            if self.is_moving:
                self.speed -= 20
                self.speed = max(Thymio.MIN_SPEED, self.speed)
                #keep moving fwd/back
                Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                      self.__isfwd * self.__speed)
                self.circle_coloring([10, 10, 10, 10, 10, 10, 10, 10])
        #move fwd
        elif self.__any_a_in_b__(cmd,self.__cmd_map['fwd'])==True:
            self.__isfwd = 1
            Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                  self.__isfwd * self.__speed)
            self.circle_coloring(
                [self.speed, self.speed, 0, 0, 0, 0, self.speed, self.speed])
        #move back
        elif self.__any_a_in_b__(cmd,self.__cmd_map['back'])==True:
            self.__isfwd = -1
            Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                  self.__isfwd * self.__speed)
            self.circle_coloring(
                [0, 0, self.speed, self.speed, self.speed, self.speed, 0, 0])
        #right
        elif self.__any_a_in_b__(cmd,self.__cmd_map['right'])==True:
            if self.is_moving:
                Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                      self.__isfwd * self.__speed // 4)
                self.circle_coloring([
                    self.speed, self.speed, self.speed, self.speed, 0, 0, 0, 0
                ])
        #left
        elif self.__any_a_in_b__(cmd,self.__cmd_map['left'])==True:
            if self.is_moving:
                Thymio.__move_robot__(self.__node,
                                      self.__isfwd * self.__speed // 4,
                                      self.__isfwd * self.__speed)
                self.circle_coloring([
                    0, 0, 0, 0, self.speed, self.speed, self.speed, self.speed
                ])
        #stop
        elif self.__any_a_in_b__(cmd,self.__cmd_map['stop'])==True:
            self.__isfwd = 0  #not fwd not back
            Thymio.__stop_robot__(self.__node)
            self.circle_coloring([0, 0, 0, 0, 0, 0, 0, 0])
        else:
            #nothing
            print('Skip unknown command: ', cmd)
            self.coloring(255, 0, 0)
        return 1

    def __run_python_f(node, fname,v):
        p=fname+'(' + str(v) + ')'
        pp=ATranspiler.simple_transpile(p)
        aw(node.compile(pp))
        aw(node.run())
