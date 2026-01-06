# Google Docs API Setup - Beginner's Complete Guide

The "403 Access Denied" error usually happens because the Google App is in "Testing" mode and your email hasn't been added as a "Test User". Follow these exact steps to fix it.

## Phase 1: Create Project & Enable API

1.  **Open Google Cloud Console**:
    *   Go to [console.cloud.google.com](https://console.cloud.google.com/).
    *   Log in with your Google (Gmail) account.
2.  **Create a New Project**:
    *   Click the project dropdown (top left, next to "Google Cloud").
    *   Click **"New Project"** (top right of the popup).
    *   **Project Name**: Enter `Video-Synthesis-System`.
    *   Click **Create**.
    *   *Wait* a moment, then click **Select Project** in the notification or select it from the dropdown.
3.  **Enable Google Docs API**:
    *   In the search bar at the very top, type `Google Docs API`.
    *   Click on "Google Docs API" (Marketplace).
    *   Click **ENABLE**.

## Phase 2: Configure Consent Screen (Crucial for 403 Error)

1.  **Go to OAuth Consent Screen**:
    *   Click the "Navigation Menu" ( ☰ three lines at top left).
    *   Hover over **APIs & Services** > Click **OAuth consent screen**.
2.  **User Type**:
    *   Select **External**.
    *   Click **Create**.
3.  **App Information**:
    *   **App name**: `Video Synthesis App`.
    *   **User support email**: Select your own email.
    *   **Developer contact information**: Enter your own email again.
    *   Click **SAVE AND CONTINUE**.
4.  **Scopes**:
    *   Click **ADD OR REMOVE SCOPES**.
    *   In the filter box, type `docs`.
    *   Check the box for `.../auth/documents` (Google Docs API).
    *   Click **UPDATE**.
    *   Click **SAVE AND CONTINUE**.
5.  **Test Users (THE FIX FOR 403 ERROR)**:
    *   Click **ADD USERS**.
    *   **Enter your own Gmail address** (the one you are logging in with).
    *   Click **ADD**.
    *   *Verify your email appears in the list.*
    *   Click **SAVE AND CONTINUE**.
6.  **Summary**:
    *   Click **BACK TO DASHBOARD**.

## Phase 3: Create Credentials

1.  **Go to Credentials**:
    *   Click **Credentials** in the left sidebar (under APIs & Services).
2.  **Create OAuth Client ID**:
    *   Click **+ CREATE CREDENTIALS** (top of screen).
    *   Select **OAuth client ID**.
3.  **Application Type**:
    *   Select **Desktop app**.
    *   Name: `Desktop Client 1`.
    *   Click **CREATE**.
4.  **Download JSON**:
    *   A popup will appear saying "OAuth client created".
    *   Click the **DOWNLOAD JSON** button (icon looks like a down arrow).
    *   Click **OK**.
5.  **Setup for Python**:
    *   Find the downloaded file (usually named `client_secret_... .json`).
    *   **Rename** it to `credentials.json`.
    *   **Move** it to your project folder: `d:\Video style analysis for AI synthesis system\`.

## Phase 4: Reset & Run

1.  **Delete Old Token**:
    *   If you have a `token.json` file in your project folder, **DELETE IT**. It contains the old/bad login info.
2.  **Run the Test**:
    *   Open your terminal in the project folder.
    *   Run: `python test_google_auth.py`
3.  **Authorize**:
    *   A browser window will open.
    *   **Select your account** (the one you added to Test Users).
    *   **Warning Screen**: You might see "Google hasn't verified this app". this is normal for your own dev apps.
        *   Click **Advanced** (small text link).
        *   Click **Go to Video Synthesis App (unsafe)**.
    *   Click **Continue** / **Allow** on the next screens.
    *   You should see "The authentication flow has completed" in the browser.
    *   Close the tab.
4.  **Check Terminal**:
    *   You should see `✅ Document created successfully`.
