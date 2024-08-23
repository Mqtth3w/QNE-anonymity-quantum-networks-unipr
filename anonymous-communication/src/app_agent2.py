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
            #m = q2.measure()
            #agent2.flush()
            #print(f"{app_config.app_name}: m={m}")    
        #END STEP2
        
            #START STEP3
            print(f"{app_config.app_name}: STEP3 Verification or Anonymous Entanglement.")
            #(a)
            #RandomBit 1.
            xi = 0
            #RandomBit 2. (LogicalOR)
            x = protocol_LogicalOR(xi, s, bcbs, AGENT2)
            #(b)
            if x == 1:
                print(f"{app_config.app_name}: x={x} Anonymous Entanglement.")
                #mm = q2.measure()
                #agent2.flush()
                #print(f"{app_config.app_name}: mm={mm}")
                #1.
                if rec == 0: # the agent isn't the receiver
                    q2.H()
                
            else: # x == 0
                print(f"{app_config.app_name}: x={x} RandomAgent and Verification.")
                
            #END STEP3
    except Exception as e:
        print(f"{app_config.app_name} error: {e}. Agent abort, other agents may also crash.")
    
    return {"0":0}


if __name__ == "__main__": 
    main()

