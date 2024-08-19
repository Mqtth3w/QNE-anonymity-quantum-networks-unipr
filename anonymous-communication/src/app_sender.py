"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""

from netqasm.sdk import EPRSocket, Qubit
from netqasm.sdk.classical_communication.message import StructuredMessage
from netqasm.sdk.external import NetQASMConnection, Socket


def qubit_teleportation(dest, q, sender, epr_socket, socket, app_config):
    
    with sender:
        epr = epr_socket.create_keep()[0]
        # Teleport
        q.cnot(epr)
        q.H()
        m1 = q.measure()
        m2 = epr.measure()

    # Send the correction information
    m1, m2 = int(m1), int(m2)
    socket.send_structured(StructuredMessage("Corrections", (m1, m2)))


def main(app_config=None, s=2, r=2):
    
    socket1 = Socket("sender", "agent1", log_config=app_config.log_config)
    epr_socket1 = EPRSocket("agent1")
    
    sender = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket1],
    )
    
    with sender:
        q0 = Qubit(sender)
        q1 = Qubit(sender)
        q2 = Qubit(sender)
        q3 = Qubit(sender)
        #GHZ
        q0.H()
        q0.cnot(q1)
        q1.cnot(q2)
        q2.cnot(q3)
        #m0 = q0.measure()
        #m1 = q1.measure()
        #m2 = q2.measure()
        #m3 = q3.measure()
        #sender.flush()
        #print(f"sender: m0={m0} m1={m1} m2={m2} m3={m3}")
    
        # teleport
        epr1 = epr_socket1.create_keep()[0]
        # Teleport
        q1.cnot(epr1)
        q1.H()
        m11 = q1.measure()
        m12 = epr1.measure()

    # Send the correction information
    m11, m12 = int(m11), int(m12)
    socket1.send_structured(StructuredMessage("Corrections", (m11, m12)))
    #print(f"sender: m0={m0} m1={m1} m2={m2} m3={m3}")
    
    return {}


if __name__ == "__main__": 
    main()
