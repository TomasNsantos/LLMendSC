"""
Detector Avançado inspirado no SmartGuard
Implementa Chain of Thought, Self-Check Architecture, e In-Context Learning
"""

import json
import time
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

import openai
from experiment.utils.config import OPENAI_API_KEY, OPENAI_API_BASE
from experiment.utils.smartguard_config import SmartGuardConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VulnerabilityResult:
    """Resultado de análise de vulnerabilidade"""
    vulnerable: bool
    vulnerability_types: List[str]
    severity_scores: Dict[str, float]
    reasoning_chain: str
    confidence_score: float
    corrected_code: Optional[str] = None
    fixes_applied: List[str] = None

@dataclass  
class CorrectionResult:
    """Resultado de correção de vulnerabilidade"""
    success: bool
    corrected_code: str
    quality_score: float
    remaining_vulnerabilities: List[str]
    iterations_needed: int
    reasoning: str

class BaseDetector(ABC):
    """Interface base para detectores"""
    
    @abstractmethod
    def analyze(self, code: str) -> VulnerabilityResult:
        pass
    
    @abstractmethod
    def correct(self, code: str, vulnerabilities: List[str]) -> CorrectionResult:
        pass

class SmartGuardAdvancedDetector(BaseDetector):
    """
    Detector avançado implementando a arquitetura SmartGuard:
    - Chain of Thought reasoning
    - Self-Check architecture  
    - In-Context Learning
    - Demonstration selection
    """
    
    def __init__(self, config: SmartGuardConfig = SmartGuardConfig()):
        self.config = config
        self.client = self._init_openai_client()
        self.demonstration_corpus = []
        self.correction_history = []
        
    def _init_openai_client(self):
        """Inicializa cliente OpenAI"""
        openai.api_key = self.config.OPENAI_API_KEY
        openai.api_base = self.config.OPENAI_API_BASE
        return openai
    
    def analyze(self, code: str) -> VulnerabilityResult:
        """
        Análise principal usando Chain of Thought
        """
        logger.info("🧠 Starting Chain of Thought analysis...")
        
        # Step 1: Generate Chain of Thought analysis
        cot_result = self._generate_cot_analysis(code)
        if not cot_result:
            return VulnerabilityResult(
                vulnerable=False,
                vulnerability_types=[],
                severity_scores={},
                reasoning_chain="Analysis failed",
                confidence_score=0.0
            )
        
        # Step 2: Self-check the analysis  
        if cot_result['confidence_score'] < self.config.MIN_CONFIDENCE_SCORE:
            logger.info("🔍 Low confidence, performing self-check...")
            cot_result = self._self_check_analysis(code, cot_result)
        
        return VulnerabilityResult(
            vulnerable=cot_result.get('vulnerable', False),
            vulnerability_types=cot_result.get('vulnerabilities', []),
            severity_scores=cot_result.get('severity_scores', {}),
            reasoning_chain=cot_result.get('reasoning_chain', ''),
            confidence_score=cot_result.get('confidence_score', 0.0),
            corrected_code=cot_result.get('corrected_code'),
            fixes_applied=cot_result.get('fixes', [])
        )
    
    def correct(self, code: str, vulnerabilities: List[str]) -> CorrectionResult:
        """
        Processo de correção com Self-Check Architecture
        """
        logger.info(f"🔧 Starting correction process for vulnerabilities: {vulnerabilities}")
        
        current_code = code
        iteration = 0
        correction_history = []
        
        while iteration < self.config.MAX_ITERATIONS:
            iteration += 1
            logger.info(f"🔁 Correction iteration {iteration}")
            
            # Generate correction
            if iteration == 1:
                correction_result = self._generate_initial_correction(code, vulnerabilities)
            else:
                # Use feedback from previous iteration
                previous_feedback = correction_history[-1]['feedback']
                correction_result = self._generate_improved_correction(
                    code, current_code, previous_feedback, iteration
                )
            
            if not correction_result:
                logger.error(f"❌ Failed to generate correction at iteration {iteration}")
                break
            
            corrected_code = correction_result.get('corrected_code')
            if not corrected_code:
                logger.error(f"❌ No corrected code at iteration {iteration}")
                break
            
            # Self-check the correction
            verification = self._verify_correction(code, corrected_code, vulnerabilities)
            
            quality_score = verification.get('correction_quality', 0.0)
            remaining_vulns = verification.get('remaining_vulnerabilities', [])
            successful = verification.get('correction_successful', False)
            
            correction_history.append({
                'iteration': iteration,
                'corrected_code': corrected_code,
                'quality_score': quality_score,
                'remaining_vulnerabilities': remaining_vulns,
                'successful': successful,
                'feedback': verification.get('verification_reasoning', '')
            })
            
            logger.info(f"📊 Quality Score: {quality_score:.2f}, Remaining: {len(remaining_vulns)} vulnerabilities")
            
            # Check if correction is satisfactory
            if successful and quality_score >= self.config.MIN_CORRECTION_QUALITY:
                # Final verification
                final_check = self._final_security_verification(corrected_code)
                
                if final_check and final_check.get('secure', False):
                    logger.info("✅ Correction successful!")
                    return CorrectionResult(
                        success=True,
                        corrected_code=corrected_code,
                        quality_score=final_check.get('security_score', quality_score),
                        remaining_vulnerabilities=[],
                        iterations_needed=iteration,
                        reasoning=final_check.get('final_assessment', '')
                    )
            
            current_code = corrected_code
        
        # Max iterations reached
        logger.warning("⚠️ Max iterations reached without satisfactory correction")
        best_attempt = max(correction_history, key=lambda x: x['quality_score']) if correction_history else None
        
        if best_attempt:
            return CorrectionResult(
                success=False,
                corrected_code=best_attempt['corrected_code'],
                quality_score=best_attempt['quality_score'],
                remaining_vulnerabilities=best_attempt['remaining_vulnerabilities'],
                iterations_needed=iteration,
                reasoning=f"Max iterations reached. Best quality: {best_attempt['quality_score']:.2f}"
            )
        
        return CorrectionResult(
            success=False,
            corrected_code=code,
            quality_score=0.0,
            remaining_vulnerabilities=vulnerabilities,
            iterations_needed=iteration,
            reasoning="Correction process failed"
        )
    
    def _generate_cot_analysis(self, code: str) -> Optional[Dict]:
        """
        Gera análise usando Chain of Thought reasoning
        """
        # Select relevant demonstrations (In-Context Learning)
        demonstrations = self._select_demonstrations(code)
        
        prompt = self._build_cot_prompt(code, demonstrations)
        
        return self._execute_llm_call(prompt, "CoT Analysis")
    
    def _self_check_analysis(self, code: str, analysis_result: Dict) -> Dict:
        """
        Self-check architecture para validar análise
        """
        check_prompt = f"""
        You are reviewing your own vulnerability analysis. Check if your analysis is correct and complete.
        
        ORIGINAL CODE:
        {code}
        
        YOUR PREVIOUS ANALYSIS:
        {json.dumps(analysis_result, indent=2)}
        
        Self-check questions:
        1. Did you identify all potential vulnerabilities?
        2. Are the severity scores accurate?
        3. Is the reasoning chain logical and complete?
        4. Are there any false positives?
        
        If you find errors, provide corrected analysis.
        Return the same JSON format with any corrections made.
        """
        
        corrected_result = self._execute_llm_call(check_prompt, "Self-Check Analysis")
        
        if corrected_result:
            # Combine original and corrected results
            corrected_result['self_checked'] = True
            return corrected_result
        
        return analysis_result
    
    def _generate_initial_correction(self, code: str, vulnerabilities: List[str]) -> Optional[Dict]:
        """
        Gera correção inicial baseada nas vulnerabilidades encontradas
        """
        vulnerability_context = self._get_vulnerability_context(vulnerabilities)
        
        prompt = f"""
        You are correcting smart contract vulnerabilities.
        
        VULNERABILITIES TO FIX: {', '.join(vulnerabilities)}
        
        {vulnerability_context}
        
        ORIGINAL CODE:
        {code}
        
        Correction strategy:
        1. Analyze each vulnerability systematically
        2. Apply specific fixes for each issue
        3. Ensure fixes don't introduce new vulnerabilities
        4. Maintain contract functionality
        
        Return JSON:
        - "corrected_code" (string): complete corrected Solidity code
        - "fixes_applied" (array): specific fixes implemented
        - "reasoning" (string): explanation of corrections made
        - "confidence" (float): confidence in correction quality
        """
        
        return self._execute_llm_call(prompt, "Initial Correction")
    
    def _generate_improved_correction(self, original_code: str, previous_code: str, 
                                    feedback: str, iteration: int) -> Optional[Dict]:
        """
        Gera correção melhorada baseada em feedback (Rethinking process)
        """
        prompt = self.config.RETHINKING_PROMPT_TEMPLATE.format(
            iteration=iteration,
            original_code=original_code,
            previous_code=previous_code,
            feedback=feedback
        )
        
        return self._execute_llm_call(prompt, f"Rethinking Iteration {iteration}")
    
    def _verify_correction(self, original_code: str, corrected_code: str, 
                          original_vulnerabilities: List[str]) -> Dict:
        """
        Verifica qualidade da correção usando Self-Check
        """
        prompt = self.config.SELF_CHECK_PROMPT_TEMPLATE.format(
            original_vulnerabilities=', '.join(original_vulnerabilities),
            original_code=original_code,
            corrected_code=corrected_code
        )
        
        result = self._execute_llm_call(prompt, "Correction Verification")
        
        if not result:
            return {
                'correction_successful': False,
                'correction_quality': 0.0,
                'remaining_vulnerabilities': original_vulnerabilities,
                'verification_reasoning': 'Verification failed'
            }
        
        return result
    
    def _final_security_verification(self, code: str) -> Optional[Dict]:
        """
        Verificação final de segurança abrangente
        """
        prompt = self.config.FINAL_VERIFICATION_PROMPT_TEMPLATE.format(code=code)
        
        return self._execute_llm_call(prompt, "Final Security Verification")
    
    def _select_demonstrations(self, query_code: str, k: int = None) -> List[Dict]:
        """
        Seleciona demonstrações relevantes para In-Context Learning
        (Implementação simplificada - no SmartGuard original usa CodeBERT)
        """
        if not k:
            k = self.config.MAX_DEMONSTRATIONS
        
        # Em uma implementação completa, aqui usaríamos:
        # 1. CodeBERT para gerar embeddings semânticos
        # 2. Cálculo de similaridade cosseno
        # 3. Seleção dos top-k exemplos mais similares
        
        # Por enquanto, retorna exemplos estáticos (placeholder)
        return []
    
    def _build_cot_prompt(self, code: str, demonstrations: List[Dict]) -> str:
        """
        Constrói prompt com Chain of Thought e demonstrações
        """
        vulnerability_types = ', '.join(self.config.VULNERABILITY_TYPES.values())
        
        base_prompt = self.config.DETECTION_PROMPT_TEMPLATE.format(
            vulnerability_types=vulnerability_types,
            code=code
        )
        
        # Adiciona demonstrações se disponíveis
        if demonstrations:
            demo_section = "\n\nEXAMPLES:\n"
            for i, demo in enumerate(demonstrations):
                demo_section += f"\nExample {i+1}:\n"
                demo_section += f"Code: {demo.get('code', '')}\n"
                demo_section += f"Analysis: {demo.get('analysis', '')}\n"
            
            base_prompt = demo_section + "\n" + base_prompt
        
        return base_prompt
    
    def _get_vulnerability_context(self, vulnerabilities: List[str]) -> str:
        """
        Obtém contexto específico para tipos de vulnerabilidade
        """
        context = "VULNERABILITY-SPECIFIC GUIDANCE:\n"
        
        for vuln in vulnerabilities:
            vuln_key = self._normalize_vulnerability_name(vuln)
            specific_context = self.config.get_vulnerability_prompt(vuln_key)
            
            if specific_context:
                context += f"\nFor {vuln}:\n{specific_context}\n"
            
            strategies = self.config.get_correction_strategy(vuln_key)
            if strategies:
                context += f"Correction strategies:\n"
                for strategy in strategies:
                    context += f"- {strategy}\n"
        
        return context
    
    def _normalize_vulnerability_name(self, vuln_name: str) -> str:
        """
        Normaliza nome da vulnerabilidade para busca no config
        """
        vuln_lower = vuln_name.lower().replace('-', '').replace('_', '').replace(' ', '')
        
        mapping = {
            'reentrancy': 'reentrancy',
            're-entrancy': 'reentrancy',
            'timestampdependency': 'timestamp',
            'timestamp-dependency': 'timestamp',
            'integeroverflow': 'overflow',
            'integer overflow/underflow': 'overflow',
            'overflow-underflow': 'overflow'
        }
        
        return mapping.get(vuln_lower, vuln_lower)
    
    def _execute_llm_call(self, prompt: str, operation: str) -> Optional[Dict]:
        """
        Executa chamada para LLM com retry e parsing
        """
        for attempt in range(self.config.MAX_RETRIES):
            try:
                logger.info(f"🤖 {operation} - Attempt {attempt + 1}")
                
                messages = [{"role": "user", "content": prompt}]
                
                response = openai.ChatCompletion.create(
                    model=self.config.OPENAI_MODEL,
                    messages=messages,
                    timeout=self.config.TIMEOUT
                )
                
                content = response['choices'][0]['message']['content']
                
                # Parse JSON response
                result = self._parse_json_response(content)
                
                if result:
                    logger.info(f"✅ {operation} successful")
                    return result
                else:
                    logger.warning(f"⚠️ {operation} - Invalid JSON response")
                
            except Exception as e:
                logger.error(f"❌ {operation} - Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(self.config.RETRY_DELAY)
        
        logger.error(f"❌ {operation} - All attempts failed")
        return None
    
    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """
        Parse resposta JSON do LLM
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.rfind("```")
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.rfind("```")
                content = content[start:end].strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Content: {content[:500]}...")
            return None
    
    def add_demonstration(self, code: str, analysis: Dict):
        """
        Adiciona exemplo ao corpus de demonstrações
        """
        self.demonstration_corpus.append({
            'code': code,
            'analysis': analysis,
            'timestamp': time.time()
        })
        
        # Limita tamanho do corpus
        max_corpus_size = 100
        if len(self.demonstration_corpus) > max_corpus_size:
            self.demonstration_corpus = self.demonstration_corpus[-max_corpus_size:]
    
    def get_performance_metrics(self) -> Dict:
        """
        Retorna métricas de performance
        """
        if not self.correction_history:
            return {}
        
        total_corrections = len(self.correction_history)
        successful_corrections = sum(1 for c in self.correction_history if c.get('success', False))
        
        avg_iterations = np.mean([c.get('iterations_needed', 0) for c in self.correction_history])
        avg_quality = np.mean([c.get('quality_score', 0) for c in self.correction_history])
        
        return {
            'total_corrections_attempted': total_corrections,
            'successful_corrections': successful_corrections,
            'success_rate': successful_corrections / total_corrections if total_corrections > 0 else 0,
            'average_iterations_needed': avg_iterations,
            'average_quality_score': avg_quality
        }