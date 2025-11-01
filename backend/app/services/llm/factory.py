"""Factory for creating and managing LLM providers."""

from typing import Literal

from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.google import GoogleProvider
from app.services.llm.providers.openai import OpenAIProvider

LLMProviderType = Literal["openai", "anthropic", "google"]


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

    # Map of provider types to classes
    provider_classes = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
    }

    # Try to create requested provider
    if requested_provider in provider_classes:
        provider = provider_classes[requested_provider]()
        if provider.is_available():
            return provider

    # Fallback: try providers in order of preference (cheapest first)
    fallback_order: list[LLMProviderType] = ["google", "openai", "anthropic"]

    for fallback_type in fallback_order:
        if fallback_type == requested_provider:
            # Already tried this one
            continue

        provider = provider_classes[fallback_type]()
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
