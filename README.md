# 🎵 Music Player

A personal music player built from scratch in Python with a clean dark UI, spinning vinyl disk, dynamic backgrounds, and YouTube search & download.

![Python](https://img.shields.io/badge/Python-3.12+-blue) ![pygame](https://img.shields.io/badge/pygame--ce-latest-green) ![customtkinter](https://img.shields.io/badge/customtkinter-latest-purple)

---

## Features

- **Spinning vinyl disk** — album art cropped into a rotating disk with vinyl ring grooves
- **Dynamic background** — animated gradient that shifts color to match the album art
- **Wavy progress scrubber** — waves while playing, flattens when paused
- **YouTube search & download** — type a song name, hit Enter, it downloads and plays automatically
- **iTunes metadata** — fetches real title, artist, and high quality album art via iTunes API
- **Persistent playlist** — your library saves automatically and reloads on next launch
- **Shuffle & repeat** — repeat one, repeat all, or shuffle mode
- **Volume slider** — with low/high icons
- **Delete tracks** — remove songs from sidebar with one click
- **Auto play next** — automatically advances to the next track when one finishes

---

## Setup

### 1. Install dependencies

```bash
pip install pygame-ce mutagen Pillow colorthief customtkinter numpy yt-dlp musicbrainzngs requests
```

### 2. Install ffmpeg

Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH, or point to it directly in the code.

### 3. YouTube cookies (to bypass 403 errors)

- Install the **"Get cookies.txt LOCALLY"** extension in your browser
- Go to youtube.com while logged in
- Export cookies and save as `cookies.txt` in the same folder as `music_player.py`

### 4. Run

```bash
python music_player.py
```

---

## Usage

| Action | How |
|---|---|
| Add local music | Click **＋ Add Local Music** |
| Search & download | Type song name in search bar → Enter |
| Play / Pause | Click the ⏸ button |
| Next / Previous | Click ⏭ or ⏮ |
| Shuffle | Click ⇌ (lights up when active) |
| Repeat | Click ↺ (cycles off → all → one) |
| Delete track | Click ✕ next to any track in sidebar |
| Volume | Drag the slider at the bottom |

---

## Stack

| Library | Purpose |
|---|---|
| `customtkinter` | Modern dark UI framework |
| `pygame-ce` | Audio playback |
| `Pillow` | Image processing, disk rendering, gradient generation |
| `mutagen` | MP3 tag reading and writing |
| `colorthief` | Dominant color extraction from album art |
| `numpy` | Fast gradient animation |
| `yt-dlp` | YouTube audio download |
| `iTunes Search API` | Track metadata and album art |

---

## Project Structure

```
music_player.py     # entire app — single file
playlist.json       # auto-generated, saves your library
cookies.txt         # YouTube cookies for download (you provide this)
downloads/          # auto-created, downloaded tracks go here
```

---

## Screenshots

> Add screenshots here after first commit

---

## What I Learned

Built entirely from scratch as a learning project covering:
- OOP with tkinter/customtkinter
- Canvas-based animation (gradient, spinning disk, wave scrubber)
- Audio streaming with pygame
- Binary tag reading/writing with mutagen
- Threading for non-blocking downloads
- API integration (iTunes, MusicBrainz)
- numpy for performant pixel manipulation

---

*Built by Sri — BTech CSE, TIET*
