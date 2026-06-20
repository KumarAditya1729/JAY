#!/usr/bin/env python3
import requests

API_URL = "http://localhost:8002/observation"


def main():
    print("🎙️  MOCK VOICE OBSERVER ACTIVE")
    print("==============================")
    print("Instead of speaking, just type your transcript here.")
    print(
        "This perfectly simulates the `faster-whisper` output hitting the Observation Engine."
    )
    print("Type 'exit' to quit.\n")

    while True:
        try:
            transcript = input("Say something to JAY: ")
            if transcript.lower() in ["exit", "quit"]:
                break

            if not transcript.strip():
                continue

            try:
                response = requests.post(
                    API_URL,
                    json={"source": "Voice", "payload": {"transcript": transcript}},
                    headers={"Authorization": "Bearer dev_key_only_change_in_prod"},
                )

                if response.status_code == 200:
                    print("[Sent to JAY Inference Engine]")
                else:
                    print(
                        f"[API ERROR] JAY Backend returned {response.status_code}: {response.text}"
                    )
                    print("Did you restart the FastAPI backend server?")

            except Exception as e:
                print(
                    f"Failed to connect to JAY Backend (is docker-compose running?): {e}"
                )

        except KeyboardInterrupt:
            print("\nShutting down Mock Observer.")
            break


if __name__ == "__main__":
    main()
