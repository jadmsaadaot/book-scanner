"""Factory for creating and managing LLM providers."""

import logging
from typing import Literal

from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.google import GoogleProvider
from app.services.llm.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)

LLMProviderType = Literal["openai", "anthropic", "google"]

# Provider class mapping (used by all fallback functions)
PROVIDER_CLASSES = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
}


def get_llm_provider(provider_type: LLMProviderType | None = None) -> LLMProvider:
    """
    Get an LLM provider instance.

    Args:
        provider_type: Type of provider to create. If None, uses settings.LLM_PROVIDER.
                      Falls back to first available provider if specified one isn't configured.

    Returns:
        LLMProvider instance

    Raises:
        RuntimeError: If no providers are configured
    """
    # Determine which provider to use
    requested_provider = provider_type or settings.LLM_PROVIDER

    # Try to create requested provider
    if requested_provider in PROVIDER_CLASSES:
        provider = PROVIDER_CLASSES[requested_provider]()
        if provider.is_available():
            return provider

    # Fallback: try providers in order of preference (cheapest first)
    fallback_order: list[LLMProviderType] = ["google", "openai", "anthropic"]

    for fallback_type in fallback_order:
        if fallback_type == requested_provider:
            # Already tried this one
            continue

        provider = PROVIDER_CLASSES[fallback_type]()
        if provider.is_available():
            return provider

    # No providers available
    raise RuntimeError(
        "No LLM providers are configured. Please set at least one API key: "
        "OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
    )


def get_available_providers() -> list[LLMProviderType]:
    """
    Get list of currently available (configured) providers.

    Returns:
        List of provider type names that are available
    """
    available = []

    providers = {
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "google": GoogleProvider(),
    }

    for name, provider in providers.items():
        if provider.is_available():
            available.append(name)  # type: ignore

    return available


async def extract_titles_with_fallback(image_bytes: bytes) -> str:
    """
    Extract titles from image with automatic provider fallback.

    Tries primary provider first, then falls back to other configured providers
    if the primary one fails.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Raw JSON string response from successful provider

    Raises:
        RuntimeError: If all providers fail
    """
    available = get_available_providers()

    if not available:
        raise RuntimeError(
            "No LLM providers are configured. Please set at least one API key: "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
        )


    # Try providers in order: primary first, then others
    primary_provider = settings.LLM_PROVIDER
    providers_to_try = [primary_provider] + [p for p in available if p != primary_provider]

    errors = []

    for provider_name in providers_to_try:
        if provider_name not in available:
            continue

        try:
            provider = PROVIDER_CLASSES[provider_name]()
            logger.info(f"Attempting VLM extraction with {provider_name}")

            result = await provider.extract_titles_from_image(image_bytes)

            logger.info(f"✅ VLM extraction succeeded with {provider_name}")
            return result

        except Exception as e:
            error_msg = f"{provider_name}: {str(e)}"
            errors.append(error_msg)
            logger.warning(f"❌ VLM extraction failed with {provider_name}: {e}")

            # Continue to next provider
            continue

    # All providers failed
    raise RuntimeError(
        f"All VLM providers failed. Errors: {'; '.join(errors)}"
    )


async def calculate_batch_scores_with_fallback(
    detected_books: list[dict],
    user_library: list[dict]
) -> list[dict]:
    """
    Calculate batch match scores with automatic provider fallback.

    Tries primary provider first, then falls back to other configured providers
    if the primary one fails.

    Args:
        detected_books: List of book metadata to evaluate
        user_library: User's library books

    Returns:
        List of dicts with keys: title, score, explanation

    Raises:
        RuntimeError: If all providers fail
    """
    available = get_available_providers()

    if not available:
        raise RuntimeError(
            "No LLM providers are configured. Please set at least one API key: "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
        )


    # Try providers in order: primary first, then others
    primary_provider = settings.LLM_PROVIDER
    providers_to_try = [primary_provider] + [p for p in available if p != primary_provider]

    errors = []

    for provider_name in providers_to_try:
        if provider_name not in available:
            continue

        try:
            provider = PROVIDER_CLASSES[provider_name]()
            logger.info(f"Attempting batch recommendation scoring with {provider_name}")

            results = await provider.calculate_batch_match_scores(
                detected_books, user_library
            )

            logger.info(f"✅ Batch recommendation scoring succeeded with {provider_name}")
            return results

        except Exception as e:
            error_msg = f"{provider_name}: {str(e)}"
            errors.append(error_msg)
            logger.warning(f"❌ Batch recommendation scoring failed with {provider_name}: {e}")

            # Continue to next provider
            continue

    # All providers failed
    raise RuntimeError(
        f"All batch recommendation providers failed. Errors: {'; '.join(errors)}"
    )
