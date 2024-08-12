"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
import random


SENDER = 0
AGENT1 = 1
AGENT2 = 2
AGENT3 = 3
AGENTS = 4


def protocol_RandomBit():
    """ Protocol 1 of the paper, it is not necessary since here the use choice the receiver """
    pass


def protocol_Parity(x: dict):
    """ Protocol 6 of the paper """
    #1
    pass


def protocol_Notification(agent: int, s: int, r: int):
    """ Protocol 2 of the paper """
    p = {0: 0, 1: 0, 2: 0, 3: 0}
    for step in range(s): # c)
        # a)
        for j in range(AGENTS):
            if j != agent:
                if i = r and j = SENDER:
                    p[j] = random.choice([0, 1])
                else
                    p[j] = 0
            else:
                p[agent] = 0
        # b)
        protocol_Parity(p)
            


def protocol_Anonymous_Entanglement():
    pass


def protocol_Verification():
    pass


def protocol_LogicalOR():
    pass

