import io
import logging
from typing import Optional

import speech_recognition as sr
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, model_size: str = "base"):
        self.recognizer = sr.Recognizer()

        # Security/Fix: Re-enable dynamic threshold so it can hear you regardless of your mic volume
        self.recognizer.dynamic_energy_threshold = True

        # Initialize whisper model.
        # Using "base" for decent speed/accuracy tradeoff.
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def listen_and_transcribe(self, timeout: Optional[int] = None) -> Optional[str]:
        with sr.Microphone() as source:
            print("Listening...")
            try:
                # Capture the audio (phrase limit prevents it from recording forever if background noise is constant)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=15
                )
                print("Audio captured, transcribing...")

                # Convert the raw audio data to WAV bytes
                wav_data = audio.get_wav_data()

                # faster_whisper accepts a file-like object
                audio_file = io.BytesIO(wav_data)

                segments, info = self.model.transcribe(audio_file, beam_size=5)

                text = ""
                for segment in segments:
                    text += segment.text + " "

                return text.strip()

            except sr.WaitTimeoutError:
                logger.info("Listening timed out.")
                return None
            except Exception as e:
                logger.error(f"Error during transcription: {e}")
                return None

    def listen_continuously(self):
        """Continuously yields transcribed text from the microphone."""
        with sr.Microphone() as source:
            print("Calibrating to room noise for 1 second...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(
                "Mansion Protocol Active. Continuously listening for wake word 'JAY'..."
            )
            while True:
                try:
                    # No timeout, blocks until it hears speech over the threshold
                    audio = self.recognizer.listen(
                        source, timeout=None, phrase_time_limit=10
                    )
                    wav_data = audio.get_wav_data()
                    audio_file = io.BytesIO(wav_data)
                    segments, info = self.model.transcribe(audio_file, beam_size=5)

                    text = ""
                    for segment in segments:
                        text += segment.text + " "

                    if text.strip():
                        yield text.strip()

                except sr.WaitTimeoutError:
                    continue
                except KeyboardInterrupt:
                    print("Continuous listening stopped.")
                    break
                except Exception as e:
                    logger.error(f"Error during continuous transcription: {e}")
                    continue
