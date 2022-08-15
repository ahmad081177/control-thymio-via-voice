#TDM client library for Thymio. 
from os import ST_APPEND
from tdmclient import ClientAsync
# aw is to run async calls to the robot.
from tdmclient import aw
#Used to run a python script on the robot.
from tdmclient.atranspiler import ATranspiler
class Thymio:
    """Wrapper functions for the robot commands. 
    Utilizes the tdmclient library to call the robot commands."""

    #constants for the Thymio's max and min speed
    MAX_SPEED = 450
    MIN_SPEED = 50
    SPEED_STEP = 50
    #Constructor
    def __init__(self):
        #Used to determine if the robot is moving forward (1) or backward (-1) or not (0)
        self.__isfwd = 0
        #The current speed of the robot
        self.__speed = 150
        #Reference to the node of the robot
        self.__node = None
        #Reference to the client
        self.__client = ClientAsync()
        #Build the commands map
        self.__build_cmd_map()


    def __build_cmd_map(self):
        """Build the commands map, the key is the command name and the value is the values to be sent to the robot
        Last item in each entry of the map is related to hand gesture"""
        self.__cmd_map = {
            'fwd': ['start', 'move', 'come','come here', 'forward', 'one'],
            'back': ['back', 'backward', 'go back', 'four'],
            'right': ['right', 'two'],
            'left': ['left', 'lift', 'three'],
            'stop': ['stop', 'stopped', 'hold', 'stuff', 'five'],
            'speed': ['speed', 'speed up', 'fast', 'faster', 'quick', 'fist'],
            'slow': ['slow', 'slower', 'calm down', 'slow down', 'y'],
        }

    def start(self) -> bool:
        """Start the client and connect to the robot.
        Returns:True in case of success, False in case of failure"""
        self.__node = Thymio.__lock_robot__(self.__client)
        if self.__node is not None:
            #Play start sound to indicate successful connection
            Thymio.__play_system_sound(self.__node, 0)
            return True
        else:
            return False
    
    
    def circle_leds(self, leds) -> bool:
        """Turn on/off the leds in the Thymio leds-circle.
        leds: A list of integers of length 8.
        Returns:True in case of success, False in case of failure"""

        if self.__node is None:
            print('Error: Robot is not initialized or not connected')
            return -1
        #initialize the leds json with the correct format and values
        v = {
            'leds.circle': [
                leds[0], leds[1], leds[2], leds[3], leds[4],
                leds[5], leds[6], leds[7]
            ],
        }
        Thymio.__set_vars__(self.__node, v)
        return True
    
    
    def coloring(self, r, g, b, istop=True)->bool:
        """Set the color of the Thymio's leds.
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
        istop: True to color the top leds, False to color the bottom leds.
        Returns:True in case of success, False in case of failure"""

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
        """Check if any element of a is in b"""
        return any(x in b for x in a)

    def is_forward(self) -> bool:
        """Returns:True if the robot is moving forward, False otherwise"""
        return self.__isfwd > 0

    def is_moving(self) -> bool:
        """Returns:True if the robot is moving, False otherwise"""
        return self.__isfwd != 0

    def __lock_robot__(client):
        """Lock the robot and return a reference to the node"""
        node = aw(client.wait_for_node())
        aw(node.lock())
        return node

    def __set_vars__(node, vars):
        """Set the variables in the robot
        vars: A dictionary of variables to set"""
        aw(node.set_variables(vars))

    def __move_robot__(node, left, right):
        """Move the robot
        left: Left speed (MIN_SPEED-MAX_SPEED)
        right: Right speed (MIN_SPEED-MAX_SPEED)"""

        v = {
            "motor.left.target": [left],
            "motor.right.target": [right],
        }
        Thymio.__set_vars__(node, v)
    
    
    def __stop_robot__(node):
        """Stop the robot"""
        Thymio.__move_robot__(node, 0, 0)

    def __play_system_sound(node, i):
        """Play a system sound on the robot.
        i: Sound index (0-5)"""

        #Prepare the python script to play the sound
        p='nf_sound_system(' + str(i) + ')'
        #Transpile the script to Aseba
        pp=ATranspiler.simple_transpile(p)
        #Compile the script
        aw(node.compile(pp))
        #Run the script asynchronously
        aw(node.run())


    def on_command(self, cmd)->bool:
        """Execute a command.
        cmd: The command to execute.
        Returns:True in case of success, False in case of failure"""

        if self.__node is None:
            print('Error: Robot is not initialized or not connected')
            return False
        if cmd is None or cmd == '':
            print('Error: Empty command')
            return False

        #color the top leds with green - indicates that the robot is executing a command
        self.coloring(0, 255, 0)
        #In case of multiple words in the command, split them
        cmd = cmd.split(' ')
        #speed up
        if self.__any_a_in_b__(cmd,self.__cmd_map['speed'])==True:
            #If robot is already moving, do speed up
            if self.is_moving:
                #speed up the robot by STEP_SPEED
                self.__speed += Thymio.STEP_SPEED
                #Make sure the speed is not greater than MAX_SPEED
                self.__speed = min(Thymio.MAX_SPEED, self.__speed)
                #keep moving fwd/back
                Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                      self.__isfwd * self.__speed)
                self.circle_leds([100, 100, 100, 100, 100, 100, 100, 100])
        #slow down
        elif self.__any_a_in_b__(cmd,self.__cmd_map['slow'])==True:
            #If robot is already moving, do slow down
            if self.is_moving:
                #slow down the robot by STEP_SPEED
                self.__speed -= Thymio.STEP_SPEED
                #Make sure the speed is not less than MIN_SPEED
                self.__speed = max(Thymio.MIN_SPEED, self.__speed)
                #keep moving fwd/back
                Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                      self.__isfwd * self.__speed)
                self.circle_leds([10, 10, 10, 10, 10, 10, 10, 10])
        #move fwd
        elif self.__any_a_in_b__(cmd,self.__cmd_map['fwd'])==True:
            #Turn the robot forward flag on
            self.__isfwd = 1
            #Move the robot forward
            Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                  self.__isfwd * self.__speed)
            self.circle_leds(
                [self.__speed, self.__speed, 0, 0, 0, 0, self.__speed, self.__speed])
        #move back
        elif self.__any_a_in_b__(cmd,self.__cmd_map['back'])==True:
            #Turn the robot forward flag off
            self.__isfwd = -1
            #Move the robot backward
            Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                  self.__isfwd * self.__speed)
            self.circle_leds(
                [0, 0, self.__speed, self.__speed, self.__speed, self.__speed, 0, 0])
        #Turn right
        elif self.__any_a_in_b__(cmd,self.__cmd_map['right'])==True:
            #If robot is moving
            if self.is_moving:
                #Turn the robot right - 
                # the left motor is set to speed and the right motor is set to 1/4 speed
                Thymio.__move_robot__(self.__node, self.__isfwd * self.__speed,
                                      self.__isfwd * self.__speed // 4)
                self.circle_leds([
                    self.__speed, self.__speed, self.__speed, self.__speed, 0, 0, 0, 0
                ])
        #Turn left
        elif self.__any_a_in_b__(cmd,self.__cmd_map['left'])==True:
            #If robot is moving
            if self.is_moving:
                #Turn the robot left -
                # the left motor is set to 1/4 speed and the right motor is set to speed
                Thymio.__move_robot__(self.__node,
                                      self.__isfwd * self.__speed // 4,
                                      self.__isfwd * self.__speed)
                self.circle_leds([
                    0, 0, 0, 0, self.__speed, self.__speed, self.__speed, self.__speed
                ])
        #stop the robot
        elif self.__any_a_in_b__(cmd,self.__cmd_map['stop'])==True:
            #Set the moving flag to 0
            self.__isfwd = 0
            #Stop the robot
            Thymio.__stop_robot__(self.__node)
            self.circle_leds([0, 0, 0, 0, 0, 0, 0, 0])
        else:
            #nothing
            print('Skip unknown command: ', cmd)
            self.coloring(255, 0, 0)
        return 1

    # def __run_python_f(node, fname,v):
    #     p=fname+'(' + str(v) + ')'
    #     pp=ATranspiler.simple_transpile(p)
    #     aw(node.compile(pp))
    #     aw(node.run())
