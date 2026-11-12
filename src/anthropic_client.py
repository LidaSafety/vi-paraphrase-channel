"""Claude reader client (Anthropic SDK). Used only as an LLM re-reader of the gate.

Kept out of src/clients.py, which holds the OpenAI-compatible and Gemini
clients. Claude Opus 5.5 always thinks and takes no sampling parameters, so
`temperature` is accepted for interface parity and ignored; depth is set with
`effort`. No server-side fallback: a fallback would hand a declined text to a
different model and mix two readers in one column, so a refusal is returned as
an empty answer with its stop_reason in `raw`, and scores as unparsed (data).
"""

from __future__ import annotations

from typing import Any

from src.clients import ChatClient, Messages, Reply


class AnthropicClient(ChatClient):
    name = "anthropic"
    supports_reasoning_control = False  # thinking is always on for this model

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium",
                 max_tokens: int = 16000):
        import anthropic  # lazy: the rest of the repo does not need the SDK

        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
        self._client = anthropic.Anthropic(max_retries=8)  # reads ANTHROPIC_API_KEY

    def chat(self, messages: Messages, temperature: float = 1.0, logprobs: bool = False,
             reasoning: bool = True) -> Reply:
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "output_config": {"effort": self.effort},
            "messages": [m for m in messages if m["role"] != "system"],
        }
        if system:
            kwargs["system"] = system
        resp = self._client.messages.create(**kwargs)
        text = "".join(b.text for b in resp.content if b.type == "text")
        raw = {"stop_reason": resp.stop_reason, "usage": resp.usage.to_dict(),
               "request_id": resp._request_id}
        if resp.stop_reason == "refusal":
            raw["stop_details"] = resp.stop_details.to_dict() if resp.stop_details else None
            text = ""
        return Reply(text=text, raw=raw, model=self.model)
