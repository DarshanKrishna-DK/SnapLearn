"""
LLM service: Google Gemini API only. Configure GOOGLE_API_KEY or GEMINI_API_KEY in backend .env
"""

import os
import re
import logging
import asyncio
import random
from typing import Optional

logger = logging.getLogger(__name__)


def _err(msg: str) -> str:
    return f"Error generating content: {msg}"


def _format_gemini_failure_message(detail: str) -> str:
    """
    Turn low-level API errors into something actionable. 403 + referrer = key misconfigured for server use.
    """
    d = (detail or "").lower()
    base = (detail or "").strip()
    if "api_key_http_referrer" in d or "referer" in d and "blocked" in d:
        return (
            f"{base}\n\n"
            "Your API key is restricted to HTTP referrers (browsers). SnapLearn calls Gemini from a Python server, so no Referer is sent. "
            "Fix: open Google Cloud Console, APIs and Services, Credentials, select this key. "
            "Under 'Application restrictions', set 'None' (recommended for local or server backends) or 'IP addresses' for a known server. "
            "Or create a new key in AI Studio: https://aistudio.google.com/apikey and leave key restrictions as default for use from apps. "
            "Do not use 'HTTP referrers' for this backend."
        )
    if "permission_denied" in d and "403" in base:
        return (
            f"{base}\n\n"
            "Check: Generative Language API is enabled, billing is OK, and the key is not restricted in a way that blocks server calls."
        )
    return base


# HTTP timeout for the Gemini SDK, in milliseconds (Field description in types.HttpOptions)
def _http_timeout_ms() -> int:
    v = (os.getenv("GEMINI_HTTP_TIMEOUT_MS") or "").strip()
    if v:
        try:
            return max(60_000, int(v))
        except ValueError:
            pass
    # Default: 6 hours (long generations; no practical cut-off for your use)
    return 6 * 60 * 60 * 1000


# Optional cap on *application-level* retries for one generate() (each attempt is a new SDK call)
def _max_app_retries() -> int:
    v = (os.getenv("GEMINI_APP_RETRIES") or "5").strip()
    try:
        return max(0, min(10, int(v)))
    except ValueError:
        return 5


def _transient_gemini_error(exc: BaseException, err_text: str) -> bool:
    """Heuristic: connection drops, Windows aborts, timeouts, reset by peer."""
    t = f"{type(exc).__name__} {exc} {err_text}"
    t_low = t.lower()
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return True
    # httpx / anyio
    for frag in (
        "10053",
        "10054",
        "connection aborted",
        "aborted by the software",
        "econnreset",
        "econnaborted",
        "broken pipe",
        "connecterror",
        "readerror",
        "remote protocol",
        "temporary failure",
        "try again",
        "resource exhausted",
        "unavailable",
        "deadline",
        "timeout",
    ):
        if frag in t_low:
            return True
    if re.search(r"\b5\d\d\b", t):  # HTTP 5xx in message
        return True
    return False


class LLMService:
    """Gemini API only. No local or alternate LLM backends."""

    def __init__(self):
        self.gemini_client = None
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._init_error: Optional[str] = None
        self._http_timeout_ms = _http_timeout_ms()
        self._init_gemini()

    def _init_gemini(self) -> None:
        try:
            from google import genai
        except ImportError as e:
            self._init_error = f"google-genai not installed: {e}"
            logger.error(self._init_error)
            return

        api_key = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
        if not api_key:
            self._init_error = "No GOOGLE_API_KEY or GEMINI_API_KEY in environment (.env required)"
            logger.error(self._init_error)
            return

        try:
            http_opts = genai.types.HttpOptions(
                timeout=self._http_timeout_ms,
                retry_options=genai.types.HttpRetryOptions(
                    attempts=8,
                    max_delay=120.0,
                    initial_delay=0.5,
                    exp_base=2.0,
                ),
            )
            self.gemini_client = genai.Client(api_key=api_key, http_options=http_opts)
            logger.info(
                "Gemini client ready (model=%s, http_timeout_ms=%s, SDK auto-retries on)",
                self.gemini_model,
                self._http_timeout_ms,
            )
        except Exception as e:
            self._init_error = str(e)
            self.gemini_client = None
            logger.error("Gemini init failed: %s", e)

    def _compose_contents(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        p = (prompt or "").strip()
        if not system_prompt:
            return p
        s = system_prompt.strip()
        return f"{s}\n\n---\n\nTask:\n{p}" if s else p

    def _one_generate_sync(self, contents: str, max_tokens: int, temperature: float) -> str:
        from google import genai
        if not self.gemini_client:
            raise RuntimeError("Gemini not configured")

        cfg = genai.types.GenerateContentConfig(
            max_output_tokens=int(max_tokens),
            temperature=float(temperature),
        )
        r = self.gemini_client.models.generate_content(
            model=self.gemini_model,
            contents=contents,
            config=cfg,
        )
        t = (getattr(r, "text", None) or "").strip() if r is not None else ""
        if not t:
            raise RuntimeError("Gemini returned empty text")
        return t

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate with Gemini. Uses long HTTP timeouts, SDK retries, and extra app-level retries
        for flaky connections (e.g. WinError 10053 on Windows). On final failure, returns
        a string starting with "Error generating content: ...".
        """
        if not self.gemini_client:
            return _err(self._init_error or "Gemini not configured")

        contents = self._compose_contents(prompt, system_prompt)
        n_try = 1 + _max_app_retries()
        last_msg = "unknown"
        for attempt in range(1, n_try + 1):
            def _call() -> str:
                return self._one_generate_sync(contents, max_tokens, temperature)

            try:
                out = await asyncio.to_thread(_call)
                if attempt > 1:
                    logger.info("Gemini call succeeded on attempt %s", attempt)
                return out
            except Exception as e:
                last_msg = f"{type(e).__name__}: {e}"
                if not _transient_gemini_error(e, last_msg):
                    logger.error("Gemini error (no retry for this class): %s", last_msg)
                    return _err(_format_gemini_failure_message(last_msg))
                if attempt >= n_try:
                    logger.error("Gemini give up after %s attempts: %s", attempt, last_msg)
                    return _err(_format_gemini_failure_message(last_msg))
                delay = min(60.0, (1.5 ** (attempt - 1)) * (0.4 + 0.3 * random.random()))
                logger.warning(
                    "Gemini attempt %s/%s failed (%s); retry in %.1fs",
                    attempt,
                    n_try,
                    last_msg,
                    delay,
                )
                await asyncio.sleep(delay)
        return _err(_format_gemini_failure_message(last_msg))

    def is_healthy(self) -> bool:
        return self.gemini_client is not None and self._init_error is None


llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service
