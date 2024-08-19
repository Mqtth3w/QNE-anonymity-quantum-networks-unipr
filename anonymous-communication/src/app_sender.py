"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from protocols import *
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection
from netqasm.sdk import Qubit
from netqasm.sdk.classical_communication.broadcast_channel import BroadcastChannelBySockets

def main(app_config=None, s=4, r=2):
    # Put your code here
    
    #yi = protocol_Notification(SENDER, s, r, app_config)
    #print(f"Sender Yi = {yi}")
    
    #bc = BroadcastChannelBySockets(app_config.app_name, ["agent1", "agent2", "agent3"])
    #bc.send("1111")
    
    sender = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
    )
    epr_socket1 = EPRSocket("agent1")
    sender1 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket1],
    )
    epr_socket2 = EPRSocket("agent2")
    sender1 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket2],
    )
    epr_socket3 = EPRSocket("agent3")
    sender1 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket3],
    )
    with sender, sender1, sender2, sender3:
        q0 = Qubit(sender)
        q1 = Qubit(sender1)
        q2 = Qubit(sender2)
        q3 = Qubit(sender3)
        #GHZ
        q0.H()
        q1.cnot(q0)
        q2.cnot(q1)
        q3.cnot(q2)
        
        
        
    
    return {}


if __name__ == "__main__": 
    main()

