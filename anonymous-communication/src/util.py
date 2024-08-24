"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
import random
import numpy as np
from functools import reduce
from netqasm.sdk.external import Socket
from timeit import default_timer as timer
from typing import List, Optional, Tuple, Type, Union

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

def protocol_Verification_1(j: int, agent: int, bcbs: BroadcastChannelBySockets) -> Union[Tuple[float, int], int]:
    if agent == j: # Verifier
        angles = np.random.uniform(0, np.pi, AGENTS-1)
        partial_sum = np.sum(angles)
        theta_n = (np.ceil(partial_sum / np.pi) * np.pi) - partial_sum
        angles = np.append(angles, theta_n)
        multiple = int(np.sum(angles) // np.pi)
        for i in range(1, AGENTS):
            bcbs.send(str(angles[i]))
        return angles[0], multiple
    else:
        angles = []
        angles.append(float(bcbs.recv()[1]))
        if agent == AGENT3:
            return angles[j]
        return angles[agent]

def parity_bits(b: int, bcbs: BroadcastChannelBySockets, agent: int) -> bool:
    bits = []
    if agent == SENDER:
        bcbs.send(str(b))
        # The sender doesn't need the parity result, only the receiver need it
        for _ in range(3): # Not necessary
            bits.append(int(bcbs.recv()[1]))
    elif agent == AGENT1:
        bits.append(int(bcbs.recv()[1]))
        bcbs.send(str(b))
        for _ in range(2):
            bits.append(int(bcbs.recv()[1]))
    elif agent == AGENT2:
        for _ in range(2):
            bits.append(int(bcbs.recv()[1]))
        bcbs.send(str(b))
        bits.append(int(bcbs.recv()[1]))
    elif agent == AGENT3:
        for _ in range(3):
            bits.append(int(bcbs.recv()[1]))
        bcbs.send(str(b))
    return sum(bits) % 2 == 1

def protocol_LogicalOR(xi: int, s: int, bcbs: BroadcastChannelBySockets, agent: int) -> int:
    """Protocol 7"""
    ys = []
    for order in [0, 1, 2, 3]:
        for _ in range(s):
            #(a)
            p = 0 if xi == 0 else random.choice([0, 1])
            #(b)
            ys.append(protocol_Parity(p, bcbs, agent, order))
    yi = 0 if max(ys) == 0 else 1
    return yi

def protocol_Parity(xi: int, bcbs: BroadcastChannelBySockets, agent: int, order: int = 0) -> int:
    """Protocol 6"""
    orders = {0: [0, 1, 2, 3],
              1: [1, 2, 3, 0],
              2: [2, 3, 0, 1],
              3: [3, 0, 1, 2]}
    #1.
    random.seed(agent)
    r_gen = [random.randint(0, 1) for _ in range(AGENTS-1)]
    current_xor = reduce(lambda x, y: x ^ y, r_gen)
    last_bit = current_xor ^ xi
    r_gen.append(last_bit)
    #2.
    r_rec = [r_gen[agent]]
    if orders[order][agent] == 0:
        for elem in r_gen:
            bcbs.send(str(elem))
        for _ in range(3):
            tmp = []
            for _ in range(4):
                tmp.append(bcbs.recv())
            r_rec.append(int(tmp[agent][1]))
        #3.
        zj = reduce(lambda x, y: x ^ y, r_rec)
        bcbs.send(str(zj))
        z_rec = [zj]
        for _ in range(3):
            z_rec.append(int(bcbs.recv()[1]))
        #4. #z
        yi = reduce(lambda x, y: x ^ y, z_rec)
    elif orders[order][agent] == 1:
        tmp = []
        for _ in range(4):
            tmp.append(bcbs.recv())
        r_rec.append(int(tmp[agent][1]))
        for elem in r_gen:
            bcbs.send(str(elem))
        for _ in range(2):
            tmp = []
            for _ in range(4):
                tmp.append(bcbs.recv())
            r_rec.append(int(tmp[agent][1]))
        #3.
        zj = reduce(lambda x, y: x ^ y, r_rec)
        z_rec = [zj]
        z_rec.append(int(bcbs.recv()[1]))
        bcbs.send(str(zj))
        for _ in range(2):
            z_rec.append(int(bcbs.recv()[1]))
        #4. #z
        yi = reduce(lambda x, y: x ^ y, z_rec)
    elif orders[order][agent] == 2:
        for _ in range(2):
            tmp = []
            for _ in range(4):
                tmp.append(bcbs.recv())
            r_rec.append(int(tmp[agent][1]))
        for elem in r_gen:
            bcbs.send(str(elem))
        tmp = []
        for _ in range(4):
            tmp.append(bcbs.recv())
        r_rec.append(int(tmp[agent][1]))
        #3.
        zj = reduce(lambda x, y: x ^ y, r_rec)
        z_rec = [zj]
        for _ in range(2):
            z_rec.append(int(bcbs.recv()[1]))
        bcbs.send(str(zj))
        z_rec.append(int(bcbs.recv()[1]))
        #4. #z
        yi = reduce(lambda x, y: x ^ y, z_rec)
    elif orders[order][agent] == 3:
        for _ in range(3):
            tmp = []
            for _ in range(4):
                tmp.append(bcbs.recv())
            r_rec.append(int(tmp[agent][1]))
        for elem in r_gen:
            bcbs.send(str(elem))
        #3.
        zj = reduce(lambda x, y: x ^ y, r_rec)
        z_rec = [zj]
        for _ in range(3):
            z_rec.append(int(bcbs.recv()[1]))
        bcbs.send(str(zj))
        #4. #z
        yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi
    
def protocol_Notification(s: int, r: int, bcbs: BroadcastChannelBySockets, agent: int) -> int:
    """Protocol 2"""
    p = [0, 0, 0, 0]
    ys = []
    for _ in range(s): # c)
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
        ys.append(protocol_Parity(p[agent], bcbs, agent))
    # c)
    if max(ys) == 0:
        return 0
    return 1

