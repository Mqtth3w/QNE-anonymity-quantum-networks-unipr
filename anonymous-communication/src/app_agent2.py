"""
@author Matteo Gianvenuti https://github.com/mqtth3w
@license GPL-3.0
"""
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection#, Socket
from util import *
import app_agent1

def main(app_config=None, s=2, r=2):
    
    try:
        
        return app_agent1.main \
        ( app_config=app_config
        , s=s
        , r=r
        , agent=AGENT2
        )
        
    except Exception as e:
        print(f"{app_config.app_name} error: {e}. Agent abort, other agents may also crash.")
    

if __name__ == "__main__": 
    main()

