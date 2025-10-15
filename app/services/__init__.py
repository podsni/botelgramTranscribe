"""Service layer for external integrations."""

from .deepgram_service import DeepgramTranscriber
from .groq_service import GroqTranscriber, TranscriptionResult
from .together_service import TogetherTranscriber
from .telethon_service import TelethonDownloadService
from .transcription import (
    DeepgramModelPreferences,
    ProviderPreferences,
    TranscriberRegistry,
)
from .audio_optimizer import AudioOptimizer, TranscriptCache
from .queue_service import TaskQueue

__all__ = [
    "GroqTranscriber",
    "DeepgramTranscriber",
    "TogetherTranscriber",
    "TranscriptionResult",
    "TelethonDownloadService",
    "TranscriberRegistry",
    "ProviderPreferences",
    "DeepgramModelPreferences",
    "AudioOptimizer",
    "TranscriptCache",
    "TaskQueue",
]
