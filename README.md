# Anonymous communication of quantum messages

-%- Work in progress -%- WIP

Project for Quantum Computing: Quantum Network Explorer (QNE) to Simulate Advanced Quantum Security Protocols. In particular, implement the paper "Anonimity for practical quantum networks".

## QNE configuration (Linux)
QNE require Linux or MacOS (up to date)

Create a virtual environment for the project
```bash
python -m venv myenvQNE
```
Activate it
```bash
source myenvQNE/bin/activate
```
Install packeges to build your projects/experiments
- qne-adk
  ```bash
  pip install qne-adk
  ```
- SquidASM based on NetSquid <br>
  first register on https://forum.netsquid.org/
  ```bash
  pip install squidasm --extra-index-url=https://<netsquid-user-name>:<netsquid-password>@pypi.netsquid.org
  ```
## Quick simulation
```bash
cd anonymous-communication/src
```
```bash
netqasm simulate
```
## Creating an experiment
```bash
qne experiment create exp1 anonymous-communication europe
```
```bash
qne experiment run exp1
```
