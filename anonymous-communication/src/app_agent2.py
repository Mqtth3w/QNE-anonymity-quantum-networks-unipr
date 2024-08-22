"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection#, Socket
from util import *
'''
def protocol_Parity_2(r_gen: List[int], bcbs: BroadcastChannelBySockets) -> List[int]:
    r_rec = [r_gen[AGENT2]]
    try:
        
        for i in range(2):
            tmp = []
            for j in range(4):
                tmp.append(bcbs.recv())
            r_rec.append(int(tmp[AGENT2][1]))
        
        for elem in r_gen:
            bcbs.send(str(elem))
        
        tmp = []
        for j in range(4):
            tmp.append(bcbs.recv())
        r_rec.append(int(tmp[AGENT2][1]))
        
        
        #print(f"agent2 r_gen: {r_gen}")
        #for i in range(2):
        #    tmp = bcbs.recv()[1]
        #    print(f"agent2 tmp: {tmp}")
        #    r_rec.append(int(tmp[AGENT2]))
        #st = ''.join(str(bit) for bit in r_gen)
        #print(f"agent2 st: {st}")
        #bcbs.send(st)
        #tmp = bcbs.recv()[1]
        #print(f"agent2 tmp: {tmp}")
        #r_rec.append(int(tmp[AGENT2]))
        
    except Exception as e:
        print(f"agent2 error: {e}")
    return r_rec

def protocol_Parity_3_4(r_rec: List[int], bcbs: BroadcastChannelBySockets) -> int:
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    z_rec = [zj]
    for i in range(2):
        z_rec.append(int(bcbs.recv()[1]))
    bcbs.send(str(zj))
    z_rec.append(int(bcbs.recv()[1]))
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi
'''

def main(app_config=None, s=2, r=2):
    
    #START STEP1
    print(f"{app_config.app_name}: STEP1 receiver notification s={s} r={r}")
    try:
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent1", "agent3"], app_config)
        ys = []
        # Notification
        for step in range(s):
            #(a)
            p = protocol_Notification_a(AGENT2, r)
            #(b) (Parity)
            #r_gen = protocol_Parity_1(AGENTS, p[AGENT2])
            #r_rec = protocol_Parity_2(r_gen, bcbs)
            #ys.append(protocol_Parity_3_4(r_rec, bcbs))
            ys.append(protocol_Parity(p[AGENT2], bcbs, AGENT2))
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
    print(f"{app_config.app_name}: STEP3 Verification or Anonymous Entanglement")
    #(a)
    #RandomBit 1.
    xi = 0
    #RandomBit 2. (LogicalOR)
    x = protocol_LogicalOR(xi, s, bcbs, AGENT2)
    print(f"{app_config.app_name}: x={x}")
    #END STEP3
    
    
    return {"0":0}


if __name__ == "__main__": 
    main()

