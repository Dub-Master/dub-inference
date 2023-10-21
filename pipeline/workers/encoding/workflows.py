from collections import defaultdict
from datetime import timedelta
from typing import Tuple

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    # from activities import download_video, upload_file_to_s3
    from activities import download_video
    from common.params import (
        AudioSegment,
        CloneVoiceParams,
        CoreParams,
        CreateSegmentParams,
        DeleteVoiceParams,
        EncodingParams,
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
        # audio_local_filepath = await workflow.execute_activity(
        #     download_audio_from_s3, params.s3_url_audio_file,
        #     start_to_close_timeout=timedelta(minutes=5)
        # )

        # create_segment_inputs = CreateSegmentParams(
        #     audio_local_filepath=audio_local_filepath, diarization=params.diarization)

        # list_of_local_file_urls = await workflow.execute_activity(
        #     create_audio_segments, create_segment_inputs,
        #     start_to_close_timeout=timedelta(
        #         minutes=15)
        # )

        # list_of_s3_urls = []
        # folder = 'step-segments-2'
        # for i, file in enumerate(list_of_local_file_urls):
        #     segment_to_upload = {
        #         'folder': folder,
        #         'local_file_path': file
        #     }

        #     s3_url = await workflow.execute_activity(
        #         upload_file_to_s3, segment_to_upload, start_to_close_timeout=timedelta(
        #             minutes=3)
        #     )

        #     list_of_s3_urls.append(
        #         {'s3_url': s3_url, 'speaker': params.diarization[i]['speaker']})

        # segments_per_speaker = defaultdict(list)

        # for i, item in enumerate(params.diarization):
        #     speaker = item["speaker"]
        #     segments_per_speaker[speaker].append(
        #         {
        #             "start": item["start"],
        #             "stop": item["stop"],
        #             "s3_url": list_of_s3_urls[i]['s3_url']
        #         })

        # voice_id_dict = {}

        # print('workflow.info()', workflow.info())
        workflow_run_id = workflow.info().run_id
        # for speaker in segments_per_speaker.keys():
        #     print(f'Speaker: {speaker}')

        #     run_id = '123'  # @TODO remove and get unique id from workflow
        #     speaker_id = speaker

        #     voice_name = f"{run_id}-{speaker_id}"
        #     print('voice_name', voice_name)
        #     s3_audio_subset_url_list = [x['s3_url']
        #                                 for x in segments_per_speaker[speaker]]

        #     print('s3_audio_subset_url_list', s3_audio_subset_url_list)

        #     voice_params = CloneVoiceParams(
        #         voice_name, s3_audio_subset_url_list)
        #     voice_id = await workflow.execute_activity(
        #         clone_voice, voice_params, start_to_close_timeout=timedelta(
        #             minutes=5)
        #     )

        #     voice_id_dict[speaker] = voice_id

        # print(voice_id_dict)

        # output_segments = []

        # for i, s3_url in enumerate(list_of_s3_urls):
        #     print('enumerate(list_of_s3_urls): ', i)
        #     print('s3_url', s3_url)
        #     audio_file_url = await workflow.execute_activity(
        #         download_audio_from_s3, s3_url['s3_url'],
        #         start_to_close_timeout=timedelta(
        #             minutes=2)
        #     )
        #     print('localfilepath', audio_file_url)
        #     transcript = await workflow.execute_activity(
        #         transcribe, TranscribeParams(audio_file_url=audio_file_url),
        #         start_to_close_timeout=timedelta(
        #             minutes=5)
        #     )

        #     target_language = "English"
        #     print('transcript', transcript)
        #     translation = await workflow.execute_activity(
        #         translate, TranslateParams(
        #             text=transcript, target_language=target_language),
        #         start_to_close_timeout=timedelta(
        #             minutes=1)
        #     )

        #     print('voice_id_dict: ', voice_id_dict)
        #     print("s3_url['speaker']: ", s3_url['speaker'])
        #     voice_id = voice_id_dict[s3_url['speaker']]

        #     audio_url = await workflow.execute_activity(
        #         text_to_speech, TextToSpeechParams(
        #             text=translation, voice=voice_id, unique_id=i),
        #         start_to_close_timeout=timedelta(
        #             minutes=5)
        #     )
        #     print(audio_url)
        #     output_segments.append(AudioSegment(

        #         start=params.diarization[i]["start"],
        #         stop=params.diarization[i]["stop"],
        #         s3_track=audio_url

        #     ))
        # unique_voice_ids = voice_id_dict.values()
        # for unique_voice_id in unique_voice_ids:
        #     await workflow.execute_activity(
        #         delete_voice, DeleteVoiceParams(unique_voice_id),
        #         start_to_close_timeout=timedelta(
        #             minutes=5)
        #     )

        output_segments = [AudioSegment(start=0.8521875, stop=2.4553125, s3_track='output-voice-0.mp3'), AudioSegment(start=3.2990625, stop=6.9103125, s3_track='output-voice-1.mp3'), AudioSegment(start=7.8046875, stop=9.002812500000001, s3_track='output-voice-2.mp3'), AudioSegment(start=9.829687500000002, stop=14.7571875, s3_track='output-voice-3.mp3'), AudioSegment(start=20.8153125, stop=27.2953125, s3_track='output-voice-4.mp3'), AudioSegment(start=27.8859375, stop=32.205937500000005, s3_track='output-voice-5.mp3'), AudioSegment(start=32.91468750000001, stop=43.680937500000006, s3_track='output-voice-6.mp3'), AudioSegment(start=44.7946875, stop=53.45156250000001, s3_track='output-voice-7.mp3'), AudioSegment(start=54.143437500000005, stop=57.619687500000005, s3_track='output-voice-8.mp3'), AudioSegment(start=58.51406250000001, stop=60.72468750000001, s3_track='output-voice-9.mp3'), AudioSegment(start=61.38281250000001, stop=63.49218750000001,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             s3_track='output-voice-10.mp3'), AudioSegment(start=64.40343750000001, stop=68.2678125, s3_track='output-voice-11.mp3'), AudioSegment(start=69.0271875, stop=71.1871875, s3_track='output-voice-12.mp3'), AudioSegment(start=71.9296875, stop=73.8534375, s3_track='output-voice-13.mp3'), AudioSegment(start=74.8153125, stop=77.6840625, s3_track='output-voice-14.mp3'), AudioSegment(start=78.4265625, stop=80.0803125, s3_track='output-voice-15.mp3'), AudioSegment(start=80.9409375, stop=83.5903125, s3_track='output-voice-16.mp3'), AudioSegment(start=84.2146875, stop=87.0159375, s3_track='output-voice-17.mp3'), AudioSegment(start=87.7078125, stop=91.2346875, s3_track='output-voice-18.mp3'), AudioSegment(start=92.0953125, stop=96.0440625, s3_track='output-voice-19.mp3'), AudioSegment(start=96.9721875, stop=100.9715625, s3_track='output-voice-20.mp3'), AudioSegment(start=101.7984375, stop=103.7390625, s3_track='output-voice-21.mp3')]
        print(output_segments)

        stitch_params = StitchAudioParams(
            output_segments,
            params.s3_url_video_file,
            workflow_id=workflow_run_id)

        # class AudioSegment:
        #     start: float
        #     stop: float
        #     s3_track: str

        # class StitchAudioParams:
        #     segments: list[AudioSegment]
        #     s3_video_track: str

        output_file = await workflow.execute_activity(
            stitch_audio,
            stitch_params,
            start_to_close_timeout=timedelta(minutes=10)
        )

        print(output_file)
