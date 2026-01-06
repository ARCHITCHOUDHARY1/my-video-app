# Visual Learning Pattern Analysis + AI Video Synthesis System - COMPLETE GUIDE

## 1. System Requirements

Before running the project, ensure you have the following installed:

*   **Python 3.10+**
*   **FFmpeg**: Required for video processing.
    *   *Windows*: Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract, and add `bin` folder to your System PATH.
    *   *Verify*: Open terminal and type `ffmpeg -version`.
*   **ImageMagick**: Required for MoviePy TextClips.
    *   *Windows*: Download and install from [imagemagick.org](https://imagemagick.org/script/download.php#windows).
    *   *Important*: During installation, check "Install legacy utilities (e.g. convert)".
    *   *Config*: You might need to edit `moviepy/config_defaults.py` to point to your ImageMagick binary if auto-detection fails.

## 2. Google Services Setup (For Reports)

To enable automatic Google Docs report generation:

1.  **Go to Google Cloud Console**: https://console.cloud.google.com/
2.  **Create a New Project**.
3.  **Enable API**: Search for "Google Docs API" and enable it.
4.  **Create Credentials**:
    *   Go to "Credentials" > "Create Credentials" > "OAuth client ID".
    *   Application type: "Desktop app".
    *   Download the JSON file.
5.  **Save File**: Rename the downloaded file to `credentials.json` and place it in the root folder of this project (`d:\Video style analysis for AI synthesis system\`).

*Note: If `credentials.json` is missing, the system will fallback to saving local text reports in `analysis_reports/`.*

## 3. Installation

1.  Open a terminal in the project folder.
2.  Install python dependencies:
    ```bash
    pip install -r requirements.txt
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client moviepy numpy
    ```

## 4. Configuration

1.  **Environment Variables**: The system uses `.env` file.
    *   Ensure `.env` exists (copy `.env.example` if needed).
    *   Set `MISTRAL_API_KEY` (mandatory for AI) or configure Ollama for local LLM.

## 5. Running the System

1.  **Start the Server**:
    ```bash
    uvicorn main:app --reload
    ```
2.  **Open the Interface**:
    *   Go to `http://localhost:8000/docs` in your browser.

## 6. Usage Workflow

### Manual Step (Part A)
1.  Watch your reference video.
2.  Identify the style (e.g., "2D explainer").

### Automatic Step (Part B)
1.  In Swagger UI, find `POST /video/generate`.
2.  Click **Try it out**.
3.  Enter your request JSON:
    ```json
    {
      "topic": "How Neural Networks Work",
      "style_analysis": {
        "style": "2D explainer",
        "colors": "blue,white",
        "animation_speed": "medium",
        "text_style": "bold",
        "transitions": "fade"
      },
      "llm_provider": "mistral"
    }
    ```
4.  Click **Execute**.
5.  Wait for the process to complete (check console logs for progress).
6.  **Outputs**:
    *   **Video**: Found in `generated_videos/` (playable MP4).
    *   **Report**: Found in `analysis_reports/` OR opened automatically in Google Docs (check logs for URL).

## 7. Troubleshooting

*   **MoviePy Error**: If you see "TextClip" errors, ensure ImageMagick is installed and configured.
*   **Google Auth Error**: Delete `token.json` and restart if you changed scopes or credentials.
