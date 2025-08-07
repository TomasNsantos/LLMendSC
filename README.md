# 🔐 LLMendSC: Correção Assistida por LLM para Vulnerabilidades em Smart Contracts

---

## 🎯 Objetivo

Este projeto propõe a extensão do **SmartGuard**, um framework baseado em LLMs para detecção de vulnerabilidades em contratos inteligentes, com um módulo adicional de **reparo automático assistido por LLM**. A ideia é que, ao identificar falhas como *reentrância*, *overflow* ou *timestamp dependence*, o sistema sugira correções plausíveis e seguras, reduzindo o ciclo de feedback e aumentando a automação na manutenção de smart contracts.

---

## 🗉 Atividade do Ciclo de Vida Envolvida

**Manutenção e Correção de Software** – atividade crítica para garantir a segurança e a confiabilidade de sistemas em produção. Este projeto explora como **LLMs podem atuar não apenas como detectores, mas como agentes de reparo automatizado**, com apoio de validação formal para garantir correções seguras e funcionais.

---

## 🤖 Proposta com LLM

Ao detectar uma vulnerabilidade em um contrato Solidity por meio do SmartGuard, um LLM (como GPT-4, Claude 3 ou LLaMA 3) recebe o trecho vulnerável e o contexto, e sugere uma versão reparada do código.  
Essa sugestão é então validada por ferramentas de análise estática (como **Slither** ou **Mythril**) e por testes de compilação e execução, com o objetivo de garantir que:

- A vulnerabilidade foi de fato corrigida;
- O código permanece funcional e semanticamente equivalente;
- Não foram introduzidos novos problemas.

---

## 🧪 Experimentos



### ✅ Vantagens (Precisão e Automação)

**Cenário:** Conjunto de contratos com falhas conhecidas.  
**Método A (Controle):** Apenas detecção com SmartGuard.  
**Método B (Experimental):** Detecção com SmartGuard + reparo automatizado com LLM + validação.  
**Métricas:**

- % de vulnerabilidades corrigidas corretamente (sem falso positivo/negativo);
- Taxa de sucesso na compilação do código corrigido;
- Comparação manual ou automatizada da lógica preservada.

### ⚠️ Limitações (Robustez e Generalização)

- Testes com vulnerabilidades mais raras ou fora das 3 principais categorias;
- Avaliação do impacto da escolha do LLM (ex: GPT-3.5 vs GPT-4o);
- Avaliação da capacidade de reparo em códigos maiores ou com lógica mais complexa.

---

## 👥 Equipe

- Jônatas Ferreira da Silva ([Jonatas-jfs8](https://github.com/Jonatas-jfs8))
- Mateus Viégas Martins Farias ([mattvie](https://github.com/mattvie))
- Rodrigo Almeida Bezerra Duarte ([rod-duarte](https://github.com/rod-duarte))
- Tomás Nascimento Santos ([TomasNsantos](https://github.com/TomasNsantos))

Este projeto é parte da disciplina de TAES, com o objetivo de investigar contribuições práticas da IA generativa para atividades do ciclo de vida do software.

[Slides da apresentação](https://docs.google.com/presentation/d/1D0Z2DrppGIy9OxlaDCWCeTzLQ6-ENBouxu_7Nmo47DM/).

---

## 🔐 Configuração da API da OpenAI (Uso Seguro)

Este projeto utiliza a API da OpenAI para realizar tarefas de detecção e reparo de vulnerabilidades. Para garantir segurança e boas práticas:

### ✅ 1. **Nunca exponha sua chave no código**

Jamais insira sua chave diretamente no código Python. Use variáveis de ambiente via `.env`.

### ⚙️ 2. Como configurar sua chave localmente

```python
#### a) Crie um arquivo `.env` na raiz do projeto:


cp .env.example .env


#### b) Adicione sua chave real no .env

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_BASE=https://api.openai.com/v1

#### c) Rode o projeto normalmente
 O carregamento da chave é feito automaticamente via config.py


