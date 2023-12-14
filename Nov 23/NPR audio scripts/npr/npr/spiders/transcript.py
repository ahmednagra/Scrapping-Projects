import os
import glob
import logging

from scrapy import Spider

from deepgram import Deepgram


class TranscriptSpider(Spider):
    name = "transcript"
    start_urls = ["https://www.npr.org/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.api_key = self.get_key_values_from_file('input/config.txt').get('api_key', '')

        # load all the audio file in the output/audio folder
        self.all_audios = self.get_all_audios()
        self.already_transcripts = self.get_all_transcripts()
        logging.basicConfig(level=logging.INFO,
                            handlers=[logging.FileHandler('logfile.log'), logging.StreamHandler()])
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self):
        return self._logger

    def parse(self, response, **kwargs):

        deepgram = Deepgram(self.api_key)
        for audiofile in self.all_audios[:1]:
            file = audiofile.split('\\')[1].replace('.mp3', '')
            if file in [x.split('\\')[1].split('_')[0] for x in self.already_transcripts]:
                print(f'audio file {audiofile} already transcript and saved ')
                continue

            print('started Audio file fir transcript : ', audiofile)
            try:
                self.logger.info(f'DeepGram API is calling for the {audiofile} Audio file')
                with open(audiofile, 'rb') as audio:
                    source = {'buffer': audio, 'mimetype': 'audio/wav'}
                    response = deepgram.transcription.sync_prerecorded(source,
                                                                       {
                                                                           'model': 'nova-2',
                                                                           "detect_language": True,
                                                                           # 'smart_format': True,
                                                                           'paragraphs': True,
                                                                           'utterances': True,
                                                                           'diarize': True,
                                                                           'punctuate': True,
                                                                           # 'utt_split': 0.10,  # by default its 0.8
                                                                           "filler_wozrds": True,
                                                                       }
                                                                       )
                    # text = response.get('results', [{}]).get('channels', [])[0].get('alternatives', [])[0].get(
                    #     'transcript', '')
                    # old_text = response.get('results', [{}]).get('channels', [])[0].get('alternatives', [])[0].get('paragraphs', {}).get('transcript', '').replace('\n\n', '\n').strip()
                    paragraphs = response.get('results', [{}]).get('channels', [])[0].get('alternatives', [])[0].get(
                        'paragraphs', {}).get('paragraphs', [])

                    # Extract speaker information and paragraphs
                    # channels = response.get('results', [{}]).get('channels', [])[0]
                    # utterances = response.get('results', {}).get('utterances', [])
                    #
                    # # Organize paragraphs by speaker
                    # speaker_paragraphs = {}
                    # for utterance in utterances:
                    #     speaker = utterance.get('speaker')
                    #     if speaker not in speaker_paragraphs:
                    #         speaker_paragraphs[speaker] = []
                    #     speaker_paragraphs[speaker].append(utterance.get('transcript', '').strip())
                    #
                    # # Create the final transcript
                    # transcript_lines = []
                    # for utterance in utterances:
                    #     speaker = utterance.get('speaker', '')
                    #     transcript = utterance.get('transcript', '').strip()
                    #     transcript_lines.append(f"Speaker {speaker}: {transcript}")
                    #
                    # # Combine speaker paragraphs
                    # for speaker, paragraphs in speaker_paragraphs.items():
                    #     if speaker != 'Unknown':
                    #         transcript_lines.append(f"Speaker {speaker}: {' '.join(paragraphs)}")
                    #
                    # # Combine all lines to get the final transcript
                    # text = '\n'.join(transcript_lines)
                    # text = text.replace('\n\n', '\n').strip()

                    all_transcript_lines = []
                    for paragraph in paragraphs:
                        speaker = paragraph.get('speaker', '')
                        trans = ' '.join([x.get('text') for x in paragraph.get('sentences', [])])
                        all_transcript_lines.append(f"Speaker{speaker}: {trans}")

                    # Join consecutive lines with the same speaker
                    joined_lines = []
                    previous_speaker = ''
                    current_lines = []

                    for line in all_transcript_lines:
                        parts = line.split(':')
                        speaker = parts[0].strip()
                        transcript = parts[1].strip()

                        if previous_speaker == speaker:
                            # Append the current line to the last list in joined_lines
                            if joined_lines and current_lines:
                                current_lines.append(transcript)
                        else:
                            # If the speaker changes, create a new list and append it to joined_lines
                            current_lines = [line]
                            joined_lines.append(current_lines)
                            previous_speaker = speaker

                    # Combine all lines to get the final transcript
                    text = '\n\n'.join([' '.join(line) for line in joined_lines])

                    if not os.path.isdir('output/transcripts'):
                        os.mkdir('output/transcripts')

                    article_id = os.path.splitext(os.path.basename(audiofile))[0]
                    output_text_file = f'output/transcripts/{article_id}_transcript.txt'
                    with open(output_text_file, 'w', encoding='utf-8') as text_file:
                        text_file.write(text)

                    self.logger.info(f"Transcript saved to {output_text_file}")

            except Exception as e:
                self.logger.error(f"Error processing {audiofile}: {e}")

    def get_key_values_from_file(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as input_file:
            data = {}

            for row in input_file.readlines():
                if not row.strip():
                    continue

                try:
                    key, value = row.strip().split('==')
                    data.setdefault(key.strip(), value.strip())
                except ValueError:
                    pass

            return data

    def get_all_audios(self):
        return glob.glob('output/audio/*')

    def get_all_transcripts(self):
        return glob.glob('output/transcripts/*')
