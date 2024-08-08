from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection

def main(app_config=None, x=0, y=0):
    # Put your code here
    
    # Specify an EPR socket to alice
    epr_socket = EPRSocket("alice")

    bob = NetQASMConnection(
        app_name=app_config.app_name, #"bob", 
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    with bob:
        # Receive an entangled pair using the EPR socket to alice
        q_ent = epr_socket.recv_keep()[0] # .recv_keep() maintain it in memory, .recv() don't and it is deprecated
        # Measure the qubit
        bob.flush() #ensure previous commands are executed, it is done automatically when you go out of the scope
        m = q_ent.measure()
        
    m = int(m)
    # Print the outcome
    print(f"bob's outcome is: {m}")
    
    return {"Bob": m}


if __name__ == "__main__": 
    main()
