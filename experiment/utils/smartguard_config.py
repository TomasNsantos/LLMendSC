"""
Configurações para o sistema SmartGuard de correção de vulnerabilidades
Baseado no paper: "SmartGuard: An LLM-enhanced framework for smart contract vulnerability detection"
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Carrega variáveis do ambiente
load_dotenv()

class SmartGuardConfig:
    """
    Configurações centralizadas para o SmartGuard
    """
    
    # === API Configuration ===
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
    
    # === Framework Parameters (baseado no paper) ===
    MAX_ITERATIONS = 5  # Limite de iterações para correção
    RETHINKING_LIMIT = 3  # N_t no paper - limite de re-thinking
    SELF_CHECK_LIMIT = 2  # N_c no paper - limite de self-check
    MAX_DEMONSTRATIONS = 4  # k no paper - top-k demonstrações
    VERIFICATION_ATTEMPTS = 3  # Tentativas de verificação final
    
    # === Code Processing ===
    MAX_CODE_LENGTH = 510  # L no paper - comprimento máximo do código para CodeBERT
    SLEEP_TIME = 1  # Tempo entre requisições API
    
    # === Directories ===
    INPUT_DIR = "contracts_to_analyze"
    OUTPUT_DIR = "corrected_contracts"
    TEMP_DIR = "temp_analysis"
    CORPUS_DIR = "smart_contract_corpus"
    REPORTS_DIR = "correction_reports"
    
    # === Vulnerability Types (baseado no SolidiFI dataset) ===
    VULNERABILITY_TYPES = {
        'reentrancy': 'Re-entrancy',
        'timestamp': 'Timestamp-Dependency',
        'overflow': 'Integer Overflow/Underflow',
        'underflow': 'Integer Overflow/Underflow',
        'access_control': 'Access Control',
        'unchecked_calls': 'Unchecked External Calls',
        'delegate_call': 'Delegate Call'
    }
    
    # === Quality Thresholds ===
    MIN_CORRECTION_QUALITY = 0.8  # Qualidade mínima para aceitar correção
    MIN_SECURITY_SCORE = 0.9  # Score mínimo de segurança final
    MIN_CONFIDENCE_SCORE = 0.7  # Confiança mínima na análise
    
    # === Prompts Templates (inspirados no SmartGuard) ===
    DETECTION_PROMPT_TEMPLATE = """
    You are a smart contract security expert analyzing Solidity code for vulnerabilities.
    
    Follow this Chain of Thought reasoning:
    1. Code Structure Analysis: Examine functions, modifiers, and state variables
    2. Vulnerability Identification: Look for {vulnerability_types}
    3. Risk Assessment: Evaluate severity and impact
    4. Correction Strategy: Plan specific fixes needed
    
    Analyze this code:
    {code}
    
    Return JSON with:
    - "vulnerable" (boolean)
    - "vulnerabilities" (array)
    - "reasoning_chain" (string): detailed CoT analysis
    - "severity_scores" (object): severity for each vulnerability (0.0-1.0)
    - "fixes" (array): specific actionable fixes
    - "corrected_code" (string)
    - "confidence_score" (float)
    """
    
    SELF_CHECK_PROMPT_TEMPLATE = """
    Verify the correction quality of this smart contract fix.
    
    Original vulnerabilities: {original_vulnerabilities}
    
    ORIGINAL CODE:
    {original_code}
    
    CORRECTED CODE:  
    {corrected_code}
    
    Self-check process:
    1. Are all original vulnerabilities addressed?
    2. Do the fixes introduce new vulnerabilities?
    3. Is the correction complete and secure?
    4. Rate correction quality (0.0-1.0)
    
    Return JSON:
    - "correction_successful" (boolean)
    - "remaining_vulnerabilities" (array) 
    - "correction_quality" (float)
    - "verification_reasoning" (string)
    - "new_issues_introduced" (array)
    - "suggestions" (array)
    """
    
    RETHINKING_PROMPT_TEMPLATE = """
    Improve the smart contract vulnerability correction.
    
    ITERATION: {iteration}
    ORIGINAL CODE: {original_code}
    PREVIOUS ATTEMPT: {previous_code}
    FEEDBACK: {feedback}
    
    Rethinking process:
    1. What specific issues remain in the previous correction?
    2. How can each vulnerability be better addressed?
    3. What additional security measures are needed?
    4. Generate improved corrected code
    
    Return JSON:
    - "improved_reasoning" (string)
    - "corrected_code" (string)
    - "changes_made" (array)
    - "improvement_confidence" (float)
    """
    
    FINAL_VERIFICATION_PROMPT_TEMPLATE = """
    Perform comprehensive final security verification.
    
    Code to verify:
    {code}
    
    Comprehensive security checklist:
    - Re-entrancy protection
    - Access control mechanisms  
    - Integer overflow/underflow protection
    - Timestamp dependency issues
    - Unchecked external calls
    - State variable manipulation
    - Function visibility
    - Gas optimization security
    - Logic errors
    
    Return JSON:
    - "secure" (boolean)
    - "final_vulnerabilities" (array)
    - "security_score" (float): 0.0-1.0
    - "final_assessment" (string)
    - "security_checklist_results" (object)
    - "recommendations" (array)
    """
    
    # === Logging Configuration ===
    ENABLE_DETAILED_LOGGING = True
    LOG_LEVEL = "INFO"
    LOG_FILE = "smartguard_correction.log"
    
    # === Performance Settings ===
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    TIMEOUT = 30  # seconds per API call
    
    # === Evaluation Metrics (baseado no paper) ===
    METRICS_TO_TRACK = [
        'correction_success_rate',
        'final_security_score',
        'iterations_needed',
        'processing_time',
        'api_calls_made',
        'vulnerability_detection_accuracy'
    ]
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Valida se todas as configurações necessárias estão definidas
        """
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        return True
    
    @classmethod
    def create_directories(cls):
        """
        Cria diretórios necessários
        """
        dirs = [
            cls.INPUT_DIR,
            cls.OUTPUT_DIR, 
            cls.TEMP_DIR,
            cls.CORPUS_DIR,
            cls.REPORTS_DIR
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Directory ready: {dir_path}")
    
    @classmethod
    def get_vulnerability_prompt(cls, vulnerability_type: str) -> str:
        """
        Retorna prompt específico para tipo de vulnerabilidade
        """
        specific_prompts = {
            'reentrancy': """
            Focus specifically on re-entrancy vulnerabilities:
            - External calls before state changes
            - Missing mutex/locks
            - Check-effects-interactions pattern violations
            """,
            'timestamp': """
            Focus specifically on timestamp dependency:
            - Use of block.timestamp in critical logic
            - Time-based randomness
            - Timestamp manipulation possibilities
            """,
            'overflow': """
            Focus specifically on integer overflow/underflow:
            - Arithmetic operations without SafeMath
            - Unchecked increments/decrements
            - Type casting issues
            """
        }
        
        return specific_prompts.get(vulnerability_type, "")
    
    @classmethod
    def get_correction_strategy(cls, vulnerability_type: str) -> List[str]:
        """
        Retorna estratégias específicas de correção
        """
        strategies = {
            'reentrancy': [
                "Implement ReentrancyGuard modifier",
                "Follow check-effects-interactions pattern",
                "Use pull-over-push for external payments"
            ],
            'timestamp': [
                "Replace block.timestamp with block.number where possible",
                "Add reasonable time bounds",
                "Use commit-reveal schemes for randomness"
            ],
            'overflow': [
                "Use SafeMath library",
                "Implement overflow checks",
                "Use Solidity 0.8+ built-in checks"
            ]
        }
        
        return strategies.get(vulnerability_type, [])