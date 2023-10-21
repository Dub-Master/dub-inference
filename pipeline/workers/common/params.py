from dataclasses import dataclass


@dataclass
class EncodingParams:
    url: str


@dataclass
class CombineParams:
    audio_file_path: str
    video_file_path: str


@dataclass
class CoreParams:
    s3_url_audio_file: str
    s3_url_video_file: str
    diarization: list


@dataclass
class DownloadAudioParams:
    s3_url: str


@dataclass
class CreateSegmentParams:
    audio_local_filepath: str
    diarization: list


@dataclass
class TranscribeParams:
    audio_file_url: str


@dataclass
class TranslateParams:
    text: str
    target_language: str


@dataclass
class TextToSpeechParams:
    text: str
    voice: str
    unique_id: int


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
    workflow_id: str
