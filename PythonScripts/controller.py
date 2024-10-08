global signals
global signal_pairs
global screen
CHROMIS_TEAL = (0, 200, 180)
SHARK_ATTACK = (100, 15, 10)
BLACK = (0,0,0)
WHITE = (255,255,255)
PURPLE = (80,15,130)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
color = CHROMIS_TEAL
#GREY = (127, 127, 127)
#color = Grey
#This is the code that was on the computer but not on the GitHub (I don't think it has an actual effect)

DEFAULT = 0
RECORDING = 1
PLAYBACK = 2

if __name__ == "__main__":
    import requests
    import urllib.parse
    import pygame
    import pygame.joystick as ctrl
    import os
    
    #Allow for controller inputs to be recieved while the window is not in focus.
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

    pygame.init()
    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("ROV Control")
    pygame.display.init()
    clock = pygame.time.Clock()
    wifi = True

    #Which controller does what
    bindings = [-1, -1]


    ctrl.init()
    try:
        joy = ctrl.Joystick(0)
        joy.init()
        print("Detected controller 1: "+ str(joy))
        try:
            joy2 = ctrl.Joystick(1)
            joy2.init()
            print("Detected controller 2: "+str(joy2))
        except:
            print("ONLY ONE CONTROLLER")
            joy2 = {}
    except:
        print("NO CONTROLLER")
        joy = {}

    running = True
    #IP of raspberry pi DO NOT FORGET
    rovIP = "192.168.1.20"
    signals = []
    signal_pairs = {
    1:"arm_open",
    2:"arm_close",
    3:"arm_clockwise",
    4:"arm_counter_clockwise",
    }
    config = {}
    config_old = {}
    #Sort dictionary of inputs.
    def sort_dict(dictionary):
        keys = [key for key in dictionary.keys()]
        if len(keys) > 0:
            keys.sort()
            new_dict = {key:dictionary[key] for key in keys}
            return new_dict
        else:
            return {}
        
    #Clear input array
    def clear_arr():
        global signals
        signals = []

    #Send inputs to bot
    def send_signals():
        global color

        if wifi:
            query = {str(i):config[i] for i in config.keys()}
            #turn it into a url
            query = urllib.parse.urlencode(query)
            #check if we get an error
            try:
                #build the whole url
                r = requests.get("http://" + rovIP + ":5000" + "/?" + query)

                state = int(r.text)

                print(state)
                if state == DEFAULT:
                    color = CHROMIS_TEAL
                elif state == RECORDING:
                    color = RED
                elif state == PLAYBACK:
                    color = GREEN
                else:
                    color = PURPLE # If you see purple, something very strange has happened (An invalid state was returned by the bot, likely indicating that the webserver returned an error)

                    print(r.text) #Print server error message


                #we sent the signals, ready to accept new ones
                # signals = []
            except Exception as e:
                print(str(e))
        else:
            print_dict(config)

    #I'm not actually sure what these functions do or what they are for
    def get_signals():
        print_signals()
        return input()
    def print_signals():
        print("Enter key to indicate signal")
        for i in signal_pairs.keys():
            print(str(i)+":"+signal_pairs[i])
        print("Or send to send")
    def add(signal):
        signals.append(signal)
    def handle_input():
        typed = get_signals()
        if typed != "send":
            add(int(typed))
            typed = get_signals()
        else:
            send_signals()

    #Print inputs for debug mode
    def print_dict(dictionary):
        os.system('cls')
        for key in dictionary.keys():
            print(str(key)+":"+str(dictionary[key]))

    #Main Loop
    while running:
        screen.fill(color)
        pygame.display.flip()
        
        #Iterate through recieved inputs
        for event in pygame.event.get():
            #Bind unbound controllers
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYHATMOTION:
                if bindings[event.instance_id] == -1:
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 6:
                            bindings[event.instance_id] = 0
                        elif event.button == 7:
                            bindings[event.instance_id] = 1
                else:
                    gamepad_id = bindings[event.instance_id]

                    #Rebind bound controllers
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 6:
                            bindings[event.instance_id] = 0
                        elif event.button == 7:
                            bindings[event.instance_id] = 1

                        #Serialize inputs
                        gamepad_id = bindings[event.instance_id]
                        config["button-"+str(event.button)+"-"+str(gamepad_id)] = True
                    elif event.type == pygame.JOYBUTTONUP:
                        config["button-"+str(event.button)+"-"+str(gamepad_id)] = False
                    elif event.type == pygame.JOYAXISMOTION:
                        config["axis-"+str(event.axis)+"-"+str(gamepad_id)] = event.value
                    elif event.type == pygame.JOYHATMOTION:
                        config["hat-"+str(event.hat)+"-"+str(gamepad_id)] = event.value

            #Detect when the window is closed
            elif event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit()

        #Send inputs
        config = sort_dict(config)
        
        if (config != config_old):
            send_signals()
        config_old = config.copy()
        # handle_input()
        clock.tick(32)

