import os
import subprocess
import tempfile

from common.params import StitchAudioParams
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
    local_segments = {}
    max_duration = 0

    # Download segments, store local file paths and durations
    for segment in params.segments:
        audio_bytes = read_s3_file(segment.s3_track)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as track_file:
            track_file.write(audio_bytes)
            local_segments[segment.start_time] = track_file.name
            # Get durations to find max_duration
            duration = get_audio_file_duration(track_file.name)
            if segment.start_time + duration > max_duration:
                max_duration = segment.start_time + duration

    # Generate silent track with max duration
    silent_track = "silent.mp3"
    subprocess.run(["ffmpeg", "-f", "lavfi", "-i",
                   f"anullsrc=r=44100:cl=stereo", "-t", str(max_duration), silent_track])

    input_params = ["-i", silent_track]

    # Add segments to ffmpeg command with offset
    for start_time, file_path in sorted(local_segments.items()):
        input_params.extend(["-itsoffset", str(start_time), "-i", file_path])

    workflow_id = activity.info().workflow_run_id
    output_file = f"output-{workflow_id}.mp3"
    output_dir = 'working_dir'
    output_path = f"{output_dir}/{output_file}"

    map_params = []

    # Create filters to append each audio track to silent background
    for i in range(len(local_segments)):
        map_params.extend(
            ["-filter_complex", f"[{i+1}:a]apad", "-map", f"[{i+1}]"])

    map_params.append(output_path)

    print(f"Running ffmpeg {' '.join(input_params + map_params)}")

    subprocess.run(["ffmpeg", "-y"] + input_params + map_params)

    with open(output_path, "rb") as f:
        data = f.read()
        write_s3_file(output_file, data)

    # Cleanup all the temp files
    for local_segment in local_segments:
        os.remove(local_segment)
    # os.remove(local_video)
    # os.remove(script_file.name)
    # os.remove(output_path)

    return output_file
