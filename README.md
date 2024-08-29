# Anonymous communication of quantum messages

Project for Quantum Computing: Quantum Network Explorer (QNE) to Simulate Advanced Quantum Security Protocols. In particular, implement the paper ["Anonimity for practical quantum networks"](./Anonymity_for_practical_quantum_networks(paper).pdf).
This application consists of the establishment of anonymous entanglement between a sender and a receiver in a quantum network with multiple agents. This entanglement can subsequently be used to share any arbitrary quantum state through quantum teleportation.

## Documentation
[project documentation](./project-documentation.pdf)

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
## Simulation
```bash
cd myenvQNE/anonymous-communication/src
```
```bash
netqasm simulate
```
## Creating an experiment
You cannot run it with the following classical way because this application requires more qubits than the experiment mode provides.
```bash
cd myenvQNE
```
```bash
qne experiment create exp1 anonymous-communication europe
```
```bash
qne experiment run exp1
```
