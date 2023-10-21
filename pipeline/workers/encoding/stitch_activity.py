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
        f"[{i}:a]adelay={s}|{s}[aud{i}]" for i, (s, f) in enumerate(local_segments)
    ])
    filter_script += ';' + '|'.join([f"[aud{i}]" for i in range(
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

# async def stitch_audio(params: StitchAudioParams) -> str:
#     local_segments = {}
#     max_duration = 0

#     # Download segments, store local file paths and durations
#     for segment in params.segments:
#         audio_bytes = read_s3_file(segment.s3_track)
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as track_file:
#             track_file.write(audio_bytes)
#             local_segments[segment.start] = track_file.name
#             # Get durations to find max_duration
#             duration = get_audio_file_duration(track_file.name)
#             if segment.start + duration > max_duration:
#                 max_duration = segment.start + duration

#     # Generate silent track with max duration
#     silent_track = "silent.mp3"
#     subprocess.run(["ffmpeg", "-f", "lavfi", "-i",
#                    f"anullsrc=r=44100:cl=stereo", "-t", str(max_duration), '-y', silent_track])

#     input_params = ["-i", silent_track]

#     # Add segments to ffmpeg command with offset
#     for start, file_path in sorted(local_segments.items()):
#         input_params.extend(["-itsoffset", str(start), "-i", file_path])

#     workflow_id = activity.info().workflow_run_id
#     output_file = f"output-{workflow_id}.mp3"
#     output_dir = 'working_dir/step-stitch-3'
#     output_path = f"{output_dir}/{output_file}"

#     map_params = []

#     # Create filters to append each audio track to silent background
#     filter_complex_script = ";".join(
#         [f"[{i+1}:a]apad[a{i+1}]" for i in range(len(local_segments))])
#     filter_complex_script += ";" + \
#         "".join([f"[a{i+1}]" for i, _ in enumerate(params.segments)])
#     filter_complex_script += f"amix=inputs={len(params.segments)}:duration=longest"
#     input_params.extend(["-filter_complex", filter_complex_script])
#     input_params.append(output_path)

#     map_params.append(output_path)

#     print(f"Running ffmpeg {' '.join(input_params + map_params)}")

#     subprocess.run(["ffmpeg", "-y"] + input_params + map_params)

#     print('output_path', output_path)
#     with open(output_path, "rb") as f:
#         data = f.read()
#         write_s3_file(output_file, data)

#     # Cleanup all the temp files
#     for local_segment in local_segments:
#         os.remove(local_segment)
#     # os.remove(local_video)
#     # os.remove(script_file.name)
#     # os.remove(output_path)

#     return output_file
