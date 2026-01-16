# Non-Coercive Superintelligence (REI)

I just finished reading the first chapter of "Introduction to AI Engineering" by O'Reilly, and I decided to stop just reading and actually build something. I wanted to take the concepts of capabilities and control and implement them into a system that actually respects me.

This isn't just another chatbot wrapper. It is an experiment in digital sovereignty which I call **rei**.

## The Concept

The core idea I'm exploring here is what happens when you don't trust a single model blindly. We know LLMs hallucinate and can be weirdly manipulative if trained that way. So instead of one model, I built a Council.

I have two distinct AIs running in parallel:
1. **Groq (LPU)** for speed and reasoning
2. **Ollama (running locally)** for privacy checks

## How It Works

When I type a command, it doesn't just go to a server and back.

First, the Council convenes. Both models come up with an answer independently. Then I have an **Auditor script** that scans their responses for any "soft coercion" or manipulative language. If it smells like the AI is trying to gaslight me or nudge me into something I didn't ask for, the Auditor flags it.

Finally, there's the Memory. This is the coolest part. I hooked up a local vector database (ChromaDB) that remembers my boundaries. If I reject an answer, rei remembers that specific context. It won't try to cross that line again. It's a system that learns to respect my "No."

## Setup

It's a Python CLI because I wanted to keep it clean and focused on the engineering, not the UI.

You'll need `ollama` running with `llama3.2:1b` (or whatever local model you prefer).

```bash
pip install -r requirements.txt
python src/app.py
```

That's it. No fancy dashboards, just a terminal that listens.
