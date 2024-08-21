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
        for j in range(AGENTS - 1): # receive from all other agents
            print(f"agent3 receive from {j}")
            r_rec.append(int(sockets_recv[j].recv()))
        for j in range(AGENTS - 1): # send to all other agents
            print(f"agent3 send to {j}")
            sockets_send[j].send(str(r_gen[j]))
    except Exception as e:
        print(f"agent3 error: {e}")
    return r_rec

def protocol_Parity_3_4(r_rec: List[int], bcbs: BroadcastChannelBySockets) -> int:
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    z_rec = [zj]
    for i in range(AGENTS - 1):
        z_rec.append(int(bcbs.recv()[1]))
    bcbs.send(str(zj))
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi

def main(app_config=None, s=2, r=2):
    
    #START STEP1
    print(f"{app_config.app_name}: STEP1 receiver notification")
    try:
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent1", "agent2"], app_config)
        sockets_send = [Socket("agent3", "sender" if j == SENDER else f"agent{j}", log_config=app_config.log_config) for j in range(AGENTS - 1)]
        sockets_recv = [Socket("sender" if j == SENDER else f"agent{j}", "agent3", log_config=app_config.log_config) for j in range(AGENTS - 1)]
        ys = []
        # Notification
        for step in range(s):
            #(a)
            p = protocol_Notification_a(AGENT3, s, r)
            #(b) (Parity)
            r_gen = protocol_Parity_1(AGENTS, p[AGENT3])
            r_rec = protocol_Parity_2(sockets_send, sockets_recv, r_gen)
            print(f"{app_config.app_name}: 2 done")
            ys.append(protocol_Parity_3_4(r_rec, bcbs))
        #(c)
        rec = 0 if max(ys) == 0 else 1
        #rec = protocol_Notification(AGENT3, s, r, bcbs)
        print(f"{app_config.app_name}: rec={rec}")
        
    except Exception as e:
        print(f"{app_config.app_name} error: {e}")
    #END STEP1
    
    #START STEP2
    print(f"{app_config.app_name}: STEP2 shared GHZ")
    # Create a socket to recv classical information
    socket = Socket("agent3", "sender", log_config=app_config.log_config)
    epr_socket = EPRSocket("sender")
    agent3 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    # teleportation to receive the GHZ qubit
    with agent3:
        q3 = epr_socket.recv_keep()[0]
        agent3.flush()
        # Get the corrections
        m1, m2 = socket.recv_structured().payload
        if m2 == 1:
            q3.X()
        if m1 == 1:
            q3.Z()
        m = q3.measure()
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

