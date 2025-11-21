"""
Quiz Generation Module for NeuroLearn
Optimized for ADHD and Dyslexic users (ages 18-25)
"""

from __future__ import annotations

import json
import re
import string
import urllib.error
import urllib.request
from typing import Any, Dict, List

# ============================================================================
# PROMPT ENGINEERING - Strict JSON Output for Reliable Parsing
# ============================================================================

QUIZ_PROMPT = """You are a quiz generator for neurodivergent learners.

TASK: Create a quiz from the provided text.

RULES:
- Output ONLY valid JSON. No markdown, no explanations, no code fences.
- Use simple, everyday words suitable for ages 18-25.
- Create exactly 3 multiple-choice questions (MCQ).
- Create exactly 2 short-answer questions.
- Each MCQ must have exactly 4 options.
- Keep questions and answers short and clear.
- Do NOT use markdown formatting.
- Do NOT wrap JSON in code blocks.
- Do NOT add any text before or after the JSON.

REQUIRED JSON STRUCTURE:
{
  "mcq": [
    {"q": "question text", "options": ["option1", "option2", "option3", "option4"], "answer": "correct option"},
    {"q": "question text", "options": ["option1", "option2", "option3", "option4"], "answer": "correct option"},
    {"q": "question text", "options": ["option1", "option2", "option3", "option4"], "answer": "correct option"}
  ],
  "short": [
    {"q": "question text", "answer": "answer text"},
    {"q": "question text", "answer": "answer text"}
  ]
}

TEXT TO CREATE QUIZ FROM:
"""


# ============================================================================
# INPUT CLEANING FUNCTIONS
# ============================================================================

def clean_input_text(text: str) -> str:
    """
    Clean input text before sending to LLM.
    Removes excessive whitespace, broken line breaks, invisible unicode, and collapses spaces.
    
    Args:
        text: Raw input text to clean
        
    Returns:
        Cleaned text ready for LLM processing
    """
    if not text:
        return ""
    
    # Step 1: Remove invisible unicode characters
    text = "".join(char for char in text if char.isprintable() or char.isspace())
    
    # Step 2: Normalize line breaks
    text = re.sub(r'\r\n|\r', '\n', text)
    
    # Step 3: Remove excessive line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Step 4: Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Step 5: Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Step 6: Remove tabs
    text = text.replace('\t', ' ')
    
    # Step 7: Final trim
    text = text.strip()
    
    # Step 8: Limit length (keep first 10000 chars for quiz generation)
    if len(text) > 10000:
        text = text[:10000] + "..."
    
    return text


# ============================================================================
# OUTPUT CLEANING FUNCTIONS
# ============================================================================

def clean_json_output(text: str) -> str:
    """
    Clean JSON output from LLM before parsing.
    Strips markdown, removes non-printable characters, and extracts JSON.
    
    Args:
        text: Raw output text from LLM
        
    Returns:
        Cleaned JSON string ready for parsing
    """
    if not text:
        return ""
    
    # Step 1: Remove markdown code blocks (```json ... ``` or ``` ... ```)
    text = re.sub(r'```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*', '', text)
    
    # Step 2: Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'#+\s*', '', text)                # Headers
    text = re.sub(r'`([^`]+)`', r'\1', text)         # Inline code
    
    # Step 3: Remove leading/trailing explanatory text
    # Find the first { and last }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]
    
    # Step 4: Remove non-printable characters (keep JSON-safe characters)
    # Allow: letters, digits, spaces, and JSON punctuation: {}[]",:-
    allowed_chars = set(string.ascii_letters + string.digits + ' \n\t{}[]",:-')
    text = "".join(char for char in text if char in allowed_chars or char.isprintable())
    
    # Step 5: Remove extra whitespace around JSON structure
    text = text.strip()
    
    # Step 6: Ensure it starts with { and ends with }
    if not text.startswith('{'):
        # Try to find JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
    
    return text


# ============================================================================
# JSON REPAIR FUNCTIONS
# ============================================================================

def repair_json(text: str) -> str:
    """
    Attempt to repair malformed JSON using regex-based bracket matching.
    This is a fallback when standard JSON parsing fails.
    
    Args:
        text: Potentially malformed JSON string
        
    Returns:
        Repaired JSON string (may still be invalid)
    """
    if not text:
        return "{}"
    
    # Step 1: Find the JSON object boundaries
    start_idx = text.find('{')
    if start_idx == -1:
        return "{}"
    
    # Step 2: Find matching closing brace
    brace_count = 0
    end_idx = start_idx
    
    for i in range(start_idx, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    if brace_count != 0:
        # Unbalanced braces - try to fix by adding closing brace
        if brace_count > 0:
            text = text[:end_idx] + '}' * brace_count
            end_idx = len(text)
        else:
            # Too many closing braces - truncate
            end_idx = start_idx + 1
            while end_idx < len(text) and text[end_idx] != '}':
                end_idx += 1
            if end_idx < len(text):
                end_idx += 1
    
    json_candidate = text[start_idx:end_idx]
    
    # Step 3: Fix common JSON issues
    
    # Fix unquoted keys
    json_candidate = re.sub(r'(\w+):', r'"\1":', json_candidate)
    
    # Fix single quotes to double quotes
    json_candidate = re.sub(r"'([^']*)'", r'"\1"', json_candidate)
    
    # Fix trailing commas
    json_candidate = re.sub(r',\s*}', '}', json_candidate)
    json_candidate = re.sub(r',\s*]', ']', json_candidate)
    
    # Fix missing commas between objects
    json_candidate = re.sub(r'}\s*{', '},{', json_candidate)
    json_candidate = re.sub(r']\s*\[', '],[', json_candidate)
    
    return json_candidate


def extract_json_safely(text: str) -> dict:
    """
    Safely extract JSON from LLM output with multiple fallback strategies.
    
    Args:
        text: Raw output text from LLM
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        RuntimeError: If JSON cannot be extracted or parsed
    """
    if not text:
        raise RuntimeError("Empty response from LLM.")
    
    # Strategy 1: Clean and parse directly
    cleaned = clean_json_output(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Try to find JSON object using regex
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Try bracket matching to extract JSON
    start_idx = cleaned.find('{')
    if start_idx != -1:
        brace_count = 0
        end_idx = start_idx
        for i in range(start_idx, len(cleaned)):
            if cleaned[i] == '{':
                brace_count += 1
            elif cleaned[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if brace_count == 0:
            json_candidate = cleaned[start_idx:end_idx]
            try:
                return json.loads(json_candidate)
            except json.JSONDecodeError:
                pass
    
    # Strategy 4: Try JSON repair
    repaired = repair_json(cleaned)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError as err:
        raise RuntimeError(
            f"Failed to parse JSON after all repair attempts. "
            f"Error: {err}. Raw text (first 500 chars): {text[:500]}"
        ) from err


# ============================================================================
# API CALL FUNCTIONS
# ============================================================================

def _call_gemini(text: str, api_key: str) -> dict:
    """
    Call Gemini API to generate quiz.
    
    Args:
        text: Cleaned input text
        api_key: Gemini API key
        
    Returns:
        Parsed quiz dictionary
        
    Raises:
        RuntimeError: If API call fails or returns invalid content
    """
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash:generateContent"
        f"?key={api_key}"
    )
    
    # Construct prompt with cleaned input
    full_prompt = f"{QUIZ_PROMPT}\n{text}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,  # Low temperature for consistent JSON structure
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2000,  # Enough for quiz JSON
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_data = response.read().decode("utf-8")
            if not response_data:
                raise RuntimeError("Gemini API returned empty response.")
            
            result = json.loads(response_data)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Gemini API returned invalid JSON response: {err}") from err
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Gemini API HTTP error: {err.code} {detail}") from err
    except urllib.error.URLError as err:
        raise RuntimeError("Unable to reach Gemini API.") from err
    
    # Extract text from response
    candidates = result.get("candidates") or []
    for candidate in candidates:
        parts = candidate.get("content", {}).get("parts", [])
        for part in parts:
            text_content = part.get("text")
            if text_content:
                # Use safe JSON extraction
                return extract_json_safely(text_content)
    
    raise RuntimeError("Gemini returned no quiz content.")


def _call_openai(text: str, api_key: str) -> dict:
    """
    Call OpenAI API to generate quiz.
    
    Args:
        text: Cleaned input text
        api_key: OpenAI API key
        
    Returns:
        Parsed quiz dictionary
        
    Raises:
        RuntimeError: If API call fails or returns invalid content
    """
    endpoint = "https://api.openai.com/v1/chat/completions"
    
    # Construct prompt with cleaned input
    full_prompt = f"{QUIZ_PROMPT}\n{text}"
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a quiz generator. Always respond with valid JSON only. No markdown, no explanations."
            },
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        "temperature": 0.2,  # Low temperature for consistent JSON
        "response_format": {"type": "json_object"},  # Force JSON mode if supported
    }
    
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_data = response.read().decode("utf-8")
            if not response_data:
                raise RuntimeError("OpenAI API returned empty response.")
            
            result = json.loads(response_data)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"OpenAI API returned invalid JSON response: {err}") from err
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "ignore")
        raise RuntimeError(f"OpenAI API HTTP error: {err.code} {detail}") from err
    except urllib.error.URLError as err:
        raise RuntimeError("Unable to reach OpenAI API.") from err
    
    # Extract content from response
    choices = result.get("choices") or []
    for choice in choices:
        message = choice.get("message", {})
        content = message.get("content")
        if content:
            # Use safe JSON extraction
            return extract_json_safely(content)
    
    raise RuntimeError("OpenAI returned no quiz content.")


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def _validate_quiz(quiz: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Validate and clean quiz structure.
    
    Args:
        quiz: Raw quiz dictionary from API
        
    Returns:
        Validated and cleaned quiz dictionary
        
    Raises:
        RuntimeError: If quiz structure is invalid or incomplete
    """
    # Ensure required keys exist
    quiz.setdefault("mcq", [])
    quiz.setdefault("short", [])
    
    # Validate and clean MCQ
    valid_mcq = []
    for q in quiz.get("mcq", []):
        if not isinstance(q, dict):
            continue
        
        question = q.get("q", "").strip()
        options = q.get("options", [])
        answer = q.get("answer", "").strip()
        
        # Validate MCQ structure
        if (question and 
            isinstance(options, list) and 
            len(options) >= 2 and 
            answer and 
            answer in options):
            valid_mcq.append({
                "q": question,
                "options": options[:4],  # Limit to 4 options max
                "answer": answer
            })
    
    # Validate and clean short answer
    valid_short = []
    for q in quiz.get("short", []):
        if not isinstance(q, dict):
            continue
        
        question = q.get("q", "").strip()
        answer = q.get("answer", "").strip()
        
        # Validate short answer structure
        if question and answer:
            valid_short.append({
                "q": question,
                "answer": answer
            })
    
    # Ensure we have the required minimum
    if len(valid_mcq) < 3:
        raise RuntimeError(
            f"Quiz incomplete: Expected at least 3 MCQs, got {len(valid_mcq)}."
        )
    
    if len(valid_short) < 2:
        raise RuntimeError(
            f"Quiz incomplete: Expected at least 2 short-answer questions, got {len(valid_short)}."
        )
    
    return {
        "mcq": valid_mcq[:3],  # Take first 3 MCQs
        "short": valid_short[:2]  # Take first 2 short answers
    }


# ============================================================================
# MAIN PUBLIC FUNCTION
# ============================================================================

def generate_quiz(text: str, api_key: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate a quiz from text using Gemini or OpenAI API.
    
    This function handles input cleaning, API calls, output cleaning,
    JSON parsing with fallback repair, and validation.
    
    Args:
        text: Raw text to generate quiz from
        api_key: API key (Gemini or OpenAI)
        
    Returns:
        Validated quiz dictionary with structure:
        {
            "mcq": [{"q": "...", "options": [...], "answer": "..."}, ...],
            "short": [{"q": "...", "answer": "..."}, ...]
        }
        
    Raises:
        ValueError: If API key is missing
        RuntimeError: If API call fails, JSON parsing fails, or quiz is invalid
    """
    # Validation
    if not api_key:
        raise ValueError("API key required.")
    if not text or not text.strip():
        return {"mcq": [], "short": []}
    
    # Step 1: Clean input text
    cleaned_input = clean_input_text(text)
    if not cleaned_input:
        return {"mcq": [], "short": []}
    
    # Step 2: Determine API provider and call
    try:
        if api_key.startswith("sk-"):
            quiz = _call_openai(cleaned_input, api_key)
        else:
            quiz = _call_gemini(cleaned_input, api_key)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "ignore")
        raise RuntimeError(f"LLM API error: {err.code} {detail}") from err
    except urllib.error.URLError as err:
        raise RuntimeError("Unable to reach LLM API.") from err
    
    # Step 3: Validate quiz structure
    validated_quiz = _validate_quiz(quiz)
    
    return validated_quiz
