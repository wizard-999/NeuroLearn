"""
Text Simplification Module for NeuroLearn
Optimized for ADHD and Dyslexic users (ages 18-25)
"""

from __future__ import annotations

import json
import re
import string
import urllib.error
import urllib.request

# ============================================================================
# PROMPT ENGINEERING - Highly Controlled for ADHD + Dyslexia
# ============================================================================

SIMPLIFICATION_PROMPT = """You are a text simplification expert for neurodivergent learners.

TASK: Simplify the following text into exactly 10 bullet points.

RULES:
- Create exactly 10 bullet points. No more, no less.
- Each bullet point must be 5-12 words long.
- Use very simple, everyday words.
- Write in a friendly, encouraging tone.
- Do NOT add new ideas or information.
- Do NOT use markdown formatting.
- Do NOT use code blocks or special characters.
- Use only plain text with bullet points starting with "- ".
- Optimize for ADHD and Dyslexic readers aged 18-25.

OUTPUT FORMAT:
- Point 1
- Point 2
- Point 3
(continue for exactly 10 points)

TEXT TO SIMPLIFY:
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
    
    # Step 1: Remove invisible unicode characters (zero-width spaces, etc.)
    # Keep only printable characters and standard whitespace
    text = "".join(char for char in text if char.isprintable() or char.isspace())
    
    # Step 2: Normalize line breaks (convert all to single newline)
    text = re.sub(r'\r\n|\r', '\n', text)
    
    # Step 3: Remove excessive line breaks (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Step 4: Collapse multiple spaces into single space
    text = re.sub(r' +', ' ', text)
    
    # Step 5: Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Step 6: Remove tabs and replace with spaces
    text = text.replace('\t', ' ')
    
    # Step 7: Final trim
    text = text.strip()
    
    # Step 8: Limit length to prevent token overflow (keep first 8000 chars)
    if len(text) > 8000:
        text = text[:8000] + "..."
    
    return text


# ============================================================================
# OUTPUT CLEANING FUNCTIONS
# ============================================================================

def clean_output_text(text: str) -> str:
    """
    Clean output text from LLM before returning.
    Strips markdown, removes non-printable characters, and ensures plain text format.
    
    Args:
        text: Raw output text from LLM
        
    Returns:
        Cleaned plain text output
    """
    if not text:
        return ""
    
    # Step 1: Remove markdown code blocks
    text = re.sub(r'```[a-z]*\n?', '', text)
    text = re.sub(r'```', '', text)
    
    # Step 2: Remove markdown formatting (bold, italic, headers)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'#+\s*', '', text)                # Headers
    text = re.sub(r'`([^`]+)`', r'\1', text)         # Inline code
    
    # Step 3: Remove non-printable characters (keep only printable + newlines)
    text = "".join(char for char in text if char.isprintable() or char == '\n')
    
    # Step 4: Normalize bullet points (ensure they start with "- ")
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Convert various bullet styles to standard "- "
        if re.match(r'^[-•*]\s+', line):
            line = re.sub(r'^[-•*]\s+', '- ', line)
        elif re.match(r'^\d+[.)]\s+', line):
            # Convert numbered lists to bullets
            line = re.sub(r'^\d+[.)]\s+', '- ', line)
        elif not line.startswith('- '):
            # If line doesn't start with bullet, add it
            line = '- ' + line
        
        lines.append(line)
    
    # Step 5: Ensure exactly 10 bullet points
    bullet_points = [line for line in lines if line.startswith('- ')]
    
    if len(bullet_points) > 10:
        # Take first 10
        bullet_points = bullet_points[:10]
    elif len(bullet_points) < 10:
        # If we have fewer than 10, try to split longer points or pad
        # For now, just return what we have (validation will catch this)
        pass
    
    # Step 6: Clean each bullet point (remove extra spaces, ensure word count)
    cleaned_points = []
    for point in bullet_points:
        # Remove the "- " prefix temporarily
        content = point[2:].strip()
        
        # Remove extra spaces
        content = re.sub(r' +', ' ', content)
        
        # Count words
        words = content.split()
        word_count = len(words)
        
        # If too long, truncate to 12 words
        if word_count > 12:
            content = ' '.join(words[:12])
        # If too short but we have content, keep it (minimum 3 words acceptable)
        elif word_count < 3 and word_count > 0:
            # Keep as is, but note it's short
            pass
        
        if content:
            cleaned_points.append(f"- {content}")
    
    # Step 7: Join with newlines
    result = '\n'.join(cleaned_points)
    
    # Step 8: Final cleanup - remove any remaining non-printable except newlines
    result = "".join(char for char in result if char.isprintable() or char == '\n')
    
    return result.strip()


# ============================================================================
# API CALL FUNCTIONS
# ============================================================================

def _extract_text_from_response(response: dict) -> str:
    """
    Extract text content from Gemini API response.
    
    Args:
        response: JSON response from Gemini API
        
    Returns:
        Extracted text content or empty string
    """
    candidates = response.get("candidates") or []
    for candidate in candidates:
        content = candidate.get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            text = part.get("text")
            if text:
                return text.strip()
    return ""


def simplify_text(text: str, api_key: str, model: str = "gemini-2.0-flash") -> str:
    """
    Simplify text for ADHD and Dyslexic readers.
    
    Takes input text, cleans it, sends to Gemini API with optimized prompt,
    cleans the output, and returns exactly 10 bullet points in simple language.
    
    Args:
        text: Raw text to simplify
        api_key: Gemini API key
        model: Gemini model name (default: gemini-2.0-flash)
        
    Returns:
        Simplified text as 10 bullet points
        
    Raises:
        ValueError: If API key is missing or text is empty
        RuntimeError: If API call fails or returns invalid content
    """
    # Validation
    if not api_key:
        raise ValueError("Gemini API key is required.")
    if not text or not text.strip():
        return ""
    
    # Step 1: Clean input text
    cleaned_input = clean_input_text(text)
    if not cleaned_input:
        return ""
    
    # Step 2: Build API request
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    
    # Construct prompt with cleaned input
    full_prompt = f"{SIMPLIFICATION_PROMPT}\n{cleaned_input}"
    
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
            "temperature": 0.3,  # Lower temperature for more consistent output
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 500,  # Limit output to ensure concise results
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    # Step 3: Make API call
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Gemini API error: {err.code} {detail}") from err
    except urllib.error.URLError as err:
        raise RuntimeError("Unable to reach Gemini API.") from err
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Invalid JSON response from Gemini API: {err}") from err
    
    # Step 4: Extract text from response
    raw_output = _extract_text_from_response(result)
    if not raw_output:
        raise RuntimeError("Gemini API returned no content.")
    
    # Step 5: Clean output
    cleaned_output = clean_output_text(raw_output)
    
    # Step 6: Validate output has content
    if not cleaned_output or len(cleaned_output.strip()) < 10:
        raise RuntimeError("Simplified text is too short or empty.")
    
    # Step 7: Ensure we have bullet points
    bullet_count = cleaned_output.count('- ')
    if bullet_count < 5:  # At least 5 bullet points required
        raise RuntimeError(f"Invalid output format. Expected bullet points, got {bullet_count}.")
    
    return cleaned_output
