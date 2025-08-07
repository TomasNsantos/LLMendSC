import sys
import os
import json
import numpy as np
from time import sleep, time
from typing import Dict, List, Optional, Tuple

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import SmartGuard components
from experiment.utils.smartguard_config import SmartGuardConfig
from experiment.utils.advanced_detector import SmartGuardAdvancedDetector, VulnerabilityResult, CorrectionResult
from experiment.utils.reporting_system import SmartGuardReporter, ContractAnalysis
from experiment.utils.tools import Detector

def main():
    """
    SmartGuard-inspired vulnerability correction system
    Implementa as técnicas do paper para correção automatizada com verificação
    """
    print("🚀 Starting SmartGuard Vulnerability Correction System")
    print("📖 Based on: 'SmartGuard: An LLM-enhanced framework for smart contract vulnerability detection'")
    
    # Initialize configuration
    config = SmartGuardConfig()
    
    # Validate configuration
    if not config.validate_config():
        print("❌ Configuration validation failed!")
        return
    
    # Create necessary directories
    config.create_directories()
    
    # Initialize components
    print("🔧 Initializing SmartGuard components...")
    detector = SmartGuardAdvancedDetector(config)
    reporter = SmartGuardReporter(config.REPORTS_DIR)
    
    # Check for input files
    if not os.path.exists(config.INPUT_DIR):
        print(f"❌ Input directory {config.INPUT_DIR} not found!")
        return
    
    sol_files = [f for f in os.listdir(config.INPUT_DIR)]
import os
import json
import numpy as np
from time import sleep
from typing import Dict, List, Optional, Tuple

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from experiment.utils.tools import Detector

# Folders
INPUT_DIR = "contracts_to_analyze"
OUTPUT_DIR = "corrected_contracts"
TEMP_DIR = "temp_analysis"
CORPUS_DIR = "smart_contract_corpus"  # Para armazenar exemplos de contratos conhecidos

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(CORPUS_DIR, exist_ok=True)

# Configuration parameters inspired by SmartGuard
MAX_ITERATIONS = 5
RETHINKING_LIMIT = 3
SELF_CHECK_LIMIT = 2
MAX_DEMONSTRATIONS = 4
VERIFICATION_ATTEMPTS = 3

class SmartGuardCorrector:
    def __init__(self):
        self.detector = Detector()
        self.vulnerability_types = {
            'reentrancy': 'Re-entrancy',
            'timestamp': 'Timestamp-Dependency', 
            'overflow': 'Integer Overflow/Underflow',
            'underflow': 'Integer Overflow/Underflow'
        }
        
    def analyze_contract_detailed(self, code: str) -> Optional[Dict]:
        """
        Análise detalhada do contrato usando prompts inspirados no SmartGuard
        """
        prompt = f"""
        You are a smart contract security expert. Analyze the following Solidity code for vulnerabilities.
        
        Please follow this Chain of Thought reasoning process:
        1. First, examine the code structure and identify potential security issues
        2. For each issue found, explain why it's dangerous
        3. Provide specific, actionable fixes
        4. Generate corrected code that addresses all issues
        
        Return your response as a JSON object with these keys:
        - "vulnerable" (boolean): true if vulnerabilities found
        - "vulnerabilities" (array): list of vulnerability types found
        - "reasoning_chain" (string): step-by-step analysis explaining your thought process
        - "explanation" (string): detailed explanation of security issues
        - "fixes" (array): specific fixes for each vulnerability
        - "corrected_code" (string): complete corrected Solidity code
        - "confidence_score" (float): confidence in the analysis (0.0 to 1.0)
        
        Focus on these vulnerability types:
        - Re-entrancy attacks
        - Timestamp dependency
        - Integer overflow/underflow
        - Access control issues
        - Unchecked external calls
        
        Smart contract code:
        {code}
        """
        
        return self._execute_with_retry(prompt)
    
    def self_check_correction(self, original_code: str, corrected_code: str, 
                            original_vulnerabilities: List[str]) -> Dict:
        """
        Auto-verificação da correção usando self-check architecture do SmartGuard
        """
        prompt = f"""
        You are verifying a smart contract vulnerability correction.
        
        Original vulnerabilities found: {', '.join(original_vulnerabilities)}
        
        Please analyze if the corrected code properly addresses these issues:
        
        ORIGINAL CODE:
        {original_code}
        
        CORRECTED CODE:
        {corrected_code}
        
        Return JSON with:
        - "correction_successful" (boolean): true if vulnerabilities were properly fixed
        - "remaining_vulnerabilities" (array): any vulnerabilities still present
        - "correction_quality" (float): quality score 0.0 to 1.0
        - "verification_reasoning" (string): detailed explanation of your verification
        - "suggestions" (array): additional improvements if needed
        """
        
        return self._execute_with_retry(prompt)
    
    def generate_improved_correction(self, code: str, previous_attempt: str, 
                                   feedback: str, iteration: int) -> Optional[Dict]:
        """
        Gera correção melhorada baseada em feedback (rethinking process)
        """
        rethinking_prompt = f"""
        You are improving a smart contract vulnerability correction.
        
        ITERATION: {iteration}
        
        ORIGINAL CODE:
        {code}
        
        PREVIOUS CORRECTION ATTEMPT:
        {previous_attempt}
        
        FEEDBACK ON PREVIOUS ATTEMPT:
        {feedback}
        
        Please rethink and provide an improved correction. Consider:
        1. What went wrong in the previous attempt?
        2. How can the correction be improved?
        3. Are there additional security measures needed?
        
        Return JSON with improved correction:
        - "vulnerable" (boolean)
        - "vulnerabilities" (array)
        - "improved_reasoning" (string): explanation of improvements made
        - "corrected_code" (string): improved corrected code
        - "changes_made" (array): specific changes from previous attempt
        """
        
        return self._execute_with_retry(rethinking_prompt)
    
    def _execute_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Executa prompt com retry em caso de erro
        """
        for attempt in range(max_retries):
            try:
                result = self.detector.detect(prompt)
                if result:
                    return result
                sleep(2)  # Wait before retry
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(2)
        return None
    
    def verify_correction_effectiveness(self, corrected_code: str) -> Dict:
        """
        Verificação final da efetividade da correção
        """
        verification_prompt = f"""
        Perform a final security verification of this corrected smart contract.
        
        Analyze for ANY remaining vulnerabilities:
        - Re-entrancy
        - Timestamp dependency  
        - Integer overflow/underflow
        - Access control issues
        - Unchecked external calls
        - Any other security issues
        
        Code to verify:
        {corrected_code}
        
        Return JSON:
        - "secure" (boolean): true if no vulnerabilities found
        - "final_vulnerabilities" (array): any remaining issues
        - "security_score" (float): overall security score 0.0 to 1.0
        - "final_assessment" (string): comprehensive security assessment
        """
        
        return self._execute_with_retry(verification_prompt)

def process_contract_with_smartguard_approach(filename: str, corrector: SmartGuardCorrector):
    """
    Processa contrato usando abordagem inspirada no SmartGuard
    """
    print(f"\n🔍 Analyzing: {filename}")
    
    contract_path = os.path.join(INPUT_DIR, filename)
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            original_code = f.read()
    except UnicodeDecodeError as e:
        print(f"❌ Could not read file: {filename}: {e}")
        return
    
    current_code = original_code
    correction_history = []
    
    # Análise inicial detalhada
    print("🧠 Performing initial detailed analysis...")
    initial_analysis = corrector.analyze_contract_detailed(current_code)
    
    if not initial_analysis:
        print("❌ Initial analysis failed")
        return
    
    if not initial_analysis.get("vulnerable", False):
        print("✅ Contract appears secure. No vulnerabilities detected.")
        return
    
    print("⚠️ Vulnerabilities detected:")
    vulnerabilities = initial_analysis.get("vulnerabilities", [])
    for vuln in vulnerabilities:
        print(f"   - {vuln}")
    
    print(f"🤖 Reasoning: {initial_analysis.get('reasoning_chain', 'N/A')}")
    
    # Processo de correção iterativa com self-check
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n🔁 Correction Iteration {iteration}...")
        
        if iteration == 1:
            # Primeira correção
            corrected_code = initial_analysis.get("corrected_code")
            if not corrected_code:
                print("❌ No corrected code provided in initial analysis")
                break
        else:
            # Correção melhorada baseada em feedback
            feedback = correction_history[-1].get("feedback", "Previous correction was not satisfactory")
            improvement_result = corrector.generate_improved_correction(
                original_code, current_code, feedback, iteration
            )
            
            if not improvement_result:
                print(f"❌ Failed to generate improved correction at iteration {iteration}")
                break
            
            corrected_code = improvement_result.get("corrected_code")
            if not corrected_code:
                print(f"❌ No improved code at iteration {iteration}")
                break
                
            print(f"💡 Improvements made: {improvement_result.get('changes_made', [])}")
        
        # Self-check da correção
        print("🔍 Performing self-check verification...")
        verification_result = corrector.self_check_correction(
            original_code, corrected_code, vulnerabilities
        )
        
        if not verification_result:
            print("❌ Self-check verification failed")
            continue
        
        correction_successful = verification_result.get("correction_successful", False)
        remaining_vulns = verification_result.get("remaining_vulnerabilities", [])
        quality_score = verification_result.get("correction_quality", 0.0)
        
        print(f"📊 Correction Quality Score: {quality_score:.2f}")
        print(f"🔍 Verification Reasoning: {verification_result.get('verification_reasoning', 'N/A')}")
        
        correction_history.append({
            "iteration": iteration,
            "corrected_code": corrected_code,
            "quality_score": quality_score,
            "remaining_vulnerabilities": remaining_vulns,
            "feedback": f"Quality: {quality_score}, Remaining issues: {remaining_vulns}"
        })
        
        if correction_successful and not remaining_vulns:
            print("✅ Self-check passed! Performing final verification...")
            
            # Verificação final independente
            final_verification = corrector.verify_correction_effectiveness(corrected_code)
            
            if final_verification and final_verification.get("secure", False):
                security_score = final_verification.get("security_score", 0.0)
                print(f"🎉 Final verification successful! Security Score: {security_score:.2f}")
                
                # Salva código corrigido e verificado
                corrected_path = os.path.join(OUTPUT_DIR, filename)
                with open(corrected_path, "w", encoding="utf-8") as f:
                    f.write(corrected_code)
                
                # Salva relatório detalhado
                report = {
                    "filename": filename,
                    "original_vulnerabilities": vulnerabilities,
                    "correction_iterations": len(correction_history),
                    "final_security_score": security_score,
                    "correction_history": correction_history,
                    "final_assessment": final_verification.get("final_assessment", ""),
                    "timestamp": str(np.datetime64('now'))
                }
                
                report_path = os.path.join(OUTPUT_DIR, f"{filename}.report.json")
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Verified corrected contract saved to {corrected_path}")
                print(f"📄 Detailed report saved to {report_path}")
                return
            else:
                print("⚠️ Final verification found remaining issues")
                final_issues = final_verification.get("final_vulnerabilities", []) if final_verification else []
                print(f"   Issues: {final_issues}")
        
        current_code = corrected_code
        
        if iteration < MAX_ITERATIONS:
            print(f"🔄 Continuing to iteration {iteration + 1}...")
    
    print("⚠️ Maximum iterations reached. Contract may still have vulnerabilities.")
    print("💡 Consider manual review or additional security analysis.")

def main():
    """
    Função principal que processa todos os contratos
    """
    print("🚀 Starting SmartGuard-inspired vulnerability correction...")
    print(f"📁 Input directory: {INPUT_DIR}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"⚙️  Max iterations: {MAX_ITERATIONS}")
    
    corrector = SmartGuardCorrector()
    
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Input directory {INPUT_DIR} not found!")
        return
    
    sol_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".sol")]
    
    if not sol_files:
        print(f"❌ No .sol files found in {INPUT_DIR}")
        return
    
    print(f"📊 Found {len(sol_files)} contracts to process")
    
    for filename in sol_files:
        try:
            process_contract_with_smartguard_approach(filename, corrector)
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue
    
    print("\n✅ Processing complete!")
    print(f"📁 Check {OUTPUT_DIR} for corrected contracts and reports")

if __name__ == "__main__":
    main()