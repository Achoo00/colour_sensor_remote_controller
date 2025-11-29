This Product Requirements Document (PRD) outlines the architecture for **Project ChromaCast**. It is designed to integrate your existing color detection codebase into a new, robust personal media center built with **PyQt6**.

Status tags are used to indicate code reuse:

  * `[EXISTING]`: Reuse code/logic from your previous Color Sensor Remote project.
  * `[MODIFIED]`: Existing code that needs slight adaptation (e.g., threading).
  * `[NEW]`: Completely new modules to be written.

-----

# Product Requirements Document: Project ChromaCast

## 1\. Executive Summary

**ChromaCast** is a gesture-controlled media dashboard. It aggregates a user's public **AniList** "Currently Watching" list and **YouTube** "Watch Later" playlist into a unified PyQt6 GUI. Users interact with the interface and control media playback using real-time color detection (holding up colored objects) via a webcam, replacing the need for a mouse or keyboard.

## 2\. System Architecture

The system moves from a simple loop-based script to an **Event-Driven Architecture** using PyQt6.

```mermaid
graph TD
    A[Webcam] --> B[Vision Worker Thread]
    B -- Signals (e.g., 'RED Detected') --> C[Main GUI (PyQt6)]
    C --> D{Context Manager}
    D -- Context: Dashboard --> E[Navigation Logic]
    D -- Context: Video Player --> F[MPV Controller]
    
    G[AniList API] --> H[Data Manager]
    I[YouTube Playlist] --> H
    H --> C
    
    J[Deluge Daemon] -- Status Updates --> C
    C -- Add Torrent --> J
```

## 3\. Migration & Reuse Strategy

We will reuse the core logic from the previous project but wrap it in PyQt6 "Workers" to prevent freezing the GUI.

| Module | Status | Integration Plan |
| :--- | :--- | :--- |
| **Color Detection (OpenCV)** | `[MODIFIED]` | Move the `while True` loop into a `QThread`. Replace direct `pyautogui` clicks with `pyqtSignal` emissions. |
| **Configuration (JSON)** | `[EXISTING]` | Reuse `config/colors/*.json` for HSV ranges. Reuse `global.json` for ROI. |
| **Action System** | `[REPLACED]` | The old `mouse_click` actions are replaced by direct function calls in the new GUI (e.g., `self.play_video()`). |
| **Calibration Tool** | `[EXISTING]` | Keep the `calibrate.py` script as a standalone utility for setting up colors. |

-----

## 4\. Functional Requirements

### 4.1 Feature: The Vision Driver `[MODIFIED]`

The "eye" of the system. It runs in the background and sends signals to the main app.

  * **Requirements:**
      * Must run on a separate thread (`QThread`) to keep the GUI responsive.
      * Must emit signals: `color_detected(str)` (e.g., "red", "blue").
      * **Debouncing:** Must implement a "cooldown" (e.g., 1.0s) after detecting a color to prevent accidental double-clicks.
      * **Visual Feedback:** The Main GUI must show a small icon indicating which color is currently being detected.
      * **Simulation Mode:** If no camera is detected on startup, the system must fallback to a "Simulation Mode" where it accepts color inputs (e.g., "red", "blue") via the terminal/console.

### 4.2 Feature: The Dashboard (Home Screen) `[NEW]`

The landing page displaying content.

  * **Requirements:**
      * **View:** A grid or list of Anime Covers (fetched from AniList) and Video Thumbnails (fetched from YouTube).
      * **AniList Integration:**
          * Query the **Public** GraphQL API for the user's "CURRENT" list.
          * Display stats: "Progress: Ep 5/12".
      * **YouTube Integration:**
          * Parse a **Public** Playlist URL using `yt-dlp --dump-json`.
          * Display video titles and thumbnails.
      * **Navigation (Color Mapped):**
          * **Blue:** Next Item (Highlight moves right/down).
          * **Red:** Previous Item (Highlight moves left/up).
          * **Green:** Select/Open.

### 4.3 Feature: Anime Download Pipeline `[NEW]`

Automates the acquisition of media via Deluge.

  * **Trigger:** User selects "Download" on an anime tile.
  * **Step 1: Search:** Use `feedparser` to parse Nyaa.si RSS: `https://nyaa.si/?page=rss&q=[Anime Title] [Ep Number]`.
      * *Logic:* Filter for "Trusted" authors (e.g., SubsPlease) and resolution (1080p).
  * **Step 2: Queue:** Send the Magnet Link to the local Deluge Client using `deluge-client`.
  * **Step 3: Monitor:** The Dashboard displays a progress bar for the active download (polling Deluge every 5s).
  * **Step 4: Organization:** Upon completion, a script moves the file to `~/Videos/Anime/[Title]/`.

### 4.4 Feature: Media Playback (MPV) `[NEW]`

Integrated video player within the application.

  * **Technology:** `python-mpv` (embeds MPV into a PyQt widget).
  * **YouTube Playback:** Streams directly via URL (MPV handles this natively).
  * **Local Playback:** Plays the downloaded MKV file.
  * **Controls (Color Mapped):**
      * **Green:** Play/Pause.
      * **Red:** Seek Forward 30s.
      * **Blue:** Close Player / Return to Dashboard.

-----

## 5\. Technical Specifications

### 5.1 Tech Stack

  * **Language:** Python 3.10+
  * **GUI:** PyQt6 (Modern, robust event handling).
  * **CV:** OpenCV (`cv2`), NumPy.
  * **Network:** `gql` (AniList), `feedparser` (Nyaa), `deluge-client`.
  * **Player:** `python-mpv`.
  * **Utilities:** `yt-dlp` (Video metadata extraction).

### 5.2 Directory Structure

```text
/ChromaCast
├── /config                 # [EXISTING] Reuse your old JSONs here
│   ├── colors/
│   └── global.json
├── /assets                 # Icons and cached thumbnails
├── /core
│   ├── vision_worker.py    # [MODIFIED] Threaded version of your CV code
│   ├── anilist_mgr.py      # [NEW] GraphQL queries
│   ├── deluge_mgr.py       # [NEW] Torrent handling
│   └── youtube_mgr.py      # [NEW] yt-dlp parsing
├── /ui
│   ├── main_window.py      # [NEW] The Dashboard
│   └── player_widget.py    # [NEW] MPV Window
└── main.py                 # Application Entry Point
```

### 5.3 Key Logic Snippets

**AniList Public Query (No Auth required):**

```graphql
query ($username: String, $status: MediaListStatus) {
  MediaListCollection(userName: $username, type: ANIME, status: $status) {
    lists {
      entries {
        media {
          title { romaji }
          coverImage { large }
          episodes
        }
        progress
      }
    }
  }
}
```

**Nyaa RSS URL:**
`https://nyaa.si/?page=rss&q={search_term}&c=1_2&f=2`
*(c=1\_2 targets Anime - Translated, f=2 targets Trusted Only)*

## 6\. Implementation Checklist

1.  **Phase 1 (The Eye):** Port existing OpenCV code to a `QThread` and verify it can print "Red Detected" to a PyQt label.
2.  **Phase 2 (The Dashboard):** Build the GUI and fetch data from public AniList/YouTube sources.
3.  **Phase 3 (The Player):** Embed MPV and map Color Signals to Play/Pause functions.
4.  **Phase 4 (The Pipeline):** Implement the Nyaa RSS search and Deluge connection.

## 7\. Known Limitations / Risks

  * **Nyaa Access:** Nyaa.si is blocked by some ISPs. *Mitigation:* Ensure VPN is active or use a proxy domain.
  * **Lighting:** Color detection is sensitive to light changes. *Mitigation:* Keep the `calibrate.py` tool handy to update ranges quickly.
  * **YouTube Rate Limits:** Parsing playlists too frequently may get IP blocked. *Mitigation:* Cache the playlist data and only refresh on app launch.