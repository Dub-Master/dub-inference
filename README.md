# DubMaster

![Logo](logo.png)

Dubmaster is on a mission to allow content creators to broadcast to a wider audience. We identified a problem where current generation’s automatic dubbing services are relatively expensive. Our solution is to leverage open source models to democratize the dubbing of content.

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
