def generate_audio_with_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """Generate audio using ElevenLabs API and return audio bytes."""
    try:
        # Use text_to_speech.convert() for ElevenLabs v2.x
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,  # Rachel voice
            model_id="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(audio_generator)
        return audio_bytes
    except Exception as e:
        raise Exception(f"ElevenLabs API error: {str(e)}")
