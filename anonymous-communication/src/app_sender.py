"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from netqasm.sdk import EPRSocket, Qubit
from netqasm.sdk.external import NetQASMConnection#, Socket
from netqasm.sdk.classical_communication.message import StructuredMessage
from util import *

def distribution_D(s: int):
    coins = []
    for i in range(s):
        coins.append(random.choice([0, 1]))
    if max(coins) == 0:
        return 0
    return 1

def protocol_Parity_2(r_gen: List[int], bcbs: BroadcastChannelBySockets) -> List[int]:
    r_rec = [r_gen[SENDER]]
    try:
        #r_gen.pop(SENDER)
        for elem in r_gen:
            bcbs.send(str(elem))
        
        for i in range(3):
            tmp = []
            for j in range(4):
                tmp.append(bcbs.recv())
            r_rec.append(int(tmp[SENDER][1]))
            
        
        '''
        print(f"agent0 r_gen: {r_gen}")
        st = ''.join(str(bit) for bit in r_gen)
        print(f"agent0 st: {st}")
        bcbs.send(st)
        for i in range(3):
            tmp = bcbs.recv()[1]
            print(f"agent0 tmp: {tmp}")
            r_rec.append(int(tmp[SENDER]))
        '''
    except Exception as e:
        print(f"sender error: {e}")
    return r_rec

def protocol_Parity_3_4(r_rec: List[int], bcbs: BroadcastChannelBySockets) -> int:
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    bcbs.send(str(zj))
    z_rec = [zj]
    for i in range(3):
        z_rec.append(int(bcbs.recv()[1]))
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi


def main(app_config=None, s=6, r=2):
    
    #START STEP1
    print(f"{app_config.app_name}: STEP1 receiver notification s={s} r={r}")
    try:
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["agent1", "agent2", "agent3"], app_config)
        ys = []
        # Notification
        for step in range(s):
            #(a)
            p = protocol_Notification_a(SENDER, s, r)
            #(b) (Parity)
            r_gen = protocol_Parity_1(AGENTS, p[SENDER])
            r_rec = protocol_Parity_2(r_gen, bcbs)
            ys.append(protocol_Parity_3_4(r_rec, bcbs))
        #(c)
        rec = 0 if max(ys) == 0 else 1
        #rec = protocol_Notification(SENDER, s, r, bcbs)
        print(f"{app_config.app_name}: rec={rec}")
        
    except Exception as e:
        print(f"{app_config.app_name} error: {e}")
    #END STEP1
    
    #START STEP2
    print(f"{app_config.app_name}: STEP2 shared GHZ")
    sockets = [Socket("sender", a, log_config=app_config.log_config) for a in ["agent1", "agent2", "agent3"]]
    epr_sockets = [EPRSocket(a) for a in ["agent1", "agent2", "agent3"]]
    sender = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=epr_sockets,
    )
    with sender: # This orrible library disallow generalization
        q0 = Qubit(sender)
        q1 = Qubit(sender)
        q2 = Qubit(sender)
        q3 = Qubit(sender)
        #GHZ
        q0.H()
        q0.cnot(q1)
        q1.cnot(q2)
        q2.cnot(q3)
        # teleport q1
        epr1 = epr_sockets[0].create_keep()[0]
        q1.cnot(epr1)
        q1.H()
        m11 = q1.measure()
        m12 = epr1.measure()
        # teleport q2
        epr2 = epr_sockets[1].create_keep()[0]
        q2.cnot(epr2)
        q2.H()
        m21 = q2.measure()
        m22 = epr2.measure()
        # teleport q3
        epr3 = epr_sockets[2].create_keep()[0]
        q3.cnot(epr3)
        q3.H()
        m31 = q3.measure()
        m32 = epr3.measure()
        # measure 
        m = q0.measure()
    
    print(f"{app_config.app_name}: m={m}")
    # Send the correction information
    m11, m12 = int(m11), int(m12)
    sockets[0].send_structured(StructuredMessage("Corrections", (m11, m12)))
    m21, m22 = int(m21), int(m22)
    sockets[1].send_structured(StructuredMessage("Corrections", (m21, m22)))
    m31, m32 = int(m21), int(m32)
    sockets[2].send_structured(StructuredMessage("Corrections", (m31, m32)))
    #END STEP2
    
    
    #START STEP3
    #(a)
    #RandomBit 1.
    xi = distribution_D(s)
    #RandomBit 2. (LogicalOR)
    print(f"xi={xi}")
    #END STEP3
    
    
    return {"0":0}


if __name__ == "__main__": 
    main()