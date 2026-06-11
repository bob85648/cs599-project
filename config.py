"""
Runtime configuration for the TravelMind multi-agent travel assistant.

Secrets must be provided through environment variables. Do not commit real API
keys to the repository.
"""
from __future__ import annotations

import os


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


LLM_CONFIG = {
    "api_key": os.getenv("LLM_API_KEY", ""),
    "model_name": os.getenv("LLM_MODEL_NAME", "mimo-v2.5-pro"),
    "base_url": os.getenv("LLM_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1"),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "8192")),
}

SYSTEM_CONFIG = {
    "enable_llm": _get_bool("ENABLE_LLM", True),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "timeout": int(os.getenv("LLM_TIMEOUT", "60")),
}

RAG_CONFIG = {
    "embedding_model": os.getenv("EMBEDDING_MODEL_PATH", "data/models/bge-small-zh-v1.5"),
}

RESILIENCE_CONFIG = {
    "max_retries": int(os.getenv("RESILIENCE_MAX_RETRIES", "3")),
    "retry_base_delay_sec": float(os.getenv("RETRY_BASE_DELAY_SEC", "1.0")),
    "retry_max_delay_sec": float(os.getenv("RETRY_MAX_DELAY_SEC", "30.0")),
    "circuit_failure_threshold": int(os.getenv("CIRCUIT_FAILURE_THRESHOLD", "5")),
    "circuit_recovery_timeout_sec": float(os.getenv("CIRCUIT_RECOVERY_TIMEOUT_SEC", "60.0")),
    "circuit_half_open_successes": int(os.getenv("CIRCUIT_HALF_OPEN_SUCCESSES", "2")),
    "health_check_timeout_sec": float(os.getenv("HEALTH_CHECK_TIMEOUT_SEC", "10.0")),
}
