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
        bcbs = BroadcastChannelBySockets(app_config.app_name, ["sender", "agent1", "agent2"], app_config)
        rec = protocol_Notification(s, r, bcbs, AGENT3)
        print(f"{app_config.app_name}: rec={rec}.")
        #END STEP1
    
        #START STEP2
        print(f"{app_config.app_name}: STEP2 shared GHZ.")
        # Create a socket to recv classical information
        socket = Socket("agent3", "sender", log_config=app_config.log_config)
        epr_socket = EPRSocket("sender")
        agent3 = NetQASMConnection(
            app_name=app_config.app_name,
            log_config=app_config.log_config,
            epr_sockets=[epr_socket],
        )
        # Teleportation to receive the shared GHZ qubit
        with agent3:
            q3 = epr_socket.recv_keep()[0]
            agent3.flush()
            # Get the corrections
            m1, m2 = socket.recv_structured().payload
            if m2 == 1:
                q3.X()
            if m1 == 1:
                q3.Z()
        #END STEP2
        
            #START STEP3
            print(f"{app_config.app_name}: STEP3 Verification or Anonymous Entanglement.")
            #(a)
            #RandomBit 1.
            xi = 0
            #RandomBit 2. (LogicalOR)
            x = protocol_LogicalOR(xi, s, bcbs, AGENT3)
            #(b)
            rec = 0 # just for test
            x = 1
            if x == 1:
                print(f"{app_config.app_name}: x={x} Anonymous Entanglement.")
                #1.
                if rec == 0: # the agent isn't the receiver
                    q3.H()
                    b = q3.measure()
                    agent3.flush()
                    parity_bits(b, bcbs, AGENT3)
                else: # rec == 1 so the agent is the receiver
                    #2.
                    b = random.choice([0, 1])
                    p = parity_bits(b, bcbs, AGENT3)
                    if p:
                        q3.Z()
                    print(f"{app_config.app_name}: Share an anonymous entanglement with the sender. It can be used to teleport a generic quantum state.")
            else: # x == 0
                print(f"{app_config.app_name}: x={x} RandomAgent and Verification.")
                
            #END STEP3
    except Exception as e:
        print(f"{app_config.app_name} error: {e}. Agent abort, other agents may also crash.")
    
    return {"0":0}


if __name__ == "__main__": 
    main()

