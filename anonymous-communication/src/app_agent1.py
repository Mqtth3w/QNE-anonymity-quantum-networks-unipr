"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""

from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection, Socket
from util import *


def protocol_Parity_2(sockets_send: List[int], sockets_recv: List[int], r_gen: List[int]) -> List[int]:
    r_rec = []
    r_rec.append(int(sockets_recv[0].recv()))
    for j in range(AGENTS):
        if j != agent:
            sockets_send[j].send(str(r_gen[j]))
    for j in range(2, AGENTS):
        r_rec.append(int(sockets_recv[j].recv()))
    return r_rec


def main(app_config=None, s=2, r=2):
    
    #START STEP1
    print("agent1: STEP1 receiver notification")
    try:
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent2", "agent3"], app_config)
        sockets_send = [Socket("agent1", f"agent{j}", log_config=app_config.log_config) for j in range(2, AGENTS)]
        sockets_send.insert(0, Socket("agent1", "sender", log_config=app_config.log_config))
        sockets_recv = [Socket(f"agent{j}", "agent1", log_config=app_config.log_config) for j in range(2, AGENTS)]
        sockets_recv.insert(0, Socket("sender", "agent1", log_config=app_config.log_config))
        ys = []
        # Notification
        for step in range(s):
            #(a)
            p = protocol_Notification_a(AGENT1, s, r, bcbs)
            #(b) (Parity)
            r_gen = protocol_Parity_1(AGENTS, p[AGENT1])
            r_rec = protocol_Parity_2(sockets_send, sockets_recv, r_gen)
            ys.append(protocol_Parity_3_4(r_rec, bcbs))
        #(c)
        rec = 0 if max(ys) == 0 else 1
        #rec = protocol_Notification(AGENT1, s, r, bcbs)
        print("agent1: rec={rec}")
        
    except Exception as e:
        print(f"agent1 error: {e}")
    #END STEP1
    
    #START STEP2
    print("agent1: STEP2 shared GHZ")
    # Create a socket to recv classical information
    socket = Socket("agent1", "sender", log_config=app_config.log_config)
    epr_socket = EPRSocket("sender")
    agent1 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    # teleportation to receive the GHZ qubit
    try:
        with agent1:
            q1 = epr_socket.recv_keep()[0]
            agent1.flush()
            # Get the corrections
            m1, m2 = socket.recv_structured().payload
            if m2 == 1:
                q1.X()
            if m1 == 1:
                q1.Z()
            m = q1.measure()
    except Exception as e:
        print(f"agent2 error: {e}")
    print(f"agent1: m={m}")
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
