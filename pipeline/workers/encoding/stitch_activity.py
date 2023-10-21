import os
import subprocess
import tempfile

from common.params import CombineParams, StitchAudioParams
from temporalio import activity
from util import read_s3_file, write_s3_file

"""
ffmpeg -i clip.mp4 -i part1.mp3 -i part2.mp3 -filter_complex \
"[1:a]asetpts=PTS-STARTPTS[a1]; \
 [2:a]asetpts=PTS-STARTPTS[a2]; \
 [a1][a2]concat=n=2:v=0:a=1[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac clip_output.mp4
"""


def get_audio_file_duration(
    audio_file_path: str,
) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", audio_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


@activity.defn
async def stitch_audio(params: StitchAudioParams) -> str:
    local_segments = []
    max_duration = 0

    # Download segments, store local file paths and durations
    for segment in params.segments:
        audio_bytes = read_s3_file(segment.s3_track)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as track_file:
            track_file.write(audio_bytes)
            local_segments.append((segment.start, track_file.name))
            # Get durations to find max_duration
            duration = get_audio_file_duration(track_file.name)
            if segment.start + duration > max_duration:
                max_duration = segment.start + duration

    # generate a silent audio with same duration as video
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-y", "-i", "anullsrc=cl=mono:r=44100", "-t",
        f"{max_duration}", "-q:a", "9", "-acodec", "libmp3lame", "silent.mp3"
    ])

    # Create filter_complex to delay segments
    filter_script = ';'.join([
        f"[{i+1}:a]adelay={s*1000}|{s*1000}[aud{i+1}]" for i, (s, f) in enumerate(local_segments)
    ])
    filter_script += ';' + ''.join([f"[aud{i+1}]" for i in range(
        len(local_segments))]) + f'amix=inputs={len(local_segments)}:duration=longest'

    workflow_id = activity.info().workflow_run_id
    output_file = f"output-{workflow_id}.mp3"
    # run ffmpeg with input files and filter_complex
    cmd = ["ffmpeg", "-y", "-i", "silent.mp3"] +\
        [item for sublist in [[f"-i", f] for _, f in local_segments] for item in sublist] +\
        ["-filter_complex", filter_script, output_file]

    print('Running command:', ' '.join(cmd))
    subprocess.run(cmd)

    return output_file


@activity.defn
async def combine_audio_video(params: CombineParams) -> str:
    local_video = None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as video_file:
        video_file.write(read_s3_file(params.video_file_path))
        local_video = video_file.name

    workflow_id = activity.info().workflow_run_id
    output_file = f"output-{workflow_id}.mp4"

    cmd = f"ffmpeg -i {local_video} -y -i {params.audio_file_path} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {output_file}"
    os.system(cmd)
    return output_file
