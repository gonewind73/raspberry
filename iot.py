import RPi.GPIO as GPIO
import time
from mns.account import Account
from mns.queue import Message,MNSExceptionBase,MNSClientException
from threading import Timer,Thread
from multiprocessing import Process,Queue
import json

class DryingRack(object):
    LightSense = 12
    WaterSense = 16
    HoerSense1 = 10   #in position
    HoerSense2 = 8    #out position
    PowerControl1 = 18
    PowerControl2 = 22

    def __init__(self):
        self.automatic = False
        self.pull_status = 0 # 0 stop 1 pullouting 2 pullining 
        GPIO_init()
        self.process_timer = Timer(1,self.timer)
        self.process_timer.start()
        pass

    def state2str(self,state):
        statestring = time.asctime()+" "
        for i in range(len(state)):
            statestring += "Y" if state[i] else "N"
        if self.pull_status:
            statestring += " pullining..." if self.pull_status==2 else " pullouting..."
        return statestring

    def get_status(self,sensor="all"):
        #sensor=all,sunny,water,inside,outside,pullstatus
        status = GPIO_read()
        status_dict={"sunny":status[0],
                    "water":status[1],
                    "innermost":status[2],
                    "outtermost":status[3],
                    "pullstatus":self.pull_status,
                    "automatic":self.automatic}
        return json.dumps(status_dict)
    
    def do_action(self,action):
        #action=pullin,pullout,stop
        if action=="pullin":
            self.pull_status = pullin()
        if action=="pullout":
            self.pull_status  = pullout()
        if action=="stop":
            self.pull_status  = stop()
        return self.get_status() 
    
    def config(self,config_dict):
        #config: auto:True,starttime:9,endtime:18
        self.automatic = config_dict.get("auto",True)
        return self.get_status() 

    def process(self,status):
        light,water,h1,h2 = status
        if water and not h1:
            self.pull_status = pullin()
        if self.automatic and light and not h2:
            self.pull_status = pullout()
        if self.pull_status==1 and h2:
            self.pull_status = stop()
        if self.pull_status==2 and h1:
            self.pull_status = stop()
        if self.pull_status :
            print "pull status = %s"%("pullining" if pull_state==2 else "pullouting")
        return

    def timer(self):
        status = GPIO_read()
        print time.asctime(),"status",status
        self.process(status)
        self.process_timer = Timer(1,self.timer)
        self.process_timer.start()
        
        


LightSense = 12
WaterSense = 16
HoerSense1 = 10   #in position
HoerSense2 = 8    #out position
PowerControl1 = 18
PowerControl2 = 22

automatic = False
pull_state = 0  # 0 stop 1 pullouting  2 pullining
quiting = False


def GPIO_init():
    # to use Raspberry Pi board pin numbers
    GPIO.setmode(GPIO.BOARD)
    # set up GPIO output channel
    GPIO.setup(PowerControl1, GPIO.OUT)
    GPIO.setup(PowerControl2, GPIO.OUT)
    # set RPi board pin PowerControl1 high
    GPIO.output(PowerControl1, GPIO.HIGH)
    GPIO.output(PowerControl2, GPIO.HIGH)
    # set up GPIO input with pull-up control
    # (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)
    GPIO.setup(LightSense, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(WaterSense, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HoerSense1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HoerSense2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def GPIO_clean():
    GPIO.cleanup()

def process(light,water,h1,h2):
    if water and not h1:
        pullin()
    if automatic and light and not h2:
        pullout()
    if pull_state==1 and h2:
        stop()
    if pull_state==2 and h1:
        stop()
    if pull_state :
        print "pull status = %s"%("pullining" if pull_state==2 else "pullouting")
    return

def state2str(state):
    statestring = time.asctime()+" "
    for i in range(len(state)):
        statestring += "Y" if state[i] else "N"
    return statestring

""" init()   
while True:
    state=read()
    process(state)
    time.sleep(1)
    
clean() """

def GPIO_read():
    # input from RPi board pin ligth_sense
    light_value = not GPIO.input(LightSense)  # 0 sunny 1 no sunny
    water_value = not GPIO.input(WaterSense)  # 0 water 1 no water
    hoer1_value = not GPIO.input(HoerSense1)  # 0 near  1 no near
    hoer2_value = not GPIO.input(HoerSense2)  
    return light_value,water_value,hoer1_value,hoer2_value

def pullout():
    global pull_state
    GPIO.output(PowerControl1, GPIO.LOW)
    GPIO.output(PowerControl2, GPIO.HIGH)
    pull_state = 1
    print "start to pullout..."
    return 1

def pullin():
    global pull_state
    GPIO.output(PowerControl1, GPIO.HIGH)
    GPIO.output(PowerControl2, GPIO.LOW)
    pull_state = 2
    print "start to pullin..."
    return 2

def stop():
    global pull_state
    GPIO.output(PowerControl1, GPIO.HIGH)
    GPIO.output(PowerControl2, GPIO.HIGH)
    pull_state = 0
    print "pull stop."
    return 0



def send_message(queue,message):
    try:
        msg = Message(message)
        re_msg = queue.send_message(msg)
        print "Send Message Succeed! MessageBody:%s MessageID:%s" % (message, re_msg.message_id)
    except MNSExceptionBase, e:
        if e.type == "QueueNotExist":
            print "Queue not exist, please create queue before send message."
        print "Send Message Fail! Exception:%s\n" % e

def receive_message(queue,wait_seconds=3):
    #receive message
    try:
        recv_msg = queue.receive_message(wait_seconds)
        print "Receive Message Succeed! ReceiptHandle:%s MessageBody:%s MessageID:%s" % (recv_msg.receipt_handle, recv_msg.message_body, recv_msg.message_id)
        return recv_msg
    except MNSExceptionBase,e:
        if e.type == "QueueNotExist":
            print "Queue not exist, please create queue before receive message."
        elif e.type == "MessageNotExist":
            pass
        #     print "Queue is empty!"
        # print "Receive Message Fail! Exception:%s\n" % e
     

def delete_message(queue,recv_msg):
    try:
        queue.delete_message(recv_msg.receipt_handle)
        print "Delete Message Succeed!  ReceiptHandle:%s" % recv_msg.receipt_handle
    except MNSExceptionBase,e:
        print "Delete Message Fail! Exception:%s\n" % e

def control_thread(my_account,quit):
    
    control_queue = my_account.get_queue("control-queue")
    #control_queue = my_account
    while not quiting and not quit.qsize():
        recv_msg = receive_message(control_queue)
        if recv_msg:
            if recv_msg.message_body =="pullin":
                pullin()
            if recv_msg.message_body =="pullout":
                pullout()
            delete_message(control_queue,recv_msg)

def ioread_thread(my_account,quit):

    last_state = (0,0,0,0)
    device_queue = my_account.get_queue("device1")
    #device_queue = my_account
    time.sleep(1)
    while not quiting and not quit.qsize():
        state = GPIO_read()
        if not last_state == state:
            process(state[0],state[1],state[2],state[3])
            last_state = state
            print state2str(state)
            send_message(device_queue,state2str(state))
        time.sleep(0.1)
    GPIO_clean()


if __name__ == '__main__':
    print "start deamon!"
    #init my_account, my_topic
    endpoint="http://1402010103453031.mns.cn-hangzhou.aliyuncs.com/"
    access_id = "LTAIfpx57LeEmMKs"
    access_key = "nUqBzUFc48cTVIZh3mkpcnmosxvGTz"
    token=""

    quit = Queue()
    dr = DryingRack()
    GPIO_init()
    #init my_account, my_topic
    my_account = Account(endpoint, access_id, access_key, token)
    # queue_name =  "control-queue"
    # my_queue = my_account.get_queue(queue_name)
    #Thread(target=control_thread,args=(my_account,)).start()
    
    #Thread(target=ioread_thread,args=(my_queue,)).start()
    Process(target=ioread_thread,args=(my_account,quit)).start()

    Process(target=control_thread,args=(my_account,quit)).start()
    #ioread_thread(my_account)

    while True:
        s = raw_input("type quit to quit:")
        if s=="quit":
            quiting = True
            quit.put("quit")
            break
    
    

    

        