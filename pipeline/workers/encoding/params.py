from dataclasses import dataclass

@dataclass
class TranslateParams:
    text: str
    target_language: str

@dataclass
class TextToSpeechParams:
    text: str
    voice: str

@dataclass
class CloneVoiceParams:
    voice_name: str
    s3_audio_files: list[str]

@dataclass
class DeleteVoiceParams:
    voice_id: str

@dataclass
class AudioSegment:
    start: float
    stop: float
    s3_track: str

@dataclass
class StitchAudioParams:
    segments: list[AudioSegment]
    s3_video_track: str
