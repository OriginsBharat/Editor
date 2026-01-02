import requests
import os
import subprocess

def create_definitive_test_video():
    """
    Creates a test video by overlaying the sign.png image.
    This provides a clean, high-contrast test case for the OCR.
    """
    if os.path.exists("test_video.mp4"):
        os.remove("test_video.mp4")

    print("Creating the definitive test video from sign.png...")
    command = [
        'ffmpeg',
        '-loop', '1',
        '-i', 'sign.png',
        '-f', 'lavfi',
        '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100', # Add silent audio
        '-c:v', 'libx264',
        '-t', '5',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        'test_video.mp4'
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Definitive test video created successfully.")

def verify_reassembly(video_path, command):
    """
    Tests the full end-to-end pipeline.
    """
    url = "http://localhost:8000/api/commands/process-video"

    if not os.path.exists(video_path):
        print(f"Error: Test video file not found at {video_path}")
        return

    with open(video_path, 'rb') as f:
        files = {'video_file': (os.path.basename(video_path), f, 'video/mp4')}
        data = {'command': command}

        try:
            print(f"Sending request to {url}...")
            response = requests.post(url, files=files, data=data, timeout=300)

            if response.status_code == 200:
                print("Request successful!")
                result = response.json()
                print("Response JSON:", result)

                output_path = result.get("output_path")
                if output_path and os.path.exists(output_path):
                    print(f"SUCCESS: Output video created at: {output_path}")
                else:
                    print(f"FAILURE: Server did not return a valid output path. Response: {result}")

            else:
                print(f"Request failed with status code: {response.status_code}")
                print("Response text:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_definitive_test_video()
    verify_reassembly("test_video.mp4", "remove the chinese text from the video")
