document.addEventListener("DOMContentLoaded", () => {
    const videoUploadInput = document.getElementById("videoUpload");
    const commandInput = document.getElementById("commandInput");
    const executeButton = document.getElementById("submitCommand");
    const logContainer = document.getElementById("logContainer");

    executeButton.addEventListener("click", async () => {
        const videoFile = videoUploadInput.files[0];
        const command = commandInput.value;

        if (!videoFile || !command) {
            log("Please select a video file and enter a command.");
            return;
        }

        log("Starting process...");

        try {
            // Step 1: Upload the video
            log("Uploading video...");
            const videoFormData = new FormData();
            videoFormData.append("file", videoFile);

            const uploadResponse = await fetch("http://localhost:8000/video/upload", {
                method: "POST",
                body: videoFormData,
            });

            if (!uploadResponse.ok) {
                throw new Error("Video upload failed.");
            }

            const uploadResult = await uploadResponse.json();
            log(`Video uploaded successfully: ${uploadResult.filename}`);

            // Step 2: Send the command
            log("Sending command...");
            const commandResponse = await fetch("http://localhost:8000/control/command", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ command: command }),
            });

            if (!commandResponse.ok) {
                throw new Error("Command processing failed.");
            }

            const commandResult = await commandResponse.json();
            log(`Command response: ${JSON.stringify(commandResult, null, 2)}`);
            log("Process complete.");

        } catch (error) {
            log(`Error: ${error.message}`);
        }
    });

    function log(message) {
        logContainer.textContent += `${new Date().toLocaleTimeString()}: ${message}\n`;
        // Scroll to the bottom of the log
        logContainer.scrollTop = logContainer.scrollHeight;
    }
});
