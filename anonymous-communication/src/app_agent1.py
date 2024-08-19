"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from protocols import *
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection
from netqasm.sdk.classical_communication.broadcast_channel import BroadcastChannelBySockets

def main(app_config=None, s=4, r=2):
    # Put your code here
    
    #yi = protocol_Notification(AGENT1, s, r, app_config)
    #print(f"Agent1 Yi = {yi}")
    
    #bc = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent2", "agent3"])
    #m = bc.recv()
    #print(m)
    
    return {}


if __name__ == "__main__": 
    main()

