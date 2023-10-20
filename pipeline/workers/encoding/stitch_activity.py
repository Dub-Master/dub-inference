from temporalio import activity
from params import StitchAudioParams
import subprocess
import tempfile
import os

from util import read_s3_file, write_s3_file

"""
ffmpeg -i clip.mp4 -i part1.mp3 -i part2.mp3 -filter_complex \
"[1:a]asetpts=PTS-STARTPTS[a1]; \
 [2:a]asetpts=PTS-STARTPTS[a2]; \
 [a1][a2]concat=n=2:v=0:a=1[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac clip_output.mp4
"""

@activity.defn
async def stitch_audio(params: StitchAudioParams) -> str:
    local_segments = []
    local_video = None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as video_file:
        video_file.write(read_s3_file(params.s3_video_track))
        local_video = video_file.name
    
    for segment in params.segments:
        audio_bytes = read_s3_file(segment.s3_track)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as track_file:
            track_file.write(audio_bytes)
            local_segments.append(track_file.name)
    
    input_params = ["-y", "-i", local_video]
    
    for local_segment in local_segments:
        input_params.extend(["-i", local_segment])
    
    wokflow_id = activity.info().workflow_run_id
    output_file = f"output-{wokflow_id}.mp4"
    output_dir = tempfile.mkdtemp()
    output_path = f"{output_dir}/{output_file}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w") as script_file:
        for i, segment in enumerate(params.segments):
            script_file.write(f"[{i+1}:a]asetpts=PTS-STARTPTS[a{i+1}];\n")
        
        #TODO: add silent breaks between segments
        script_file.write("".join([f"[a{i+1}]" for i in range(len(params.segments))]))
        script_file.write(f"concat=n={len(params.segments)}:v=0:a=1[a]\n")

    input_params.extend(["-filter_complex_script", script_file.name])
    input_params.extend(["-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-shortest", output_path])
    
    print(f"Running ffmpeg {' '.join(input_params)}")
    
    subprocess.run(["ffmpeg"] + input_params)
    
    with open(output_path, "rb") as f:
        data = f.read()
        write_s3_file(output_file, data)

    # Cleanup all the temp files
    for local_segment in local_segments:
        os.remove(local_segment)
    os.remove(local_video)
    os.remove(script_file.name)
    os.remove(output_path)
    
    return output_file
