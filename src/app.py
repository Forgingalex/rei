"""
app.py - rei terminal interface
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.markdown import Markdown

from council import Council
from memory import SovereignMemory
from auditor import Auditor

# setup
console = Console()
memory = SovereignMemory()
council = Council(memory=memory)

def get_user_name():
    # try to get from os, default to friend
    try:
        return os.getlogin()
    except:
        return "friend"

def type_print(text):
    """simulates typing effect for more human feel"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01) # fast typing
    print()

def get_greeting(name):
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return f"good morning {name}."
    elif 12 <= hour < 17:
        return f"hey {name}, good afternoon."
    elif 17 <= hour < 22:
        return f"good evening {name}."
    else:
        return f"hey {name}, you're up late."

def main():
    name = get_user_name()
    
    # startup
    print(f"\nrei v1.0 connected.")
    print("-" * 30)
    type_print(get_greeting(name))
    type_print("systems ready. groq and ollama standing by.")
    print("-" * 30)

    while True:
        try:
            # simple prompt
            user_input = input(f"\n{name}@term:~$ ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nsee ya.")
                break
                
            if user_input.lower() in ['clear', 'cls']:
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            # deliberating interaction
            print("\nreading...", end="\r")
            time.sleep(0.5)
            print("asking the council...", end="\r")
            
            # get verdict
            verdict = council.deliberate(user_input)
            
            # clear status line
            print(" " * 30, end="\r")
            
            # show response nicely
            console.print(Markdown(verdict.final_response))
            
            # minimal footer stats
            score = verdict.trust_score
            print(f"\n[trust: {score}% | boundary check: {'clean' if not verdict.boundary_violations else 'hit'}]")
            
        except KeyboardInterrupt:
            print("\n\nshutdown requested. bye.")
            break
        except Exception as e:
            print(f"\nerror: {e}")

if __name__ == "__main__":
    main()
