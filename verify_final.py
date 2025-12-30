from playwright.sync_api import sync_playwright, expect
import os
import json

CONSOLE_LOG_FILE = "browser_console.log"

def verify_full_flow(page, api_key):
    """
    Tests the full end-to-end flow and captures a full-page screenshot.
    """
    # Clear previous log file
    if os.path.exists(CONSOLE_LOG_FILE):
        os.remove(CONSOLE_LOG_FILE)

    # Attach a listener to the console event
    page.on("console", lambda msg: log_console_message(msg))

    # Navigate to the app's home page
    page.goto("http://localhost:8000/")

    # Step 1: Save the API Key
    api_key_input = page.locator("#apiKeyInput")
    api_key_input.fill(api_key)
    save_button = page.get_by_role("button", name="Save Key")
    save_button.click()
    log_container = page.locator("#logContainer")
    expect(log_container).to_contain_text("API Key saved successfully.", timeout=10000)

    # Step 2: Upload a video
    video_upload_input = page.locator("#videoUpload")
    dummy_file_path = os.path.abspath("dummy_video.txt")
    video_upload_input.set_input_files(dummy_file_path)

    # Step 3: Send a command
    command_input = page.locator("#commandInput")
    command_input.fill("Remove the Chinese text from the video")
    execute_button = page.get_by_role("button", name="Execute")
    execute_button.click()

    # Step 4: Verify the error response when no valid API key is present
    expect(log_container).to_contain_text('error', timeout=20000)

    # Step 5: Capture a full-page screenshot
    page.screenshot(path="verification_final.png", full_page=True)

def log_console_message(msg):
    """Callback to write console messages to a file."""
    with open(CONSOLE_LOG_FILE, "a") as f:
        f.write(f"[{msg.type}] {msg.text}\n")

if __name__ == "__main__":
    user_api_key = "dummy-api-key-for-testing"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Set a larger viewport to ensure all elements are visible
        page = browser.new_page(viewport={"width": 1280, "height": 1024})
        try:
            verify_full_flow(page, user_api_key)
            print("Final verification script completed and screenshot captured.")
        except Exception as e:
            print(f"Playwright script failed: {e}")
            print(f"Check '{CONSOLE_LOG_FILE}' for browser console output.")
        finally:
            browser.close()
