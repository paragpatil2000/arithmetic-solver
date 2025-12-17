# arithmetic_solver.py
import os
import re
import requests
from dotenv import load_dotenv
  
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_API_BASE")
MODEL = os.getenv("GROQ_MODEL","llama-3.1-8b-instant")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# -------------------------
# ADVANCED RULE-BASED SOLVER
# -------------------------
def rule_based_solver(text):
    numbers = list(map(int, re.findall(r'\d+', text)))
    t = text.lower()

    if len(numbers) == 0:
        return None

    # Addition
    if any(word in t for word in ["add", "plus", "total"]):
        return sum(numbers)

    # Multi-step subtraction
    if any(word in t for word in ["left", "remain", "remaining", "spoiled", "eaten", "lost"]):
        total = numbers[0]
        for n in numbers[1:]:
            total -= n
        return total

    # Division
    if "divide" in t or "each" in t:
        if len(numbers) >= 2 and numbers[1] != 0:
            return numbers[0] / numbers[1]

    # Multiplication
    if any(word in t for word in ["times", "multiply"]):
        result = 1
        for n in numbers:
            result *= n
        return result

    return None


# -------------------------
# CALL GROQ API
#...existing code...
def call_groq(problem):
    url = BASE_URL.rstrip('/') + "/chat/completions"

    prompt = f"""
You are a precise arithmetic calculator.
Rules:
1. Solve exact math only.
2. Do not guess.
3. Show step-by-step reasoning.
4. Final line MUST be: Answer: <number>

Problem: {problem}
"""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 200,
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=15)
    except requests.RequestException as e:
        raise RuntimeError(f"GROQ request failed: {e}")

    if response.status_code // 100 != 2:
        # include response text for debugging (safe to log; avoid exposing API key)
        raise RuntimeError(f"GROQ API error {response.status_code}: {response.text}")

    try:
        return response.json()
    except ValueError:
        raise RuntimeError("GROQ response is not valid JSON")
# ...existing code...

# -------------------------
# PARSE ANSWER
# -------------------------
def parse_answer(resp):
    content = resp["choices"][0]["message"]["content"]

    m = re.search(r"Answer[:\-\s]+\s*(-?\d+(?:\.\d+)?)", content)
    if m:
        return content, m.group(1)

    numbers = re.findall(r"-?\d+(?:\.\d+)?", content)
    if numbers:
        return content, numbers[-1]

    return content, None


# -------------------------
# MAIN SOLVER
# -------------------------
def solve(problem):
    r = rule_based_solver(problem)
    if r is not None:
        return {
            "method": "rule",
            "problem": problem,
            "raw": str(r),
            "answer": str(r)
        }

    resp = call_groq(problem)
    raw_text, ans = parse_answer(resp)

    return {
        "method": "llm",
        "problem": problem,
        "raw": raw_text,
        "answer": ans
    }


# LOCAL TEST
if __name__ == "__main__":
    print(solve("A bag has 50 mangoes, 12 spoiled, 8 eaten. How many left?"))
