
document.addEventListener("DOMContentLoaded", () => {
    const videoUpload = document.getElementById("videoUpload");
    const commandInput = document.getElementById("commandInput");
    const executeButton = document.getElementById("executeCommand");
    const logContainer = document.getElementById("logContainer");
    const apiKeyInput = document.getElementById("apiKeyInput");
    const saveKeyButton = document.getElementById("saveApiKey");
    const videoPlayer = document.getElementById("videoPlayer");

    function log(message) {
        logContainer.textContent += `> ${message}\n`;
        logContainer.scrollTop = logContainer.scrollHeight;
        console.log(message); // Also log to browser console for easier debugging
    }

    // --- Save API Key ---
    saveKeyButton.addEventListener("click", async () => {
        const apiKey = apiKeyInput.value;
        if (!apiKey) {
            log("Please enter a Groq API key.");
            return;
        }
        log("Saving API Key...");
        try {
            const response = await fetch('/api/config/api-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ apiKey: apiKey }),
            });
            const result = await response.json();
            if (response.ok) {
                log("API Key saved successfully.");
            } else {
                throw new Error(result.detail || "Failed to save API key");
            }
        } catch (error) {
            log(`Error: ${error.message}`);
        }
    });

    // --- Consolidated Video Processing ---
    executeButton.addEventListener("click", async () => {
        const videoFile = videoUpload.files[0];
        const command = commandInput.value;

        if (!videoFile || !command) {
            log("Please select a video file and enter a command.");
            return;
        }

        log(`Sending command: "${command}" for video: "${videoFile.name}"`);
        const formData = new FormData();
        formData.append("video_file", videoFile);
        formData.append("command", command);

        try {
            const response = await fetch("/api/commands/process-video", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || "Processing failed");
            }

            log("Server Response:");
            log(JSON.stringify(result, null, 2));

            if (result.output_path) {
                log(`Processing complete. Constructing video URL for: ${result.output_path}`);

                // Construct the URL to hit the new dedicated endpoint
                videoPlayer.src = `/video_output/${result.output_path}`;

                // Mute the video to comply with browser autoplay policies
                videoPlayer.muted = true;

                videoPlayer.load();
                videoPlayer.play().catch(e => log(`Autoplay was prevented: ${e.message}`));
                log("Video playback initiated.");
            }

        } catch (error) {
            log(`An error occurred: ${error.message}`);
        }
    });
});
