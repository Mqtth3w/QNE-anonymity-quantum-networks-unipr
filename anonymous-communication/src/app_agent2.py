"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection, Socket
from util import *

def protocol_Parity_2(sockets_send: List[int], sockets_recv: List[int], r_gen: List[int]) -> List[int]:
    r_rec = []
    try:
        for j in range(AGENTS - 2): # receive from agent 1 and 2
            print(f"agent2 receive from {j}")
            r_rec.append(int(sockets_recv[j].recv()))
        i = 0
        for j in range(AGENTS): # send to all other agents
            if j != AGENT2:
                print(f"agent2 send to {j}")
                sockets_send[i].send(str(r_gen[j]))
                i += 1
        print("agent2 receive from 3")
        r_rec.append(int(sockets_recv[-1].recv())) # receive fro agent 3
    except Exception as e:
        print(f"agent2 error: {e}")
    return r_rec

def protocol_Parity_3_4(r_rec: List[int], bcbs: BroadcastChannelBySockets) -> int:
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    z_rec = [zj]
    for i in range(AGENTS - 2):
        z_rec.append(int(bcbs.recv()[1]))
    bcbs.send(str(zj))
    z_rec.append(int(bcbs.recv()[1]))
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi

def main(app_config=None, s=2, r=2):
    
    #START STEP1
    print(f"{app_config.app_name}: STEP1 receiver notification")
    try:
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent1", "agent3"], app_config)
        sockets_send = [Socket("agent2", "sender" if j == SENDER else f"agent{j}", log_config=app_config.log_config) for j in range(AGENTS - 2)]
        sockets_send.append(Socket("agent2", "agent3", log_config=app_config.log_config))
        sockets_recv = [Socket("sender" if j == SENDER else f"agent{j}", "agent2", log_config=app_config.log_config) for j in range(AGENTS - 2)]
        sockets_recv.append(Socket("agent3", "agent2", log_config=app_config.log_config))
        ys = []
        # Notification
        for step in range(s):
            #(a)
            p = protocol_Notification_a(AGENT2, s, r)
            #(b) (Parity)
            r_gen = protocol_Parity_1(AGENTS, p[AGENT2])
            r_rec = protocol_Parity_2(sockets_send, sockets_recv, r_gen)
            print(f"{app_config.app_name}: 2 done")
            ys.append(protocol_Parity_3_4(r_rec, bcbs))
        #(c)
        rec = 0 if max(ys) == 0 else 1
        #rec = protocol_Notification(AGENT2, s, r, bcbs)
        print(f"{app_config.app_name}: rec={rec}")
        
    except Exception as e:
        print(f"{app_config.app_name} error: {e}")
    #END STEP1
    
    #START STEP2
    print(f"{app_config.app_name}: STEP2 shared GHZ")
    # Create a socket to recv classical information
    socket = Socket("agent2", "sender", log_config=app_config.log_config)
    epr_socket = EPRSocket("sender")
    agent2 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    # teleportation to receive the GHZ qubit
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
    print(f"{app_config.app_name}: m={m}")    
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

