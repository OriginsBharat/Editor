document.addEventListener("DOMContentLoaded", () => {
    const videoUpload = document.getElementById("videoUpload");
    const commandInput = document.getElementById("commandInput");
    const executeButton = document.getElementById("executeCommand");
    const logContainer = document.getElementById("logContainer");
    const apiKeyInput = document.getElementById("apiKeyInput");
    const saveKeyButton = document.getElementById("saveApiKey");
    let lastUploadedFilename = ""; // Variable to store the last uploaded filename

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

    // Handle video upload separately to store the filename
    videoUpload.addEventListener("change", async () => {
        const videoFile = videoUpload.files[0];
        if (!videoFile) {
            return;
        }

        log("Uploading video...");
        const formData = new FormData();
        formData.append("file", videoFile);

        try {
            const uploadResponse = await fetch("/video/upload", {
                method: "POST",
                body: formData,
            });
            const uploadResult = await uploadResponse.json();
            if (!uploadResponse.ok) {
                throw new Error(uploadResult.detail || "Video upload failed");
            }
            lastUploadedFilename = uploadResult.filename; // Store the filename
            log(`Video uploaded successfully: ${lastUploadedFilename}`);
        } catch (error) {
            log(`An error occurred during upload: ${error.message}`);
            lastUploadedFilename = ""; // Reset on failure
        }
    });

    executeButton.addEventListener("click", async () => {
        const command = commandInput.value;

        if (!command || !lastUploadedFilename) {
            log("Please upload a video and enter a command before executing.");
            return;
        }

        log("Sending command to backend...");
        try {
            const commandResponse = await fetch("/control/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    command: command,
                    video_filename: lastUploadedFilename // Send the stored filename
                }),
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
