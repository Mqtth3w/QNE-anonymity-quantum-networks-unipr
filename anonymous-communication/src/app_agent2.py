"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection#, Socket
from util import *

def main(app_config=None, s=2, r=2):
    
    try:
        #START STEP1
        print(f"{app_config.app_name}: STEP1 receiver notification s={s} r={r}.")
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent1", "agent3"], app_config)
        rec = protocol_Notification(s, r, bcbs, AGENT2)
        print(f"{app_config.app_name}: rec={rec}.")
        #END STEP1
    
        #START STEP2
        print(f"{app_config.app_name}: STEP2 shared GHZ.")
        # Create a socket to recv classical information
        socket = Socket("agent2", "sender", log_config=app_config.log_config)
        epr_socket = EPRSocket("sender")
        agent2 = NetQASMConnection(
            app_name=app_config.app_name,
            log_config=app_config.log_config,
            epr_sockets=[epr_socket],
        )
        # Teleportation to receive the shared GHZ qubit
        with agent2:
            valid = True
            while valid: # If the Verification (STEP3-b-i-ii) is successful, it is necessary restart from STEP2
                print(f"{app_config.app_name}: STEP2 shared GHZ.")
                valid = False
                q2 = epr_socket.recv_keep()[0]
                agent2.flush()
                # Get the corrections
                m1, m2 = socket.recv_structured().payload
                if m2 == 1:
                    q2.X()
                if m1 == 1:
                    q2.Z()    
        #END STEP2
            
                #START STEP3
                print(f"{app_config.app_name}: STEP3 Verification or Anonymous Entanglement.")
                #(a)
                #RandomBit 1.
                xi = 0
                #RandomBit 2. (LogicalOR)
                x = protocol_LogicalOR(xi, s, bcbs, AGENT2)
                #(b)
                #rec = 1 # Just to test
                #x = 0
                if x == 1:
                    print(f"{app_config.app_name}: x={x} Anonymous Entanglement.")
                    #1.
                    if rec == 0: # The agent isn't the receiver
                        q2.H()
                        b = q2.measure()
                        agent2.flush()
                        parity_bits(b, bcbs, AGENT2)
                    else: # rec == 1 so the agent is the receiver
                        #2. 3.
                        b = random.choice([0, 1])
                        p = parity_bits(b, bcbs, AGENT2)
                        if p:
                            q2.Z()
                        print(f"{app_config.app_name}: Share an anonymous entanglement with the sender. It can be used to teleport a generic quantum state.")
                else: # x == 0
                    print(f"{app_config.app_name}: x={x} RandomAgent and Verification.")
                    #(i)
                    j = int(bcbs.recv()[1])
                    #(ii) #Verification
                    if j == AGENT2: # Verifier
                        print(f"{app_config.app_name}: I'm the verifier.")
                        theta, multiple = protocol_Verification_1(j, AGENT2, bcbs)
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
                        theta = protocol_Verification_1(j, AGENT2, bcbs)
                        #2. 
                        q2.rot_Y(angle=2*theta)
                        m = q2.measure()
                        agent2.flush()
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

