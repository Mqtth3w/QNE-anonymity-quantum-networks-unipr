"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from protocols import *
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection


def main(app_config=None, s=4, r=2):
    # Put your code here
    
    yi = protocol_Notification(AGENT2, s, r, app_config)
    print(f"Agent2 Yi = {yi}")
    
    return {}


if __name__ == "__main__": 
    main()

