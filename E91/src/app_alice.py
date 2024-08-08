from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection

def main(app_config=None, x=0, y=0):
    # Put your code here
    
    # Specify an EPR socket to bob
    epr_socket = EPRSocket("bob")

    alice = NetQASMConnection(
        app_name=app_config.app_name, #"alice",
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )
    with alice:
        # Create an entangled pair using the EPR socket to bob
        q_ent = epr_socket.create_keep()[0] # .create_keep() maintain it in memory, .create() don't and it is deprecated
        # Measure the qubit
        alice.flush() #ensure previous commands are executed, it is done automatically when you go out of the scope
        m = q_ent.measure()
    
    m = int(m)
    # Print the outcome
    print(f"alice's outcome is: {m}")
    
    return {"Alice": m}


if __name__ == "__main__": 
    main()
