from typing import List, Dict, Any, Tuple, Optional
from app.schemas import Message


def to_openai_format(
    messages: List[Message],
    system_prompt: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Format standard messages for OpenAI Chat Completions API.
    Format: [{'role': 'system'|'user'|'assistant', 'content': '...'}]
    """
    formatted = []
    
    # Prepend system prompt if provided
    if system_prompt and system_prompt.strip():
        formatted.append({"role": "system", "content": system_prompt.strip()})
        
    for msg in messages:
        if msg.role == "system" and not system_prompt:
            formatted.append({"role": "system", "content": msg.content})
        elif msg.role in ["user", "assistant"]:
            formatted.append({"role": msg.role, "content": msg.content})
            
    return formatted


def to_claude_format(
    messages: List[Message],
    system_prompt: Optional[str] = None
) -> Tuple[Optional[str], List[Dict[str, str]]]:
    """
    Format standard messages for Anthropic Claude API.
    - Extracts system message into a separate system parameter.
    - Messages list only accepts 'user' and 'assistant' roles.
    - Merges consecutive messages of the same role.
    """
    extracted_system = system_prompt.strip() if system_prompt else None
    system_parts = [extracted_system] if extracted_system else []
    
    raw_chat = []
    for msg in messages:
        if msg.role == "system":
            if msg.content.strip():
                system_parts.append(msg.content.strip())
        elif msg.role in ["user", "assistant"]:
            raw_chat.append({"role": msg.role, "content": msg.content})

    final_system = "\n\n".join(system_parts) if system_parts else None

    # Merge consecutive same-role messages to satisfy Anthropic requirements
    merged_messages: List[Dict[str, str]] = []
    for msg in raw_chat:
        if merged_messages and merged_messages[-1]["role"] == msg["role"]:
            merged_messages[-1]["content"] += f"\n\n{msg['content']}"
        else:
            merged_messages.append({"role": msg["role"], "content": msg["content"]})

    # Anthropic requires the first message to be from the 'user'
    if merged_messages and merged_messages[0]["role"] == "assistant":
        merged_messages.insert(0, {"role": "user", "content": "Hello"})

    return final_system, merged_messages


def to_gemini_format(
    messages: List[Message],
    system_prompt: Optional[str] = None
) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Format standard messages for Google GenAI / Gemini API.
    - Extracts system message to system_instruction.
    - Converts role 'assistant' -> 'model', 'user' -> 'user'.
    - Formats contents as [{'role': 'user'|'model', 'parts': [{'text': '...'}]}]
    - Merges consecutive same-role messages.
    """
    extracted_system = system_prompt.strip() if system_prompt else None
    system_parts = [extracted_system] if extracted_system else []
    
    raw_chat = []
    for msg in messages:
        if msg.role == "system":
            if msg.content.strip():
                system_parts.append(msg.content.strip())
        elif msg.role in ["user", "assistant"]:
            role = "model" if msg.role == "assistant" else "user"
            raw_chat.append({"role": role, "content": msg.content})

    final_system = "\n\n".join(system_parts) if system_parts else None

    # Merge consecutive same-role messages
    merged_chat: List[Dict[str, Any]] = []
    for msg in raw_chat:
        if merged_chat and merged_chat[-1]["role"] == msg["role"]:
            merged_chat[-1]["parts"][0]["text"] += f"\n\n{msg['content']}"
        else:
            merged_chat.append({
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            })

    # Gemini requires the first message to be from 'user'
    if merged_chat and merged_chat[0]["role"] == "model":
        merged_chat.insert(0, {
            "role": "user",
            "parts": [{"text": "Hello"}]
        })

    return final_system, merged_chat
