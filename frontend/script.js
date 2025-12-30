document.addEventListener("DOMContentLoaded", () => {
    const videoUpload = document.getElementById("videoUpload");
    const commandInput = document.getElementById("commandInput");
    const executeButton = document.getElementById("executeCommand");
    const logContainer = document.getElementById("logContainer");
    const apiKeyInput = document.getElementById("apiKeyInput");
    const saveKeyButton = document.getElementById("saveApiKey");

    function log(message) {
        logContainer.textContent += `> ${message}\n`;
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    saveKeyButton.addEventListener("click", async () => {
        const apiKey = apiKeyInput.value;
        if (!apiKey) {
            log("Please enter an API key.");
            return;
        }
        log("Saving API Key...");

        try {
            const response = await fetch('/config/api-key', {
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

    executeButton.addEventListener("click", async () => {
        const command = commandInput.value;
        const videoFile = videoUpload.files[0];

        if (!command || !videoFile) {
            log("Please enter a command and select a video file.");
            return;
        }

        log("Executing command...");
        const formData = new FormData();
        formData.append("file", videoFile); // Changed from "video" to "file" to match backend

        try {
            // Step 1: Upload the video
            log("Uploading video...");
            const uploadResponse = await fetch("/video/upload", {
                method: "POST",
                body: formData,
            });
            const uploadResult = await uploadResponse.json();
            if (!uploadResponse.ok) {
                throw new Error(uploadResult.detail || "Video upload failed");
            }
            log(`Video uploaded: ${uploadResult.filename}`);

            // Step 2: Send the command
            log("Sending command...");
            const commandResponse = await fetch("/control/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ command: command }),
            });
            const commandResult = await commandResponse.json();
            if (!commandResponse.ok) {
                throw new Error(commandResult.detail || "Command execution failed");
            }

            log("Server response:");
            log(JSON.stringify(commandResult, null, 2));

        } catch (error) {
            log(`An error occurred: ${error.message}`);
        }
    });
});
