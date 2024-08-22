"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection#, Socket
from util import *

def protocol_Parity_2(r_gen: List[int], bcbs: BroadcastChannelBySockets) -> List[int]:
    r_rec = [r_gen[AGENT1]]
    try:
        print(f"agent1 r_gen: {r_gen}")
        tmp = bcbs.recv()[1]
        print(f"agent1 tmp: {tmp}")
        r_rec.append(int(tmp[AGENT1]))
        st = ''.join(str(bit) for bit in r_gen)
        print(f"agent1 st: {st}")
        bcbs.send(st)
        for i in range(2):
            tmp = bcbs.recv()[1]
            print(f"agent1 tmp: {tmp}")
            r_rec.append(int(tmp[AGENT1]))
    except Exception as e:
        print(f"agent1 error: {e}")
    return r_rec

def protocol_Parity_3_4(r_rec: List[int], bcbs: BroadcastChannelBySockets) -> int:
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    z_rec = [zj]
    z_rec.append(int(bcbs.recv()[1]))
    bcbs.send(str(zj))
    for i in range(2):
        z_rec.append(int(bcbs.recv()[1]))
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi

def main(app_config=None, s=2, r=2):
    
    #START STEP1
    print(f"{app_config.app_name}: STEP1 receiver notification")
    try:
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent2", "agent3"], app_config)
        ys = []
        # Notification
        for step in range(s):
            #(a)
            p = protocol_Notification_a(AGENT1, s, r)
            #(b) (Parity)
            r_gen = protocol_Parity_1(AGENTS, p[AGENT1])
            r_rec = protocol_Parity_2(r_gen, bcbs)
            ys.append(protocol_Parity_3_4(r_rec, bcbs))
        #(c)
        rec = 0 if max(ys) == 0 else 1
        #rec = protocol_Notification(AGENT1, s, r, bcbs)
        print(f"{app_config.app_name}: rec={rec}")
        
    except Exception as e:
        print(f"{app_config.app_name} error: {e}")
    #END STEP1
    
    #START STEP2
    print(f"{app_config.app_name}: STEP2 shared GHZ")
    # Create a socket to recv classical information
    socket = Socket("agent1", "sender", log_config=app_config.log_config)
    epr_socket = EPRSocket("sender")
    agent1 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    # teleportation to receive the GHZ qubit
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
