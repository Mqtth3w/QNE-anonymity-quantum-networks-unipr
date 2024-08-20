"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""

from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection, Socket
from util import *

def main(app_config=None, s=2, r=2):
    
    #START STEP1
    try:
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent1", "agent3"])
        msg = bcbs.recv()
        print(f"agent2: {msg}")
    except Exception as e:
        print(f"agent2 error: {e}")
    #END STEP1
    
    #START STEP2
    print("agent2: STEP2 shared GHZ")
    # Create a socket to recv classical information
    socket = Socket("agent2", "sender", log_config=app_config.log_config)
    epr_socket = EPRSocket("sender")
    agent2 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    # teleportation to receive the GHZ qubit
    try:
        with agent2:
            q2 = epr_socket.recv_keep()[0]
            agent2.flush()
            # Get the corrections
            m1, m2 = socket.recv_structured().payload
            if m2 == 1:
                q2.X()
            if m1 == 1:
                q2.Z()
            m = q2.measure()
    except Exception as e:
        print(f"agent2 error: {e}")
    print(f"agent2: m={m}")    
    #END STEP2
    
    
    #START STEP3
    #(a)
    #RandomBit 1.
    xi = 0
    #RandomBit 2. (LogicalOR)
    
    #END STEP3
    
    
    return {"0":0}


if __name__ == "__main__": 
    main()

