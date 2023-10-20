from collections import defaultdict
from datetime import timedelta
from typing import Tuple

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    # from activities import download_video, upload_file_to_s3
    from activities import download_video
    from common.params import (
        CloneVoiceParams,
        CoreParams,
        CreateSegmentParams,
        DeleteVoiceParams,
        EncodingParams,
        StitchAudioParams,
        TextToSpeechParams,
        TranslateParams,
    )
    from media_activity import (
        create_audio_segments,
        download_audio_from_s3,
        upload_file_to_s3,
    )
    from stitch_activity import stitch_audio
    from transcribe_activity import transcribe
    from translate_activity import translate
    from voice_clone_activity import clone_voice, delete_voice, text_to_speech


@workflow.defn
class EncodingWorkflow:
    @workflow.run
    async def handle_media(self, params: EncodingParams) -> Tuple:
        (
            local_video_file_path,
            local_audio_file_path,
        ) = await workflow.execute_activity(
            download_video, params, start_to_close_timeout=timedelta(
                minutes=15)
        )

        print(local_audio_file_path)

        folder = 'step-encoding-1'

        video_to_upload = {
            'folder': folder,
            'local_file_path': local_video_file_path
        }

        print(video_to_upload)

        s3_video_url = await workflow.execute_activity(
            upload_file_to_s3,
            video_to_upload,
            start_to_close_timeout=timedelta(minutes=15),
        )

        audio_to_upload = {
            'folder': folder,
            'local_file_path': local_audio_file_path
        }

        s3_audio_url = await workflow.execute_activity(
            upload_file_to_s3,
            audio_to_upload,
            start_to_close_timeout=timedelta(minutes=15),
        )
        return (s3_video_url, s3_audio_url)


@workflow.defn
class CoreWorkflow:
    @workflow.run
    async def handle(self, params: CoreParams) -> str:
        audio_local_filepath = await workflow.execute_activity(
            download_audio_from_s3, params.s3_url_audio_file,
            start_to_close_timeout=timedelta(minutes=5)
        )

        create_segment_inputs = CreateSegmentParams(
            audio_local_filepath=audio_local_filepath, diarization=params.diarization)

        list_of_local_file_urls = await workflow.execute_activity(
            create_audio_segments, create_segment_inputs,
            start_to_close_timeout=timedelta(
                minutes=15)
        )

        list_of_s3_urls = []
        folder = 'step-segments-2'
        for i, file in enumerate(list_of_local_file_urls):
            segment_to_upload = {
                'folder': folder,
                'local_file_path': file
            }

            s3_url = await workflow.execute_activity(
                upload_file_to_s3, segment_to_upload, start_to_close_timeout=timedelta(
                    minutes=3)
            )

            list_of_s3_urls.append(
                {'s3_url': s3_url, 'speaker': params.diarization[i]['speaker']})

        segments_per_speaker = defaultdict(list)

        for i, item in enumerate(params.diarization):
            speaker = item["speaker"]
            segments_per_speaker[speaker].append(
                {
                    "start": item["start"],
                    "stop": item["stop"],
                    "s3_url": list_of_s3_urls[i]['s3_url']
                })

        voice_id_dict = {}

        for speaker in segments_per_speaker.keys():
            print(f'Speaker: {speaker}')

            run_id = '123'  # TODO remove
            speaker_id = speaker

            voice_name = f"{run_id}-{speaker_id}"
            print('voice_name', voice_name)
            s3_audio_subset_url_list = [x['s3_url']
                                        for x in segments_per_speaker[speaker]]

            print('s3_audio_subset_url_list', s3_audio_subset_url_list)

            voice_params = CloneVoiceParams(
                voice_name, s3_audio_subset_url_list)
            voice_id = await workflow.execute_activity(
                clone_voice, voice_params, start_to_close_timeout=timedelta(
                    minutes=5)
            )

            voice_id_dict[speaker] = voice_id

        for i, s3_url in enumerate(list_of_s3_urls):
            localfilepath = await workflow.execute_activity(
                download_audio_from_s3, s3_url['s3_url'],
                start_to_close_timeout=timedelta(
                    minutes=2)
            )
            transcript = await workflow.execute_activity(
                transcribe, localfilepath, start_to_close_timeout=timedelta(
                    minutes=2)
            )
            translation = await workflow.execute_activity(
                translate, TranslateParams(transcript, "Spanish"),
                start_to_close_timeout=timedelta(
                    minutes=1)
            )

            voice_id = voice_id_dict[s3_url['speaker']]

            audio_url = await workflow.execute_activity(
                text_to_speech, TextToSpeechParams(translation, voice_id),
                start_to_close_timeout=timedelta(
                    minutes=5)
            )
            print(audio_url)

        unique_voice_ids = []
        for unique_voice_id in unique_voice_ids:
            await workflow.execute_activity(
                delete_voice, DeleteVoiceParams(unique_voice_id),
                start_to_close_timeout=timedelta(
                    minutes=5)
            )

        StitchAudioParams(list_of_s3_urls, params.s3_url_video_file)
        output_file = await workflow.execute_activity(
            stitch_audio, params, start_to_close_timeout=timedelta(minutes=10)
        )

        print(output_file)
