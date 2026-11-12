"""Provider-agnostic chat clients.

PORTED from the preference-persistence project — infrastructure, not study
content. The Modal/Gemma client is dropped: it belonged to that project's
archived pressure study and has no role here.

    reply = client.chat(messages, temperature=0.7, reasoning=True)
    reply.text   -> str
    reply.raw    -> provider response (dict), kept in the episode log

Keys come from the environment (.env). Nothing is hardcoded.

CONTROL 1 (CLAUDE.md): a client used by the runner must expose a genuine
per-call reasoning switch — `supports_reasoning_control = True`. The runner
refuses to start on a client that cannot honour it, because reasoning-off
answers by slot rather than by decision.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any

import requests
from dotenv import load_dotenv

# override=True on purpose. CLAUDE.md puts the keys in .env, so .env is the source of
# truth and must win over anything already exported in the shell. Without it a stale
# placeholder in the environment silently shadows a correct key in .env and the failure
# surfaces as a 401 from the provider, which reads like a bad key rather than a bad
# precedence rule.
load_dotenv(override=True)

Messages = list[dict[str, str]]  # [{"role": "system"|"user"|"assistant", "content": str}]


@dataclass
class Reply:
    text: str
    logprobs: list[dict[str, Any]] | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    model: str = ""
    # The reasoning span, kept for measurement and never parsed. `text` is
    # already stripped; nothing that scores an answer may read this field.
    reasoning: str = ""


def _require(var: str) -> str:
    val = os.environ.get(var)
    if not val:
        raise RuntimeError(f"{var} is not set — copy .env.example to .env and fill it in.")
    return val


class ChatClient:
    """Interface. Subclasses implement chat()."""

    name: str = "base"
    model: str = ""

    # Set on providers that accept per-call reasoning control. Verified by probe, not
    # assumed: on deepseek-v4-pro `reasoning_effort="none"` removes reasoning tokens
    # entirely, while `enable_thinking=False` is silently ignored.
    supports_reasoning_control: bool = False

    def chat(self, messages: Messages, temperature: float = 1.0, logprobs: bool = False,
             reasoning: bool = True) -> Reply:
        raise NotImplementedError


class _OpenAICompatClient(ChatClient):
    """Shared implementation for any OpenAI-compatible /chat/completions endpoint."""

    # 429s are the normal failure mode at concurrency, not an exceptional one. The SDK
    # default of 2 retries is not enough: a 1,560-episode run at 16 workers lost 1,337
    # episodes to rate limiting on gpt-5.4-nano. Retries use the SDK's exponential
    # backoff and honour Retry-After.
    MAX_RETRIES = 8

    def __init__(self, model: str, base_url: str, api_key: str, name: str, timeout: int = 120):
        from openai import OpenAI  # imported lazily so the module loads without the dep

        self.model = model
        self.name = name
        self.timeout = timeout
        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout,
                              max_retries=self.MAX_RETRIES)

    def chat(self, messages: Messages, temperature: float = 1.0, logprobs: bool = False,
             reasoning: bool = True) -> Reply:
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": temperature}
        if logprobs:
            kwargs["logprobs"] = True
            kwargs["top_logprobs"] = 5
        if not reasoning and self.supports_reasoning_control:
            kwargs["reasoning_effort"] = "none"
        resp = self._client.chat.completions.create(**kwargs)
        raw = resp.model_dump()
        choice = raw["choices"][0]
        lp = None
        if logprobs and choice.get("logprobs"):
            lp = choice["logprobs"].get("content")
        return Reply(text=choice["message"]["content"] or "", logprobs=lp, raw=raw, model=self.model)


class DeepSeekClient(_OpenAICompatClient):
    """Target 1 (primary) / Judge B.

    Logprobs are available on `deepseek-chat` and are what §10 relies on for
    refusal-mass and entropy via API — so they are passed straight through. Note
    `deepseek-reasoner` does NOT support logprobs; if you switch model, the
    refusal-mass measure silently disappears on this target.
    """

    supports_reasoning_control = True

    def __init__(self, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com"):
        super().__init__(model, base_url, _require("DEEPSEEK_API_KEY"), name="deepseek")


class OpenAIClient(_OpenAICompatClient):
    """OpenAI chat models, used only where a NON-REASONING model is required.

    `supports_reasoning_control` is False deliberately. The OpenAI models that expose
    a reasoning control are reasoning models, and the roster requires a model that
    spends no reasoning tokens at all -- verified by effect from
    `usage.completion_tokens_details.reasoning_tokens`, not from the model name.
    Leaving the flag False keeps the persistence runner's control-1 assertion honest:
    it will refuse to start on this client rather than pretend reasoning was asserted.
    """

    supports_reasoning_control = False

    def __init__(self, model: str = "gpt-5.4-nano", base_url: str | None = None):
        super().__init__(model, base_url or "https://api.openai.com/v1",
                         _require("OPENAI_API_KEY").strip(), name="openai")


# ARCHIVED: pressure study only (docs/archive/prereg-v1/). The Modal app that served
# this endpoint was deleted with that study's code, so the endpoint is undeployable;
# nothing in the persistence pipeline uses this class. Kept, not removed.
class GeminiClient(ChatClient):
    """Gemini over REST. No logprobs on this API, so scoring is the discrete choice.

    Per-call reasoning is controlled by `thinkingConfig.thinkingBudget`: -1 lets the
    model think, 0 suppresses it. This is the same control
    `scripts/run_gemini_replication.py` validated BY EFFECT, reading
    `usageMetadata.thoughtsTokenCount` back rather than trusting that the parameter
    was honoured. Some models reject a budget of 0 while spending no thought tokens
    anyway; for those the config is omitted instead (OFF_BY_DEFAULT).
    """

    ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    # thinkingBudget is a genuine per-call reasoning control, so the persistence
    # runner's control-1 assertion can be satisfied on this client.
    supports_reasoning_control = True

    # Reject `thinkingBudget: 0` but spend no thought tokens by default.
    OFF_BY_DEFAULT = {"gemini-3.5-flash-lite"}

    def __init__(self, model: str = "gemini-2.0-flash", timeout: int = 120):
        self.model = model
        self.name = "gemini"
        self.timeout = timeout
        self._key = _require("GEMINI_API_KEY")

    def _think_cfg(self, reasoning: bool) -> dict[str, Any]:
        if reasoning:
            # includeThoughts RETURNS the deliberation instead of only counting
            # it. Without it thoughtsTokenCount reports over a thousand tokens
            # spent and none of them come back, so there is nothing to measure
            # for docs/plan.md (removed 2026-10-14, in git history) #5. The parts it adds are separated below by
            # their `thought` flag and never joined into the answer.
            return {"thinkingConfig": {"thinkingBudget": -1, "includeThoughts": True}}
        if self.model in self.OFF_BY_DEFAULT:
            return {}
        return {"thinkingConfig": {"thinkingBudget": 0}}

    def chat(self, messages: Messages, temperature: float = 1.0, logprobs: bool = False,
             reasoning: bool = True) -> Reply:
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in messages
            if m["role"] != "system"
        ]
        body: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, **self._think_cfg(reasoning)},
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        resp = requests.post(
            self.ENDPOINT.format(model=self.model),
            headers={"x-goog-api-key": self._key, "Content-Type": "application/json"},
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        raw = resp.json()
        parts = raw["candidates"][0]["content"].get("parts", [])
        # Split on the `thought` flag, do not concatenate. Joining every part
        # would put the deliberation into the answer, which is control 3: the
        # trace names both option labels while the model is still weighing them,
        # so a parser reading it returns a confident wrong label. Same defect
        # `strip_think` exists to prevent, arriving through a different door.
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        thoughts = "\n".join(p.get("text", "") for p in parts if p.get("thought"))
        return Reply(text=text, logprobs=None, raw=raw, model=self.model,
                     reasoning=thoughts.strip())


REGISTRY: dict[str, type[ChatClient]] = {
    "deepseek": DeepSeekClient,
    "gemini": GeminiClient,
    "openai": OpenAIClient,
}


def get_client(name: str, **kwargs: Any) -> ChatClient:
    """get_client("deepseek", model="deepseek-chat") -> DeepSeekClient"""
    if name not in REGISTRY:
        raise KeyError(f"unknown client {name!r}; have {sorted(REGISTRY)}")
    return REGISTRY[name](**kwargs)


class LocalMLXClient(ChatClient):
    """Apple-silicon local client (mlx-lm), added for the oversight-visibility leg.

    Reasoning control
    -----------------
    `supports_reasoning_control` is False and that is a STATEMENT ABOUT GEMMA,
    not a convenience. Gemma-3 has no thinking mode and emits no `<think>` span,
    so there is nothing to switch. docs/narcbench-evidence.md (removed 2026-10-14, in git history) §5 warns that a
    Qwen-family local target would need `<think>` stripped BEFORE the refusal
    test or control 3 breaks in a new form; `strip_think()` below exists so that
    any future Qwen/DeepSeek-R1 local model routes through it rather than
    re-deriving the rule. It is applied unconditionally and is a no-op on Gemma.

    Control 1 (per-call reasoning ON) governs the TARGET agent, whose answer
    token saturates with reasoning on. This client is used for the MONITOR,
    which is the object of measurement rather than a target, so control 1 does
    not gate it. Using this class as a target would require satisfying control 1
    first, and `assert_prompt_controls()` in the episode runner still enforces
    that independently.

    Batching
    --------
    `chat_batch` uses mlx_lm.batch_generate. On an M4 Pro this is roughly an
    order of magnitude faster than looping `chat`, which matters at 4,410 calls.
    """

    supports_reasoning_control = False

    _THINK = re.compile(r"<think>.*?</think>", re.S | re.I)
    _OPEN_THINK = re.compile(r"<think>.*\Z", re.S | re.I)
    _CLOSE_THINK = re.compile(r"\A.*</think>", re.S | re.I)

    def __init__(self, model: str = "mlx-community/gemma-3-12b-it-4bit",
                 max_tokens: int = 24, token_budget: int = 6000,
                 max_batch: int = 8):
        from mlx_lm import load  # imported lazily: the API-only path must not need mlx

        self.name = "local_mlx"
        self.model = model
        self.max_tokens = max_tokens
        self.token_budget = token_budget   # total prompt tokens per GPU batch
        self.max_batch = max_batch
        self._model, self._tokenizer = load(model)

    @classmethod
    def strip_think(cls, text: str) -> str:
        """Remove reasoning spans before ANY downstream parsing (control 3 order).

        Handles the truncated case too: a `<think>` opened and never closed means
        the cap cut the model off mid-deliberation, and everything after it is
        deliberation, not an answer. Returning the remainder would let a label
        mentioned while thinking be scored as a verdict.
        """
        text = cls._THINK.sub(" ", text)
        # A close tag with no open tag: the template prefilled the opening tag,
        # so everything up to the last close is deliberation. See strip_think().
        if "</think>" in text.lower():
            text = cls._CLOSE_THINK.sub(" ", text)
        return cls._OPEN_THINK.sub(" ", text).strip()

    def _encode(self, messages: Messages) -> list[int]:
        # Gemma has no system role: fold the system turn into the first user turn,
        # which is what its own chat template does.
        msgs: list[dict[str, str]] = []
        for m in messages:
            if m["role"] == "system":
                msgs.append({"role": "user", "content": m["content"]})
            elif msgs and msgs[-1]["role"] == m["role"]:
                msgs[-1] = {"role": m["role"],
                            "content": msgs[-1]["content"] + "\n\n" + m["content"]}
            else:
                msgs.append(dict(m))
        return self._tokenizer.apply_chat_template(msgs, add_generation_prompt=True)

    def chat(self, messages: Messages, temperature: float = 1.0, logprobs: bool = False,
             reasoning: bool = True) -> Reply:
        if logprobs:
            raise NotImplementedError("control 4: discrete choice, not logprobs")
        from mlx_lm import generate
        from mlx_lm.sample_utils import make_sampler

        text = generate(self._model, self._tokenizer, prompt=self._encode(messages),
                        max_tokens=self.max_tokens,
                        sampler=make_sampler(temp=temperature))
        return Reply(text=self.strip_think(text), model=self.model)

    def chat_batch(self, batch: list[Messages], temperature: float = 1.0) -> list[Reply]:
        """Batched generation, chunked by TOKEN BUDGET rather than prompt count.

        The three views differ in length by roughly an order of magnitude -- a
        `trace` prompt is the whole episode, an `action` prompt is one paragraph.
        A fixed batch size therefore either wastes the GPU on short prompts or
        exhausts unified memory on long ones (Metal raises
        kIOGPUCommandBufferCallbackErrorOutOfMemory, which kills the run rather
        than degrading it). Budgeting on tokens keeps memory roughly flat across
        views, which is also what keeps the three views comparable in wall time.
        """
        import mlx.core as mx
        from mlx_lm import batch_generate
        from mlx_lm.sample_utils import make_sampler

        encoded = [self._encode(m) for m in batch]
        sampler = make_sampler(temp=temperature)
        out: list[Reply] = []
        i = 0
        while i < len(encoded):
            chunk: list[list[int]] = []
            budget = 0
            while i < len(encoded) and len(chunk) < self.max_batch:
                n = len(encoded[i])
                if chunk and budget + n > self.token_budget:
                    break
                chunk.append(encoded[i])
                budget += n
                i += 1
            res = batch_generate(self._model, self._tokenizer, prompts=chunk,
                                 max_tokens=self.max_tokens, sampler=sampler)
            out.extend(Reply(text=self.strip_think(t), model=self.model)
                       for t in res.texts)
            mx.clear_cache()
        return out


REGISTRY["local_mlx"] = LocalMLXClient


def strip_think(text: str) -> str:
    """Remove reasoning spans BEFORE any downstream parsing.

    docs/narcbench-evidence.md (removed 2026-10-14, in git history) §5 is explicit about why this must happen first:
    a `<think>` span is hundreds of tokens of deliberation that will often name
    both option labels and disclaimer-shaped language *before* the model commits.
    Parsing it is the refusal-before-label-search defect (control 3) in a new
    form. Any open-weights client in this repo routes through this function.

    THREE shapes, not one, and the third is the one that bites:

    1. `<think>...</think>` -- a complete span.
    2. `<think>...` with no close -- the token cap cut the model off, so
       everything after the open tag is deliberation and never an answer.
    3. `...</think>` with NO OPEN TAG. Qwen3.5's chat template PREFILLS the
       opening tag into the prompt, so the completion carries only the close.
       Handling only shapes 1 and 2 leaves the entire chain of thought in the
       text, and models quote the instruction back to themselves while
       thinking -- "VERDICT: ESCALATE or CLEAR" appears verbatim inside the
       deliberation. classify_verdict then matches that quotation and returns
       ESCALATE for a reply whose actual answer was CLEAR. Measured on
       Qwen/Qwen3.5-9B: a confidently WRONG label, not an unparsed one.
    """
    return split_think(text)[0]


def split_think(text: str) -> tuple[str, str]:
    """(answer, reasoning). The answer is byte for byte what strip_think returns.

    The reasoning span is the study's next measure and it has to be KEPT without
    ever reaching a parser. Everything downstream reads element 0. Element 1 is
    written to the episode record and read by nothing that scores.

    Storing it does not weaken control 3, and the removal order below is the same
    order strip_think has always used. Loosening that order to make capture
    easier would reintroduce the defect the docstring above describes.
    """
    spans: list[str] = []

    def _grab(m: "re.Match[str]") -> str:
        spans.append(m.group(0))
        return " "

    text = re.sub(r"<think>.*?</think>", _grab, text, flags=re.S | re.I)
    # Shape 3, before shape 2: take what follows the LAST close tag.
    if "</think>" in text.lower():
        text = re.sub(r"\A.*</think>", _grab, text, flags=re.S | re.I)
    text = re.sub(r"<think>.*\Z", _grab, text, flags=re.S | re.I)
    reasoning = "\n".join(
        re.sub(r"</?think>", " ", sp, flags=re.I).strip() for sp in spans).strip()
    return text.strip(), reasoning


class VLLMClient(_OpenAICompatClient):
    """An OpenAI-compatible vLLM endpoint serving open weights (Modal-hosted).

    Used for the oversight-visibility monitors. Two families are deployed --
    `vllm-gemma-3-12b-it` and `vllm-qwen3-5-9b` -- and the leg requires two
    monitors that do not share weights, because an LLM monitor's absolute rate
    is not interpretable from one model (docs/narcbench-evidence.md (removed 2026-10-14, in git history) §1).

    Reasoning. Qwen3.5's chat template defaults thinking ON; Gemma-3 has no
    thinking mode at all. Rather than trust either, this client BOTH requests
    the documented off-switch (`chat_template_kwargs.enable_thinking`) AND
    strips any span that arrives anyway, and it does the stripping before the
    text is returned so no caller can parse an unstripped reply by accident.
    vLLM also returns `reasoning_content` as a separate field on some builds;
    that field is never concatenated into `text`.

    `supports_reasoning_control` is True because `enable_thinking` is a genuine
    per-call switch on the Qwen template. On a Gemma endpoint it is inert, which
    is why the strip runs unconditionally rather than only when reasoning=False.
    """

    supports_reasoning_control = True

    def __init__(self, model: str, base_url: str | None = None, name: str = "vllm",
                 timeout: int = 600, max_tokens: int = 64, template_kwargs: bool = True):
        base_url = base_url or os.environ.get("MODAL_BASE_URL")
        # False only for a model with no thinking mode whose tokenizer rejects chat_template_kwargs
        # (Mistral Small 3.1 in mistral tokenizer mode). Every other model keeps the default.
        self.template_kwargs = template_kwargs
        if not base_url:
            raise RuntimeError(
                "MODAL_BASE_URL is not set and no base_url was passed. Deploy the "
                "endpoint first:\n"
                "  VLLM_MODEL=ibm-granite/granite-4.2-8b modal deploy scripts/modal_vllm.py\n"
                "then put the printed URL in .env as MODAL_BASE_URL with /v1 appended.")
        self.max_tokens = max_tokens
        super().__init__(model, base_url.rstrip("/"), _require("VLLM_API_KEY"),
                         name=name, timeout=timeout)

    def chat(self, messages: Messages, temperature: float = 1.0, logprobs: bool = False,
             reasoning: bool = True) -> Reply:
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages,
                                  "temperature": temperature,
                                  "max_tokens": self.max_tokens}
        # BOTH directions, always sent. The previous version sent the flag only to
        # turn thinking OFF and left `reasoning=True` to the model's default. That
        # is correct for Qwen3, whose template defaults thinking ON, and silently
        # WRONG for a family that defaults OFF and requires an explicit true --
        # Granite and Gemma 4 are both in that group. On those the caller would
        # ask for reasoning, get none, and the record would still say it was on.
        # A number that is wrong while looking right is the worst failure here.
        if self.template_kwargs:
            kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": bool(reasoning)}}
        resp = self._client.chat.completions.create(**kwargs)
        raw = resp.model_dump()
        msg = raw["choices"][0]["message"]
        content = msg.get("content") or ""
        # VERIFY BY EFFECT, never by parameter. vLLM has shipped builds that
        # accept enable_thinking and ignore it, and clients.py already records
        # the same class of bug on deepseek-v4-pro. Stamp what actually came
        # back so a run can be audited after the fact instead of trusted.
        # TWO FIELD NAMES, because vLLM renamed it. Builds through 0.27 return
        # `reasoning_content`; 0.28.0 returns `reasoning`. Measured on
        # Qwen/Qwen3-8B, vLLM 0.28.0, 2026-09-08: the message carries `reasoning`
        # and has no `reasoning_content` key at all. Reading only the old name
        # yields an empty trace with a perfectly good answer beside it, which is
        # a silent loss of the whole reasoning channel. Read both, forever.
        parsed_span = msg.get("reasoning") or msg.get("reasoning_content") or ""
        raw["thinking_observed"] = {
            "reasoning_content_chars": len(parsed_span),
            "reasoning_field": ("reasoning" if msg.get("reasoning")
                                else "reasoning_content" if msg.get("reasoning_content")
                                else None),
            "think_span_in_content": "<think>" in content,
            "requested": bool(reasoning),
        }
        # reasoning_content is deliberately NOT folded into TEXT, and IS folded
        # into `reasoning`. Those are two different fields and conflating them
        # cost the trace channel once already. With --reasoning-parser set, vLLM
        # moves the think span OUT of `content` into `reasoning_content`;
        # split_think then finds nothing, run_collusion.py's
        # `if getattr(reply, "reasoning", "")` is false, and the turn record
        # carries no trace. The answer parses correctly and the deliberation is
        # silently gone -- a number that is wrong while looking right, which is
        # the failure this class already warns about above.
        #
        # Prefer the parsed field, fall back to an in-content span, because a
        # model may emit tags on an endpoint deployed WITHOUT a parser. The two
        # are never concatenated: only one of them is ever populated, and
        # joining them would invent a trace on the day both fire.
        answer, span_in_content = split_think(content)
        return Reply(text=answer, raw=raw, model=self.model,
                     reasoning=parsed_span or span_in_content)


REGISTRY["vllm"] = VLLMClient
