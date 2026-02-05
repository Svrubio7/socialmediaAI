"""
Chat endpoint for Strategies conversational UI.
Accepts messages, calls LLM with tool definitions, executes tools (MCP-style), returns message + cards.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.services.chat_tools import TOOL_DEFINITIONS, execute_tool

router = APIRouter()


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    """Chat request schema."""
    messages: List[ChatMessage]
    session_id: Optional[str] = None


class CardPayload(BaseModel):
    """Result card for frontend."""
    type: str  # "schedule" | "script" | "strategy" | "oauth"
    payload: Dict[str, Any]


class ChatResponse(BaseModel):
    """Chat response schema."""
    message: str
    cards: List[CardPayload] = []


SYSTEM_PROMPT = """You are a marketing strategist assistant for ElevoAI. The user can ask you to:
- List or schedule posts, reschedule or cancel scheduled posts
- Create or list scripts and strategies
- List videos and patterns
- Connect social accounts (you can provide the connection URL)

Use the available tools to perform actions. When you use a tool, summarize what you did in a short reply. Be concise and helpful. Do not use emojis."""


def _looks_like_placeholder_key(api_key: str) -> bool:
    key = (api_key or "").strip().lower()
    if not key:
        return True
    return key in {"your-openai-key", "your-openai-api-key"} or key.startswith("your-")


def _openai_tool_definitions() -> List[Dict[str, Any]]:
    """Convert TOOL_DEFINITIONS to OpenAI API format."""
    return [
        {
            "type": "function",
            "function": {
                "name": d["function"]["name"],
                "description": d["function"]["description"],
                "parameters": d["function"].get("parameters", {"type": "object", "properties": {}}),
            },
        }
        for d in TOOL_DEFINITIONS
    ]


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send messages to the LLM; tools are executed when the LLM requests them.
    Returns the assistant message and any result cards (schedule, script, strategy, oauth).
    """
    api_key = (settings.OPENAI_API_KEY or "").strip()
    if _looks_like_placeholder_key(api_key):
        return ChatResponse(
            message="Chat is not configured. Set OPENAI_API_KEY to use the assistant.",
            cards=[],
        )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    if not any(m.get("role") == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    cards: List[CardPayload] = []
    max_tool_rounds = 5
    tool_round = 0

    while tool_round < max_tool_rounds:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=_openai_tool_definitions(),
                tool_choice="auto",
            )
        except Exception as e:
            if "invalid_api_key" in str(e).lower() or "incorrect api key" in str(e).lower():
                return ChatResponse(
                    message="Chat is not configured. Set a valid OPENAI_API_KEY to use the assistant.",
                    cards=[],
                )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM request failed: {str(e)}",
            )

        choice = response.choices[0] if response.choices else None
        if not choice:
            return ChatResponse(message="No response from assistant.", cards=cards)

        msg = choice.message
        if msg.content:
            return ChatResponse(message=(msg.content or "").strip(), cards=cards)

        if not getattr(msg, "tool_calls", None):
            return ChatResponse(message="Assistant did not return text.", cards=cards)

        import json
        tool_calls = msg.tool_calls
        messages.append({
            "role": "assistant",
            "content": msg.content or None,
            "tool_calls": [
                {
                    "id": getattr(tc, "id", ""),
                    "type": "function",
                    "function": {
                        "name": getattr(tc.function, "name", None) or (tc.get("function") or {}).get("name"),
                        "arguments": getattr(tc.function, "arguments", None) or (tc.get("function") or {}).get("arguments", "{}"),
                    },
                }
                for tc in tool_calls
            ],
        })
        for tc in tool_calls:
            name = getattr(tc.function, "name", None) or (tc.get("function") or {}).get("name")
            args_str = getattr(tc.function, "arguments", None) or (tc.get("function") or {}).get("arguments", "{}")
            if not name:
                continue
            try:
                arguments = json.loads(args_str) if isinstance(args_str, str) else (args_str or {})
            except Exception:
                arguments = {}
            try:
                out = await execute_tool(name, arguments, db, current_user)
            except ValueError as e:
                messages.append({"role": "tool", "tool_call_id": getattr(tc, "id", ""), "content": str(e)})
                continue
            result_str = json.dumps(out.get("result")) if isinstance(out.get("result"), (dict, list)) else str(out.get("result"))
            messages.append({"role": "tool", "tool_call_id": getattr(tc, "id", ""), "content": result_str})
            if out.get("card_type") and out.get("card_payload"):
                cards.append(CardPayload(type=out["card_type"], payload=out["card_payload"]))

        tool_round += 1

    return ChatResponse(message="Assistant is thinking. Try again.", cards=cards)
