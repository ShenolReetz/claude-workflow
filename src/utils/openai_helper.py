#!/usr/bin/env python3
"""
OpenAI Helper Functions
=======================

Helper functions for OpenAI API calls with GPT-5 support
"""

import openai

def call_openai_with_fallback(client, messages, model="gpt-5", fallback_model="gpt-4-turbo-preview", **kwargs):
    """Helper function to call OpenAI with GPT-5 and GPT-4 fallback"""
    try:
        # Try GPT-5 first
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response, "gpt-5"
    except openai.NotFoundError:
        # Fallback to GPT-4 if GPT-5 not available
        response = client.chat.completions.create(
            model=fallback_model,
            messages=messages,
            **kwargs
        )
        return response, fallback_model
