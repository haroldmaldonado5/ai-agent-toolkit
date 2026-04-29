# C5M Muxic Player — Build Walkthrough

## Result

![C5M Muxic Player](C:\Users\cu5to\.gemini\antigravity\brain\ad671984-d21e-42b3-8481-c7525ed3d0ac\player_screenshot.png)

## What Was Built

A full-stack Game Boy Advance SP-style music player running on **http://localhost:3000**

---

## Files Created

| File | Purpose |
|------|---------|
| `package.json` | Dependencies: express, multer, music-metadata, cors |
| `server.js` | Express backend on port 3000 |
| `public/index.html` | 🎮 Game Boy player UI |
| `public/admin.html` | 🔐 Admin panel for uploading songs |
| `public/uploads/` | Auto-created folder for MP3 storage |

---

## Features

### 🎮 Player (`/`)
- **Pixel-perfect Game Boy Advance SP** design in sage green
- **LCD screen** with scanline effect, POWER ON / BATTERY FULL status bar
- **Now Playing** display: album art, title, artist, album
- **Blue progress bar** with click-to-seek
- **Time display**: current time + remaining (negative)
- **D-Pad**: Up/Down = prev/next track | Left/Right = seek ±10s
- **Play / Pause** action buttons
- **Shuffle** toggle button (glows green when active)
- **Prev / Next** bottom navigation buttons
- **Song list overlay** (click center of D-Pad ring)
- **Keyboard shortcuts**: Space=play/pause, ←→=prev/next, ↑↓=seek, S=shuffle, L=list
- **Range-based MP3 streaming** (seek without full download)

### 🔐 Admin Panel (`/admin.html`)
- Password gate: **`admin123`**
- **Drag & drop** or file picker for multiple MP3s
- **Upload progress** queue with per-file status
- **Auto metadata extraction**: title, artist, album, duration, embedded artwork
- **Stats dashboard**: total songs, total size, total duration
- **Song library table** with delete buttons
- **Toast notifications** for all actions

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/songs` | List all songs with metadata |
| POST | `/api/songs/upload` | Upload multiple MP3s (multipart) |
| DELETE | `/api/songs/:filename` | Delete a song by filename |
| GET | `/uploads/:filename` | Stream MP3 with HTTP range support |
| POST | `/api/admin/login` | Auth check (password: admin123) |

---

## How to Use

1. **Start server**: `node server.js` (already running)
2. **Upload songs**: Go to http://localhost:3000/admin.html → password `admin123` → drag MP3s
3. **Play music**: Go to http://localhost:3000 → songs appear automatically
