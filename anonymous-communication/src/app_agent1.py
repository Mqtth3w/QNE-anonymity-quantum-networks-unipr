"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection#, Socket
from util import *

def main(app_config=None, s=2, r=2, agent=AGENT1):
    
    try:
        #START STEP1
        targets = ["sender"]
        for i in range(1, 4):
            if i != agent:
                targets.append(f"agent{i}")
        
        print(f"{app_config.app_name}: STEP1 receiver notification s={s} r={r}.")
        bcbs = BroadcastChannelBySockets(app_config.app_name, targets, app_config)
        rec = protocol_Notification(s, r, bcbs, agent)
        print(f"{app_config.app_name}: rec={rec}.")
        #END STEP1
        
        #START STEP2
        print(f"{app_config.app_name}: STEP2 shared GHZ.")
        # Create a socket to recv classical information
        socket = Socket(f"agent{agent}", "sender", log_config=app_config.log_config)
        epr_socket = EPRSocket("sender")
        agent_conn = NetQASMConnection(
            app_name=app_config.app_name,
            log_config=app_config.log_config,
            epr_sockets=[epr_socket],
        )
        # Teleportation to receive the shared GHZ qubit
        with agent_conn:
            valid = True
            while valid: # If the Verification (STEP3-b-i-ii) is successful, it is necessary restart from STEP2
                print(f"{app_config.app_name}: STEP2 shared GHZ.")
                valid = False
                q1 = epr_socket.recv_keep()[0]
                agent_conn.flush()
                # Get the corrections
                m1, m2 = socket.recv_structured().payload
                if m2 == 1:
                    q1.X()
                if m1 == 1:
                    q1.Z()
        #END STEP2
            
                #START STEP3
                print(f"{app_config.app_name}: STEP3 Verification or Anonymous Entanglement.")
                #(a)
                #RandomBit 1.
                xi = 0
                #RandomBit 2. (LogicalOR)
                x = protocol_LogicalOR(xi, s, bcbs, agent)
                #(b)
                #rec = 0 # Just to test
                #x = 0
                if x == 0:
                    print(f"{app_config.app_name}: x={x} Anonymous Entanglement.")
                    #1.
                    if rec == 0: # The agent isn't the receiver
                        q1.H()
                        b = q1.measure()
                        agent_conn.flush()
                        parity_bits(b, bcbs, agent)              
                    else: # rec == 1 so the agent is the receiver
                        #2. 3.
                        b = random.choice([0, 1])
                        p = parity_bits(b, bcbs, agent)
                        if p:
                            q1.Z()
                        print(f"{app_config.app_name}: Share an anonymous entanglement with the sender. It can be used to teleport a generic quantum state.")
                else: # x == 1
                    print(f"{app_config.app_name}: x={x} RandomAgent and Verification.")
                    #(i)
                    j = int(bcbs.recv()[1])
                    #(ii) #Verification
                    if j == agent: # Verifier
                        print(f"{app_config.app_name}: I'm the verifier.")
                        theta, multiple = protocol_Verification_1(j, agent, bcbs)
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
                        theta = protocol_Verification_1(j, agent, bcbs)
                        #2. 
                        q1.rot_Y(angle=2*theta)
                        m = q1.measure()
                        agent_conn.flush()
                        bcbs.send(str(m))
                        bcbs.recv() # Clean the broadcast from other agents
                        bcbs.recv() 
                        #3. # Receive the verifier decision
                        v = bcbs.recv()[1]
                        valid = v == "1"
                #END STEP3
    except Exception as e:
        print(f"{app_config.app_name} error: {e}. Agent abort, other agents may also crash.")
    
    return {"is_receiver": rec,
            "x_decision": x,
            "verifier_index": j,
            "valid_GHZ": valid}


if __name__ == "__main__": 
    main()
