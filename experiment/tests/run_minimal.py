import sys
import os

# Adiciona a raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from experiment.utils.tools import Detector

# Carregar contrato
with open("test_contract.sol", "r") as f:
    code = f.read()

# Prompt simples
prompt = (
    "Analyze the following Solidity smart contract for vulnerabilities. "
    "Return a JSON with keys 'vulnerable' (true/false), 'vulnerabilities' (list), "
    "and 'explanation' (string):\n\n"
    f"{code}"
)

# Detecção
detector = Detector()
result = detector.detect(prompt)

# Exibir resultado
print("\n=== Resultado da Detecção ===")
print(result)
