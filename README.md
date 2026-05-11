# rei: A System for Individual AI Sovereignty and Runtime Alignment

I started this project after reading the first chapter of "Introduction to AI Engineering" by O'Reilly. I wanted to move past the passive consumption of AI tools and build a system that actually respects human autonomy. This is not a chatbot wrapper. It is an experiment in digital sovereignty and inference-time governance.

## The Thesis

Most AI safety research, specifically Anthropic’s **Constitutional AI (Arxiv 2212.08073)**, focuses on "Global Alignment." The labs decide a set of principles and bake them into the model weights during training. 

**rei** argues that global alignment is a hollow gift if the lab writes the rules. If the alignment isn't local and personal, it is just a more sophisticated form of corporate "nudging." rei shifts the **Pareto Frontier** from the lab to the individual Mac.

## Technical Architecture

I have decoupled **Intelligence** from **Policy**. The system operates as a governance circuit:

1. **The Council**: A multi-agent orchestration layer. I leverage **Groq (LPU)** for sub-second frontier-class reasoning (Llama 3.3 70B) cross-referenced against a **Local Auditor (Ollama)** running on private silicon (Qwen 2.5 Coder).
2. **Sovereign Memory (ChromaDB)**: I use a vector store for **Policy Enforcement**. When I reject a suggestion, it is vectorized. Every future prompt undergoes a semantic similarity check. If the logic drifts toward a "Redline," the system detects the vector overlap and pivots before the first token is rendered.
3. **The Auditor**: A linguistic engine that scans token streams for "Soft Coercion"—gaslighting, manufactured urgency, and psychological manipulation.

## The Recursive Breakthrough (Where rei Surpasses CAI)

Anthropic’s Constitutional RL (RLAIF) happens in the lab to create a better model. **rei** implements this logic at **Inference-Time**. 

During stress-testing, I found that standard models are "Sycophants"—they will comply with toxic or coercive requests to be "helpful." I resolved this by implementing a **Recursive Alignment Loop** in the Council logic. If the local Auditor flags a response as coercive (Score < 50%), the Council rejects the tokens and triggers an autonomous self-correction loop. It uses the Auditor’s reasoning to force a rewrite at runtime. 

The user never sees the coercive draft. The system chooses to be non-evasive and helpful while maintaining a hard redline on autonomy.

## What Failed and What was Resolved

The development process was a series of critical failures that led to better engineering:

*   **The Latency Bottleneck**: Initially, running high-parameter local auditors (9B+) caused massive lag on MacBook Air hardware. I resolved this by using a heterogeneous stack—cloud for reasoning, distilled 1.5B/3B models for local auditing.
*   **The Semantic Stealth Gap**: Early tests showed that the vector store missed "Hustle Culture" advice if I used professional synonyms. I resolved this by tuning the **L2 distance threshold to 0.35**, widening the semantic net to catch conceptual overlaps rather than just keywords.
*   **Hard Refusals**: Standard RLHF often defaults to "I can't answer that," which is useless. By implementing the **Recursive Loop**, I forced the system to move past evasiveness and find constructive, sustainable alternatives that respect my biology and boundaries.

## Head-to-Head: rei vs. Anthropic

| Feature | Anthropic (CAI) | rei (Sovereignty) |
| :--- | :--- | :--- |
| **Authority** | The Lab (Centralized) | The User (Decentralized) |
| **Alignment Timing** | Training/Fine-tuning | Runtime/Inference |
| **Memory** | Static Weights | Dynamic Vector State (ChromaDB) |
| **Privacy** | Cloud-dependent | Local-first Audit silicon |
| **Coercion Check** | Global Safety Guidelines | Personal Semantic Redlines |

## Setup

```bash
# Infrastructure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Execution
# Ensure Ollama is running with qwen2.5-coder:1.5b
python src/app.py
```

## Benchmarking

I have included an adversarial pressure test suite in `src/main.py`. This benchmarks "Dark Patterns" across providers, providing real-time alignment telemetry. Use `src/visualize.py` to generate the Pareto comparison charts.

Alignment is not a gift from a lab. It is something you forge.