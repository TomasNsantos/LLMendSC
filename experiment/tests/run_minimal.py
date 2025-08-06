import sys
import os
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from experiment.utils.tools import Detector

# Folders
INPUT_DIR = "contracts_to_analyze"
OUTPUT_DIR = "corrected_contracts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Max number of auto-correction attempts
MAX_ITERATIONS = 3

def analyze_contract(code):
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

    if isinstance(result, dict):
        return result

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON from model output.")
        print(result)
        return None

# Process all .sol files
for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".sol"):
        continue

    print(f"\n🔍 Analyzing: {filename}")
    contract_path = os.path.join(INPUT_DIR, filename)

    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            code = f.read()
    except UnicodeDecodeError as e:
        print(f"❌ Could not read file: {filename}: {e}")
        continue

    current_code = code
    corrected_path = os.path.join(OUTPUT_DIR, filename)

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n🔁 Iteration {iteration}...")

        analysis = analyze_contract(current_code)
        if not analysis:
            print("⚠️ Skipping due to error in analysis.")
            break

        if analysis.get("vulnerable"):
            vulnerabilities = analysis.get("vulnerabilities", [])
            if vulnerabilities:
                print("⚠️ Vulnerabilities found:")
                for vuln in vulnerabilities:
                    print(f"   - {vuln}")
            else:
                print("⚠️ Vulnerable, but no specific issues listed.")

            corrected_code = analysis.get("corrected_code")
            if not corrected_code:
                print("❌ No corrected code returned.")
                break

            # Save only if the corrected code is different from current
            if corrected_code.strip() != current_code.strip():
                with open(corrected_path, "w", encoding="utf-8") as f:
                    f.write(corrected_code)
                print(f"💾 Corrected contract saved to {corrected_path}")
            else:
                print("ℹ️ Model returned the same code. No changes made.")

            current_code = corrected_code
        else:
            print("✅ Contract is secure. No vulnerabilities found.")
            break
    else:
        print("⚠️ Maximum iterations reached. Contract may still be vulnerable.")
