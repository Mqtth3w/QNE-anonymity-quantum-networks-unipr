"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
import random
from functools import reduce
from netqasm.sdk.external import Socket
from timeit import default_timer as timer
from typing import List, Optional, Tuple, Type

SENDER = 0
AGENT1 = 1
AGENT2 = 2
AGENT3 = 3
AGENTS = 4

class BroadcastChannelBySockets():
    """Implementation of a broadcast using a Socket for each remote node.

    Technically this is a multicast channel since the receiving nodes must be
    explicitly listed. It simply uses one-to-one sockets for every remote node.
    """
    def __init__(self, app_name: str, remote_app_names: List[str], app_config=None):
        """BroadcastChannel constructor.

        :param app_name: application/Host name of self
        :param remote_app_names: list of receiving remote Hosts
        :param app_config: app_config of app_name 
        """
        self._app_name = app_name
        self._app_config = app_config
        self._sockets = {
            remote_app_name: self._socket_class(
                app_name=app_name, remote_app_name=remote_app_name, app_config=app_config
            )
            for remote_app_name in remote_app_names
        }
    
    def _socket_class(self, app_name: str, remote_app_name: str, app_config=None) -> Type[Socket]:
        """Create one-to-one socket between app_name and remote_app_name."""
        return Socket(app_name, remote_app_name, log_config=app_config.log_config if app_config else None)
    
    def get_app_config(self):
        """Return the self._app_config"""
        return self._app_config
    
    def send(self, msg: str) -> None:
        """Broadcast a message to all remote nodes."""
        for socket in self._sockets.values():
            socket.send(msg=msg)

    def recv(
        self, block: bool = True, timeout: Optional[float] = None
    ) -> Tuple[str, str]:
        """Receive a message that was broadcast.

        Parameters
        ----------
        block : bool
            Whether to block for an available message
        timeout : float, optional
            Optionally use a timeout for trying to recv a message. Only used if `block=True`.

        Returns
        -------
        tuple
            (remote_node_name, msg)

        Raises
        ------
        RuntimeError
            If `block=False` and there is no available message
        """
        t_start = timer()
        while block:
            for remote_node_name, socket in self._sockets.items():
                try:
                    msg = socket.recv(block=False)
                except RuntimeError:
                    continue
                else:
                    return remote_node_name, msg
            if block and timeout is not None:
                t_now = timer()
                t_elapsed = t_now - t_start
                if t_elapsed > timeout:
                    raise TimeoutError(
                        "Timeout while trying to receive broadcasted message"
                    )
        raise RuntimeError("No message broadcasted")

def protocol_Anonymous_Entanglement():
    pass

def protocol_Verification():
    pass

def protocol_LogicalOR():
    pass

def protocol_Parity_1(n: int, xi: int) ->  List[int]: #  generate_bits_with_xor
    random_bits = [random.randint(0, 1) for _ in range(n-1)]
    current_xor = reduce(lambda x, y: x ^ y, random_bits)
    last_bit = current_xor ^ xi
    random_bits.append(last_bit)
    return random_bits

'''
def protocol_Parity_3_4(r_rec: List[int], bcbs: BroadcastChannelBySockets) -> int:
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    bcbs.send(str(zj))
    print("3 done")
    z_rec = [zj]
    for i in range(AGENTS):
        z_rec.append(int(bcbs.recv()[1]))
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi
'''

def protocol_Notification_a(agent: int, s: int, r: int) -> dict:
    """Step (a) of protocol 2"""
    p = {0: 0, 1: 0, 2: 0, 3: 0}
    for j in range(AGENTS):
        if j != agent:
            if agent == r and j == SENDER:
                p[j] = random.choice([0, 1])
            else:
                p[j] = 0
        else:
            p[j] = 0
    return p

'''
def protocol_Parity(xi: int, agent: int, bcbs: BroadcastChannelBySockets) -> int:
    """Protocol 6"""
    #1.
    r_gen = generate_bits_with_xor(AGENTS, xi)
    print("1 done")
    #2.
    r_rec = []
    log_config = bcbs.get_app_config().log_config
    sockets_send = []
    sockets_recv = []
    if agent == AGENT1:
        print("1111111")
        sockets_recv.append(Socket("sender", "agent1", log_config=log_config))
        r_rec.append(int(sockets_recv[-1].recv()))
        print("1111111")
        for j in range(AGENTS):
            if j != agent:
                sockets_send.append(Socket("agent1", "sender" if j == SENDER else f"agent{j}", log_config=log_config))
                sockets_send[-1].send(str(r_gen[j]))
        for j in range(2, AGENTS):
            print("1111111")
            sockets_recv.append(Socket(f"agent{j}", "agent1", log_config=log_config))
            r_rec.append(int(sockets_recv[-1].recv()))
    elif agent == AGENT2:
        print("222222")
        for j in range(AGENTS - 2):
            print("222222")
            sockets_recv.append(Socket("sender" if j == SENDER else f"agent{j}", "agent2", log_config=log_config))
            r_rec.append(int(sockets_recv[-1].recv()))
        for j in range(AGENTS):
            if j != agent:
                sockets_send.append(Socket("agent2", "sender" if j == SENDER else f"agent{j}", log_config=log_config))
                sockets_send[-1].send(str(r_gen[j]))
        sockets_recv.append(Socket("agent3", "agent2", log_config=log_config))
        r_rec.append(int(sockets_recv[-1].recv()))
    elif agent == AGENT3:
        print("33333")
        for j in range(AGENTS - 1):
            print("33333")
            sockets_recv.append(Socket("sender" if j == SENDER else f"agent{j}", "agent3", log_config=log_config))
            r_rec.append(int(sockets_recv[-1].recv()))
        for j in range(AGENTS - 1):
            sockets_send.append(Socket("agent3", "sender" if j == SENDER else f"agent{j}", log_config=log_config))
            sockets_send[-1].send(str(r_gen[j]))
    elif agent == SENDER:
        print("000000")
        for j in range(1, AGENTS):
            sockets_send.append(Socket("sender", f"agent{j}", log_config=log_config))
            sockets_send[-1].send(str(r_gen[j]))
        for j in range(1, AGENTS):
            sockets_recv.append(Socket(f"agent{j}", "sender", log_config=log_config))
            r_rec.append(int(sockets_recv[-1].recv()))
            
    print("2 done")
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    bcbs.send(str(zj))
    print("3 done")
    z_rec = [zj]
    for i in range(AGENTS):
        z_rec.append(int(bcbs.recv()[1]))
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi
    
    
def protocol_Notification(agent: int, s: int, r: int, bcbs: BroadcastChannelBySockets) -> int:
    """Protocol 2"""
    p = {0: 0, 1: 0, 2: 0, 3: 0}
    ys = []
    for step in range(s): # c)
        print(f"agent {agent} step {step}")
        # a)
        for j in range(AGENTS):
            if j != agent:
                if agent == r and j == SENDER:
                    p[j] = random.choice([0, 1])
                else:
                    p[j] = 0
            else:
                p[j] = 0
        # b)
        ys.append(protocol_Parity(p[agent], agent, bcbs))
    # c)
    if max(ys) == 0:
        return 0
    return 1
'''


'''
        qubits = [Qubit(sender) for i in range(4)]
        #GHZ
        qubits[0].H()
        qubits[0].cnot(qubits[1])
        qubits[1].cnot(qubits[2])
        qubits[2].cnot(qubits[3])
        # Teleport qubits 1, 2, 3 to the agents
        eprs = [epr_sockets[i].create_keep()[0] for i in range(3)]
        #sender.flush()
        ms = []
        for i in range(1, 4):
            qubits[i].cnot(eprs[i - 1])
            qubits[i].H()
            m1 = qubits[i].measure()
            m2 = eprs[i - 1].measure()
            sender.flush()
            m1, m2 = int(m1), int(m2)
            sockets[i - 1].send_structured(StructuredMessage("Corrections", (m1, m2)))

'''
