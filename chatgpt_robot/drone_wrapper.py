import socket
import threading
import time
import queue

UDP_IP = "192.168.10.1"
UDP_PORT = 8889

print("Tello UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)


class Tello(object):
    def __init__(self, interface=2, timeout=6):
        self.sock = socket.socket(socket.AF_INET, 
                                  socket.SOCK_DGRAM, socket.IPPROTO_UDP) 

        self.sock.settimeout(timeout)

        self.command_queue = queue.Queue()
        self.stop_event = threading.Event()
        #self.queue_lock = threading.Lock()
        self.is_executing = False
        self.last_command_time = time.time()

        rc_thread = threading.Thread(target=self.send_rc_command)
        rc_thread.start()

    def send(self, message, verbose=False):
        ret = self.sock.sendto(bytes(message, 'utf-8'), (UDP_IP, UDP_PORT))
        if verbose:
            print('sent', '"' + message + '"')
            print('waiting for response...')

        try:
            data, server = self.sock.recvfrom(UDP_PORT)
            if verbose:
                print('recieved', data, server)
            return True
        except socket.timeout:
            if verbose:
                print('timeout, recieved no data.')
            return False
        
    def up(self, meters):
        cmd = 'up ' + str(meters)
        #print("*****",cmd,"\n")
        #with self.queue_lock:
        self.command_queue.put(cmd)
        print("upupup!\n")
        

    def down(self, meters):
        cmd = 'down ' + str(meters)
        #print("*****",cmd,"\n")
        #with self.queue_lock:
        self.command_queue.put(cmd)
        
        

    def right(self, meters):
        cmd = 'right ' + str(meters)
        #with self.queue_lock:
        self.command_queue.put(cmd)

    def left(self, meters):
        cmd = 'left ' + str(meters)
        #with self.queue_lock:
        self.command_queue.put(cmd)

    def forward(self, meters):
        cmd = 'forward ' + str(meters)
        #with self.queue_lock:
        self.command_queue.put(cmd)
        

    def back(self, meters):
        cmd = 'back ' + str(meters)
        #with self.queue_lock:
        self.command_queue.put(cmd)

    def cw(self, degrees):
        cmd = 'cw ' + str(degrees)
        #print("*****",cmd,"\n")
        #with self.queue_lock:
        self.command_queue.put(cmd)
        #print("cwcwcwcwcwcw!\n")
        

    def ccw(self, degrees):
        cmd = 'ccw ' + str(degrees)
        #with self.queue_lock:
        self.command_queue.put(cmd)
        

    def takeoff(self):
        cmd = 'takeoff'
        self.command_queue.put(cmd)

        
        
    def land(self):
        cmd = 'land'
        self.command_queue.put(cmd)
        
    def stop(self):
        cmd = 'stop'
        self.command_queue.put(cmd)
        
    def emergency(self, meters):
        cmd = 'emergency'
        self.command_queue.put(cmd)
        

    def send_rc_command(self):
        while not self.stop_event.is_set():
            try:
                command = self.command_queue.get(timeout=14)
                self.is_executing = True
                self.send(command, verbose=True)
                self.is_executing = False
                if command == 'takeoff':
                    time.sleep(6)
                else:
                    time.sleep(1) 
            except queue.Empty:
                if not self.is_executing and time.time() - self.last_command_time >= 14:
                    self.send("rc 0 0 0 0")
                    self.last_command_time = time.time()
                    time.sleep(0.1)
test = Tello()
test.send("command")


        