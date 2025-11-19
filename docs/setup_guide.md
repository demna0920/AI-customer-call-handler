# 📞 Real-time Call Setup Guide

To test the system with actual phone calls, you need to expose your local server to the internet so Twilio can talk to it. We use **ngrok** for this.

## 1. Install ngrok (If not already installed)
Since `ngrok` was not found on your system, you need to install it first:
1.  Go to [ngrok.com/download](https://ngrok.com/download).
2.  Download the version for Windows.
3.  Unzip it and place `ngrok.exe` in a folder (e.g., this project folder).
4.  (Optional) Add it to your system PATH or just run it from the current folder.

## 2. Start the Application
Open a terminal and run the Flask app:
```bash
python src/app.py
```
The app will start on `http://localhost:5001`.

## 3. Start ngrok
Open a **new** terminal window. If `ngrok.exe` is in the current folder, run:
```bash
.\ngrok http 5001
```
(If installed globally, just run `ngrok http 5001`)
This will create a secure tunnel. Look for the `Forwarding` URL, which will look something like:
`https://your-random-id.ngrok-free.app`

## 3. Configure Twilio
1.  Log in to your [Twilio Console](https://console.twilio.com/).
2.  Go to **Phone Numbers** > **Manage** > **Active Numbers**.
3.  Click on your phone number (`+441135198981`).
4.  Scroll down to the **Voice & Fax** section.
5.  Under **A Call Comes In**, set the Webhook to:
    `https://your-random-id.ngrok-free.app/voice/incoming`
    *(Replace `your-random-id.ngrok-free.app` with your actual ngrok URL)*
6.  Ensure the method is set to **POST**.
7.  Click **Save**.

## 4. Update Environment Variables
1.  Copy your ngrok URL (e.g., `https://your-random-id.ngrok-free.app`).
2.  Open the `.env` file in your project.
3.  Update the `AUDIO_BASE_URL` variable:
    ```env
    AUDIO_BASE_URL=https://your-random-id.ngrok-free.app/audio
    ```
    *(Don't forget the `/audio` at the end!)*
4.  **Restart your Flask app** (Ctrl+C and run `python src/app.py` again) to load the new config.

## 5. Make a Call!
Now call your Twilio number (`+441135198981`) from your phone. You should hear the AI greeting!
