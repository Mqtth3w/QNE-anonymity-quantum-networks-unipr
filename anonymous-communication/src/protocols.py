"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
import random
from functools import reduce
from netqasm.sdk.external import Socket

SENDER = 0
AGENT1 = 1
AGENT2 = 2
AGENT3 = 3
AGENTS = 4


def protocol_RandomBit():
    """ Protocol 1 of the paper, it is not necessary since here the use choice the receiver """
    pass


def generate_bits_with_xor(n, xi):
    random_bits = [random.randint(0, 1) for _ in range(n-1)]
    current_xor = reduce(lambda x, y: x ^ y, random_bits)
    last_bit = current_xor ^ xi
    random_bits.append(last_bit)
    return random_bits


def protocol_Parity(x: dict, agent: int, app_config=None):
    """ Protocol 6 of the paper """
    #1.
    xi = x[agent]
    r_gen = generate_bits_with_xor(AGENTS, xi)
    print("1 done")
    #2.
    whosend = "sender" if agent == SENDER else f"agent{agent}"
    for j in range(AGENTS):
        if j != agent:
            socket = Socket(whosend, "sender" if j == SENDER else f"agent{agent}", log_config=app_config.log_config)
            socket.send(str(r_gen[j]))
    r_rec = []
    for j in range(AGENTS):
        if j != agent:
            socket = Socket("sender" if j == SENDER else f"agent{agent}", whosend, log_config=app_config.log_config)
            r_rec.append(int(socket.recv()))
    print("2 done")
    #3.
    zj = reduce(lambda x, y: x ^ y, r_rec)
    for j in range(AGENTS):
        if j != agent:
            socket = Socket(whosend, "sender" if j == SENDER else f"agent{agent}", log_config=app_config.log_config)
            socket.send(str(zj))
    z_rec = []
    for j in range(AGENTS):
        if j != agent:
            socket = Socket("sender" if j == SENDER else f"agent{agent}", whosend, log_config=app_config.log_config)
            z_rec.append(int(socket.recv()))
    z_rec.append(zj)
    #4. #z
    yi = reduce(lambda x, y: x ^ y, z_rec)
    return yi
    
            
def protocol_Notification(agent: int, s: int, r: int, app_config=None):
    """ Protocol 2 of the paper """
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
                p[agent] = 0
        # b)
        ys.append(protocol_Parity(p, agent, app_config))
    # c)
    if max(ys) == 0:
        return 0
    return 1


def protocol_Anonymous_Entanglement():
    pass


def protocol_Verification():
    pass


def protocol_LogicalOR():
    pass

