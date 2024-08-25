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

def main(app_config=None, s=2, r=2):
    
    try:
        #START STEP1
        print(f"{app_config.app_name}: STEP1 receiver notification s={s} r={r}.")
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["agent1", "agent2", "agent3"], app_config)
        rec = protocol_Notification(s, r, bcbs, SENDER)
        print(f"{app_config.app_name}: rec={rec}.")
        #END STEP1
        
        #START STEP2
        sockets = [Socket("sender", a, log_config=app_config.log_config) for a in ["agent1", "agent2", "agent3"]]
        epr_sockets = [EPRSocket(a) for a in ["agent1", "agent2", "agent3"]]
        sender = NetQASMConnection(
            app_name=app_config.app_name,
            log_config=app_config.log_config,
            epr_sockets=epr_sockets,
        )
        # Create and share the GHZ
        with sender: # This orrible library disallow generalization
            valid = True
            while valid: # If the Verification (STEP3-b-i-ii) is successful, it is necessary restart from STEP2
                print(f"{app_config.app_name}: STEP2 shared GHZ.")
                valid = False
                q0 = Qubit(sender)
                q1 = Qubit(sender)
                q2 = Qubit(sender)
                q3 = Qubit(sender)
                #GHZ
                q0.H()
                q0.cnot(q1)
                q1.cnot(q2)
                q2.cnot(q3)
                # Teleport q1 to agent1
                epr1 = epr_sockets[0].create_keep()[0]
                q1.cnot(epr1)
                q1.H()
                m11 = q1.measure()
                m12 = epr1.measure()
                # Teleport q2 to agent2
                epr2 = epr_sockets[1].create_keep()[0]
                q2.cnot(epr2)
                q2.H()
                m21 = q2.measure()
                m22 = epr2.measure()
                # Teleport q3 to agent3
                epr3 = epr_sockets[2].create_keep()[0]
                q3.cnot(epr3)
                q3.H()
                m31 = q3.measure()
                m32 = epr3.measure()
                sender.flush()
                # Send the correction information
                m11, m12 = int(m11), int(m12)
                sockets[0].send_structured(StructuredMessage("Corrections", (m11, m12)))
                m21, m22 = int(m21), int(m22)
                sockets[1].send_structured(StructuredMessage("Corrections", (m21, m22)))
                m31, m32 = int(m21), int(m32)
                sockets[2].send_structured(StructuredMessage("Corrections", (m31, m32)))
        #END STEP2
                
                #START STEP3
                print(f"{app_config.app_name}: STEP3 Verification or Anonymous Entanglement.")
                #(a)
                #RandomBit 1.
                xi = distribution_D(s)
                #RandomBit 2. (LogicalOR)
                x = protocol_LogicalOR(xi, s, bcbs, SENDER)
                #(b)
                #x = 0 # Just to test
                if x == 1:
                    print(f"{app_config.app_name}: x={x} Anonymous Entanglement.")
                    #1.
                    #2. 3.
                    b = random.choice([0, 1])
                    parity_bits(b, bcbs, SENDER)
                    if b == 1:
                        q0.Z()
                    print(f"{app_config.app_name}: Share an anonymous entanglement with the receiver. It can be used to teleport a generic quantum state.")
                else: # x == 0
                    print(f"{app_config.app_name}: x={x} RandomAgent and Verification.")
                    #(i) #RandomAgent
                    js = []
                    for _ in range(2): # log2(n) = 2, with n = AGENTS = 4
                        #RandomBit (private) # Since other agents insert xi=0, the distribution D is always the result
                        js.append(str(distribution_D(s)))
                    j = int(''.join(js), 2)
                    print(f"{app_config.app_name}: j={j}.")
                    bcbs.send(str(j))
                    #(ii) #Verification
                    if j == SENDER: # Verifier
                        print(f"{app_config.app_name}: I'm the verifier.")
                        theta, multiple = protocol_Verification_1(j, SENDER, bcbs)
                        #2.
                        yjs = [] # Measures
                        for _ in range(AGENTS-1):
                            yjs.append(int(bcbs.recv()[1]))
                        #3.
                        valid = reduce(lambda x, y: x ^ y, yjs) == (multiple % 2)
                        print(f"{app_config.app_name}: valid={valid}.")
                        if valid:
                            bcbs.send("1")
                        else:
                            bcbs.send("0")
                    else:
                        theta = protocol_Verification_1(j, SENDER, bcbs)
                        #2.
                        q0.rot_Y(angle=2*theta)
                        m = q0.measure()
                        sender.flush()
                        bcbs.send(str(m))
                        bcbs.recv() # Clean the broadcast from other agents
                        bcbs.recv() 
                        #3. # Receive the verifier decision
                        v = bcbs.recv()[1]
                        valid = v == "1"
                #END STEP3
    except Exception as e:
        print(f"{app_config.app_name} error: {e}. Agent abort, other agents may also crash.")
    
    return {"0":0}


if __name__ == "__main__": 
    main()