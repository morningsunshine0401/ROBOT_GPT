import openai
import re
import argparse
from drone_wrapper import *
from tellovideo import *
import math
import numpy as np
import os
import json
import time
#import rclpy
#import whisper
#####################################################
from mic import *


####################################################
parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, default="prompts/airsim_basic.txt")
parser.add_argument("--sysprompt", type=str, default="system_prompts/airsim_basic.txt")
args = parser.parse_args()

with open("config.json", "r") as f:
    config = json.load(f)

print("Initializing ChatGPT...")
openai.api_key = config["OPENAI_API_KEY"]

with open(args.sysprompt, "r") as f:
    sysprompt = f.read()

chat_history = [
    {
        "role": "system",
        "content": sysprompt
    },
    {
        "role": "user",
        "content": "why don't you start off and look around and go up about 40cm to see higher places and then land"
    },
    {
        "role": "assistant",
        "content": """```python
te.takeoff()
te.cw(360)
te.ccw(360)
te.up(40)
te.land()
'''
This code uses the `te.takeoff()' function first then uses 'te.cw(360)' function twice to look around two times and then go up 40cm by using 'te.up(40)' function then lands by using 'te.land()' function."""
    }
]


def ask(prompt):
    chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_history,
        temperature=0
    )
    chat_history.append(
        {
            "role": "assistant",
            "content": completion.choices[0].message.content,
        }
    )
    return chat_history[-1]["content"]


print(f"Done.")

code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)


def extract_python_code(content):
    code_blocks = code_block_regex.findall(content)
    if code_blocks:
        full_code = "\n".join(code_blocks)

        if full_code.startswith("python"):
            full_code = full_code[7:]

        return full_code
    else:
        return None



print(f"Initializing...")
#############rclpy.init()
te = Tello()
time.sleep(1)
#mytello=MyTello()
#mytello.mystart()
print(f"Done.")

with open(args.prompt, "r") as f:
    prompt = f.read()

ask(prompt)
print("Welcome to the weird chatbot! I am ready to help you with your questions and commands.")

'''
#model_w=whisper.load_model("base")
#result_w = model_w.transcribe("Whisper.m4a")
server_ip = '0.0.0.0'  # Listen to all available interfaces
server_port = 12345

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP address and port
server_socket.bind((server_ip, server_port))

# Listen for incoming connections
server_socket.listen(1)
print(f"Server is listening on {server_ip}:{server_port}")

# Accept a connection
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}")
message = client_socket.recv(1024).decode('utf-8')
#print(f"Message received: {message}")
result_w=message
# Close the sockets
client_socket.close()
server_socket.close()

recv=0
'''
#############################################################################################

#mic=VoiceRecognizer()
#message=mic.main()
           
#############################################################################################
while True:
   #if recv==0:
   
        #client_socket, client_address = server_socket.accept()
        #print(f"Connection from {client_address}")
        #message = client_socket.recv(1024).decode('utf-8')
        #client_socket.close()
        #result_w=message
        result_w=input(">>>")
     
        
        #server_socket.close()
        question = result_w
        #question = input("ask me something?> ")

        if question == "!quit" or question == "!exit":
            print("okok ending code\n")
            break

        if question == "!clear":
            os.system("cls")
            continue

        response = ask(question)

        print(f"\n{response}\n")

        code = extract_python_code(response)
        if code is not None:
            print("Please wait while I run the code...")
            exec(extract_python_code(response))
            print("Done!\n")
          #  recv=1
