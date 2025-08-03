import sys
import os
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from experiment.utils.tools import Detector

def analyze_contract(contract_file):
    # Load contract
    with open(contract_file, "r") as f:
        code = f.read()

    prompt = f"""
    Analyze the following Solidity smart contract code for security issues.
    Return the response strictly as a JSON object with the following keys:

    - "vulnerable" (boolean): true if any vulnerabilities are found, otherwise false.
    - "vulnerabilities" (array): a list of detected vulnerabilities. Each vulnerability must be a short description of the issue.
    - "explanation" (string): a detailed explanation of why these vulnerabilities are dangerous.
    - "fixes" (array): for each vulnerability found, provide a clear and actionable fix.
      Each fix should include specific changes (e.g., additional modifiers, new checks,
      safe math, proper access control) described in plain English. Be as detailed as possible.
    - "corrected_code" (string): provide a corrected version of the original Solidity code,
      applying all suggested fixes directly into the code.

    IMPORTANT:
    1. Do not include any extra commentary outside the JSON.
    2. Ensure the JSON is valid and can be parsed without errors.

    Smart contract code to analyze:
    {code}
    """

    detector = Detector()
    result = detector.detect(prompt)

    # Handle dict or string
    if isinstance(result, dict):
        data = result
    else:
        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            print("The model did not return valid JSON. Output was:")
            print(result)
            sys.exit(1)
    return data


# 1. First analysis on original contract
data = analyze_contract("test_contract.sol")

# Save corrected contract if available
corrected_code = data.get("corrected_code")
if corrected_code:
    output_file = "corrected_contract.sol"
    with open(output_file, "w") as f:
        f.write(corrected_code)
    print(f"\nCorrected contract saved to {output_file}")

    # 2. Second analysis on corrected contract
    print("\nReanalyzing corrected contract...\n")
    second_data = analyze_contract(output_file)

    if second_data.get("vulnerable"):
        print("⚠️ Issues still detected in the corrected contract:")
        for v in second_data.get("vulnerabilities", []):
            print("-", v)
    else:
        print("✅ No vulnerabilities found in the corrected contract!")
else:
    print("\nNo corrected code provided by the model.")
