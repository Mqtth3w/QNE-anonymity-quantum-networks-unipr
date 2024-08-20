"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""

from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection, Socket


def main(app_config=None, s=2, r=2):
    
    # Create a socket to recv classical information
    socket = Socket("agent3", "sender", log_config=app_config.log_config)
    epr_socket = EPRSocket("sender")
    agent3 = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    # teleportation to receive the GHZ qubit
    try:
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
            
    except Exception as e:
        print(f"agent3 error: {e}")
    print(f"agent3: m={m}")
    
    return {"0":0}


if __name__ == "__main__": 
    main()

