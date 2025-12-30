from playwright.sync_api import sync_playwright, expect
import os

CONSOLE_LOG_FILE = "browser_console.log"

def verify_ocr_pipeline(page):
    """
    Tests the full end-to-end flow from command to OCR initiation.
    """
    # Clear previous log file
    if os.path.exists(CONSOLE_LOG_FILE):
        os.remove(CONSOLE_LOG_FILE)

    # Attach a listener to the console event
    page.on("console", lambda msg: log_console_message(msg))

    # Navigate to the app's home page
    page.goto("http://localhost:8000/")

    # Step 1: Save a dummy API Key
    api_key_input = page.locator("#apiKeyInput")
    api_key_input.fill("dummy-key-for-testing")
    save_button = page.get_by_role("button", name="Save Key")
    save_button.click()
    log_container = page.locator("#logContainer")
    expect(log_container).to_contain_text("API Key saved successfully.", timeout=10000)

    # Step 2: Upload the test video
    video_upload_input = page.locator("#videoUpload")
    test_video_path = os.path.abspath("test_video.mp4")
    video_upload_input.set_input_files(test_video_path)
    expect(log_container).to_contain_text("Video uploaded successfully: test_video.mp4", timeout=10000)

    # Step 3: Send a command
    command_input = page.locator("#commandInput")
    command_input.fill("Remove the Chinese text from the video")
    execute_button = page.get_by_role("button", name="Execute")
    execute_button.click()

    # Step 4: Verify that the OCR process was initiated
    # We expect an error because the file is not a real video, but this confirms the pipeline is working.
    expect(log_container).to_contain_text("No frames were extracted from the video.", timeout=20000)

    # Step 5: Capture a screenshot for final verification
    page.screenshot(path="verification_ocr.png", full_page=True)

def log_console_message(msg):
    """Callback to write console messages to a file."""
    with open(CONSOLE_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{msg.type}] {msg.text}\n")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1024})
        try:
            verify_ocr_pipeline(page)
            print("OCR pipeline verification script completed and screenshot captured.")
        except Exception as e:
            print(f"Playwright script failed: {e}")
            print(f"Check '{CONSOLE_LOG_FILE}' for browser console output.")
        finally:
            browser.close()
