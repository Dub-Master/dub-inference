#### requirements

- conda

### worker environment setup

1. Create environment:

```shell
conda create -n diart python=3.8
conda activate diart
```

2. Install audio libraries:

```shell
conda install portaudio pysoundfile ffmpeg -c conda-forge
```

3. Install diart and other packages:

```shell
pip install diart temporalio boto3 python-dotenv
```

### Get access to 🎹 pyannote models

By default, diart is based on [pyannote.audio](https://github.com/pyannote/pyannote-audio) models stored in the [huggingface](https://huggingface.co/) hub.
To allow diart to use them, you need to follow these steps:

1. [Accept user conditions](https://huggingface.co/pyannote/segmentation) for the `pyannote/segmentation` model
2. [Accept user conditions](https://huggingface.co/pyannote/embedding) for the `pyannote/embedding` model
3. Install [huggingface-cli](https://huggingface.co/docs/huggingface_hub/quick-start#install-the-hub-library) and [log in](https://huggingface.co/docs/huggingface_hub/quick-start#login) with your user access token (or provide it manually in diart CLI or API).
