# DubMaster

![Logo](logo.png)

DubMaster is on a mission to allow content creators to broadcast to a wider audience. We identified a problem where current generation’s automatic dubbing services are relatively expensive. Our solution is to leverage open source models to democratize the dubbing of content.

## Technical Overview

DubMaster works in several steps to provide automatic dubbing services:

1. **Encoding**: The encoding worker is responsible for processing the input video and audio files. It uses ffmpeg to shorten the video and extract the audio. The shortened video and audio are then uploaded to S3 for storage.

2. **Speaker Diarization**: The speaker-diarization worker identifies different speakers in the audio file. This information is used later in the voice cloning process.

3. **Transcription and Translation**: The audio file is transcribed using OpenAI's API. The transcribed text is then translated into the target language.

4. **Voice Cloning**: The voice cloning process uses Eleven Labs' API to clone the voices of the identified speakers. The cloned voices are used to dub the translated text.

5. **Stitching and Combining**: The final step is to stitch the dubbed audio segments together and combine them with the video file. The result is a video file with dubbed audio in the target language.

## Prerequisites

Please ensure you have these prerequisites before running DubMaster.

- TemporalIO for background jobs
- A GPU for speaker diarization
- OpenAI API key for transcription and translation
- Eleven Labs for voice cloning
- S3 for object storage

## Running Encoding Worker

Follow these steps to run the encoding worker:

1. Navigate to the encoding worker directory of the project.
2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
4. Run the worker:
   ```
   python run_worker.py
   ```

## Running Speaker-Diarization Worker

Follow these steps to run the speaker-diarization worker on a GPU server:

1. Navigate to the speaker-diarization worker directory of the project.
2. Run the worker:
   ```
   CUDA_VISIBLE_DEVICES=0 python run_worker.py
   ```

## Running Dub-API

Dub-API is a FastAPI server. You can find the repository [here](https://github.com/Dub-Master/dub-api). Follow these steps to run it:

1. Navigate to the root directory of the project.
2. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
3. Run the server using uvicorn:
   ```
   uvicorn main:app --reload
   ```
   The server will start running on `http://127.0.0.1:8000`.

## Running Dub-Web

Dub-Web is a React frontend. You can find the repository [here](https://github.com/Dub-Master/dub-web). Follow these steps to run it:

1. Navigate to the dub-web directory of the project.
2. Install the required dependencies using npm:
   ```
   npm install
   ```
3. Run the frontend using npm:
   ```
   npm start
   ```
   The frontend will start running on `http://localhost:3000`.

## Backlog

- [x] Downloading YouTube video
- [x] Speaker diarization
- [x] Transcription
- [x] Translation
- [x] Voice cloning
- [x] Video/audio mixing
- [ ] Add back any background audio
- [ ] Move transcription to a GPU worker
- [ ] Move translation to an open source model
- [ ] Move voice cloning to open source
- [ ] Modify speaker's lips in the video to match the translated audio
