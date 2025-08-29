# Famly Feed Archiver

A tool to download and archive your Famly daycare photos and posts before account closure.

## Quick Start

### Step 1: Capture Feed Data

1. Open Firefox and go to `app.famly.co`
2. Log in to your account
3. Open Developer Tools (F12)
4. Go to the Console tab
5. Copy and paste the entire contents of `famly_capture.js` into the console and press Enter
6. Start capturing: `famlyCapture.start()`
7. Scroll through your entire feed to load all posts (scroll slowly to ensure all data loads)
8. When done: `famlyCapture.stop()`
9. Download the data: `famlyCapture.download()`

This will download a JSON file with all your feed data.

### Step 2: Create Archive

1. Install Python dependencies:
   ```bash
   pip install requests
   ```

2. Run the archiver:
   ```bash
   python famly_archiver.py your_downloaded_feed.json
   ```

3. Open the generated `famly_archive/index.html` in your browser

## What You Get

- **Static HTML file** with all your posts, photos, and metadata
- **Downloaded images** in full resolution
- **Preserved data**: dates, senders, receivers, likes, comments
- **Offline viewing** - no internet required once created

## Files

- `famly_capture.js` - Browser script to capture feed data
- `famly_archiver.py` - Python script to download images and create HTML archive
- `README.md` - This file

## Tips

- **Scroll slowly** through your feed to ensure all posts load
- **Check the console** for capture progress with `famlyCapture.status()`
- **Multiple sessions** - You can run the capture multiple times and the script will deduplicate
- **Large feeds** - The archiver handles large feeds but may take time to download all images

## Troubleshooting

- If images fail to download, check your internet connection
- If the browser script doesn't work, make sure you're on `app.famly.co`
- For large feeds, the download may take several minutes

## Privacy

This tool runs entirely locally - no data is sent to external servers except to download the images from Famly's CDN.
