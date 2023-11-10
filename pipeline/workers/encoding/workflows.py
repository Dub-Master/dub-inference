from collections import defaultdict
from datetime import timedelta
from typing import Tuple

from temporalio import workflow
from workflow_util import get_workflow_job_id

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import download_video, shrink_inputs
    from common.params import (
        AudioSegment,
        CloneVoiceParams,
        CombineParams,
        CoreParams,
        CreateSegmentParams,
        DeleteVoiceParams,
        E2EParams,
        EncodingParams,
        RawInputParams,
        StitchAudioParams,
        TextToSpeechParams,
        TranscribeParams,
        TranslateParams,
    )
    from media_activity import (
        create_audio_segments,
        download_audio_from_s3,
        upload_file_to_s3,
    )
    from stitch_activity import combine_audio_video, stitch_audio
    from transcribe_activity import transcribe
    from translate_activity import translate
    from voice_clone_activity import clone_voice, delete_voice, text_to_speech


@workflow.defn
class EncodingWorkflow:
    @workflow.run
    async def handle_media(self, params: EncodingParams) -> Tuple:
        video_id = await workflow.execute_activity(
            download_video, params, start_to_close_timeout=timedelta(
                minutes=15)
        )

        shrinkParams = RawInputParams(video_id=video_id)

        (
            local_video_file_path,
            local_audio_file_path,
        ) = await workflow.execute_activity(
            shrink_inputs, shrinkParams, start_to_close_timeout=timedelta(
                minutes=10)
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
        job_id = get_workflow_job_id()

        audio_local_filepath = await workflow.execute_activity(
            download_audio_from_s3, params.s3_url_audio_file,
            start_to_close_timeout=timedelta(minutes=5)
        )

        create_segment_inputs = CreateSegmentParams(
            audio_local_filepath=audio_local_filepath,
            diarization=params.diarization)

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
                upload_file_to_s3, segment_to_upload,
                start_to_close_timeout=timedelta(
                    minutes=3)
            )

            list_of_s3_urls.append(
                {'s3_url': s3_url,
                 'speaker': params.diarization[i]['speaker']})

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

        print('workflow.info()', workflow.info())
        workflow_run_id = workflow.info().run_id
        for speaker in segments_per_speaker.keys():
            print(f'Speaker: {speaker}')

            # @TODO remove and get unique id from workflow
            run_id = workflow.info().run_id
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

        print(voice_id_dict)

        output_segments = []

        for i, s3_url in enumerate(list_of_s3_urls):
            print('enumerate(list_of_s3_urls): ', i)
            print('s3_url', s3_url)
            audio_file_url = await workflow.execute_activity(
                download_audio_from_s3, s3_url['s3_url'],
                start_to_close_timeout=timedelta(
                    minutes=2)
            )
            print('localfilepath', audio_file_url)
            transcript = await workflow.execute_activity(
                transcribe, TranscribeParams(audio_file_url=audio_file_url),
                start_to_close_timeout=timedelta(
                    minutes=5)
            )

            print('transcript', transcript)
            translation = await workflow.execute_activity(
                translate, TranslateParams(
                    text=transcript,
                    target_language=params.target_language),
                start_to_close_timeout=timedelta(
                    minutes=1)
            )

            print('voice_id_dict: ', voice_id_dict)
            print("s3_url['speaker']: ", s3_url['speaker'])
            voice_id = voice_id_dict[s3_url['speaker']]

            audio_url = await workflow.execute_activity(
                text_to_speech, TextToSpeechParams(
                    text=translation, voice=voice_id, unique_id=i),
                start_to_close_timeout=timedelta(
                    minutes=5)
            )
            print(audio_url)
            output_segments.append(AudioSegment(

                start=params.diarization[i]["start"],
                stop=params.diarization[i]["stop"],
                s3_track=audio_url

            ))
        unique_voice_ids = voice_id_dict.values()
        for unique_voice_id in unique_voice_ids:
            await workflow.execute_activity(
                delete_voice, DeleteVoiceParams(unique_voice_id),
                start_to_close_timeout=timedelta(
                    minutes=5)
            )

        stitch_params = StitchAudioParams(
            output_segments,
            params.s3_url_video_file,
            workflow_id=workflow_run_id)

        audio_file = await workflow.execute_activity(
            stitch_audio,
            stitch_params,
            start_to_close_timeout=timedelta(minutes=10)
        )

        print(audio_file)

        output_path = f"output-{job_id}.mp4"
        combine_params = CombineParams(
            audio_file_path=audio_file,
            video_file_path=params.s3_url_video_file,
            output_path=output_path
        )

        output_file = await workflow.execute_activity(
            combine_audio_video,
            combine_params,
            start_to_close_timeout=timedelta(minutes=10)
        )

        print("output file:", output_file)

        s3_url = await workflow.execute_activity(
            upload_file_to_s3, 
            output_file,
            start_to_close_timeout=timedelta(minutes=10)
        )
        print("output s3_url:", s3_url)
        return s3_url


@workflow.defn
class E2EWorkflow:
    @workflow.run
    async def handle(self, params: E2EParams) -> str:
        job_id = get_workflow_job_id()
        input = EncodingParams(url=params.url)
        source_data = await workflow.execute_child_workflow(
            "EncodingWorkflow",
            input,
            id=f"encoding-{job_id}",
            task_queue="encoding-task-queue",
        )
        s3_url_video_file = source_data[0]
        s3_url_audio_file = source_data[1]

        diarization = await workflow.execute_child_workflow(
            "DiarizationWorkflow",
            s3_url_audio_file,
            id=f"diarization-{job_id}",
            task_queue="diarization-task-queue",
        )

        print(f"diarization: {diarization}")

        core_inputs = CoreParams(
            target_language=params.target_language,
            s3_url_audio_file=s3_url_audio_file,
            s3_url_video_file=s3_url_video_file,
            diarization=diarization)

        output_s3_url = await workflow.execute_child_workflow(
            "CoreWorkflow",
            core_inputs,
            id=f"core-{job_id}",
            task_queue="core-task-queue",
        )
        return output_s3_url
