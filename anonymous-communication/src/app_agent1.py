"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""

from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection, Socket


def main(app_config=None, s=2, r=2):
    
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
        #print(f"`receiver` got corrections: {m1}, {m2}")
        if m2 == 1:
            #print("`receiver` will perform X correction")
            q1.X()
        if m1 == 1:
            #print("`receiver` will perform Z correction")
            q1.Z()
        #agent1.flush()
        m1 = q1.measure()
        
    print(f"agent1: m1={m1}")
    
    return {}


if __name__ == "__main__": 
    main()
