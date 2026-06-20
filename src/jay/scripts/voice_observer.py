#!/usr/bin/env python3
import speech_recognition as sr
from faster_whisper import WhisperModel
import requests
import time
import os

API_URL = "http://localhost:8002/observation"
WAKE_WORDS = ["hey jay", "hey j", "jay"]


def main():
    print("Loading Whisper model (this may take a moment)...")
    # Using tiny for fast local inference
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Adjusting for ambient noise...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)

    print("Voice Observer Active. Say 'Hey JAY' followed by your message.")

    while True:
        try:
            with mic as source:
                # Listen continuously in chunks
                audio = recognizer.listen(source, phrase_time_limit=10)

            # Save temporarily for faster_whisper
            with open("temp_listen.wav", "wb") as f:
                f.write(audio.get_wav_data())

            segments, _ = model.transcribe("temp_listen.wav", beam_size=5)
            transcript = " ".join([segment.text for segment in segments]).strip()
            transcript_lower = transcript.lower()

            if any(wake in transcript_lower for wake in WAKE_WORDS):
                print(f"[OBSERVED] {transcript}")

                # Send to JAY
                try:
                    requests.post(
                        API_URL,
                        json={"source": "Voice", "payload": {"transcript": transcript}},
                        headers={"Authorization": "Bearer dev_key_only_change_in_prod"},
                    )
                    print("[Sent to Inference Engine]")
                except Exception as e:
                    print(f"Failed to send to JAY: {e}")

            if os.path.exists("temp_listen.wav"):
                os.remove("temp_listen.wav")

        except sr.WaitTimeoutError:
            pass
        except KeyboardInterrupt:
            print("\nShutting down Voice Observer.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
