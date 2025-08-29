# Famly Feed Archiver

A tool to download and archive your Famly daycare photos and posts before account closure.

This tool helps you save all your precious memories from Famly before your child's account gets closed. It downloads all photos, posts, observations, and comments into a beautiful offline HTML archive that you can keep forever.

## Quick Commands (if you have mise installed)

If you already have mise set up, you can use these simple commands:
- `mise download your_feed_file.json` - Download all images
- `mise generate metadata.json` - Generate HTML archive
- `mise archive your_feed_file.json` - Do both steps at once

## Complete Setup Guide

### Step 1: Install mise (the tool manager)

**What is mise?** Mise is a tool that helps manage different programming tools. We use it to make running our scripts easier.

**How to install mise:**

1. **Open your terminal/command prompt:**
   - **On Mac:** Press `Cmd + Space`, type "Terminal", and press Enter
   - **On Windows:** Press `Windows key + R`, type "cmd", and press Enter
   - **On Linux:** Press `Ctrl + Alt + T`

2. **Install mise by copying and pasting this command:**
   ```bash
   curl https://mise.run | sh
   ```
   
   For more installation options, visit: https://mise.jdx.dev/installing-mise.html

3. **Restart your terminal** (close it and open a new one)

4. **Navigate to this project folder** in your terminal:
   ```bash
   cd path/to/famly-archiver
   ```
   (Replace `path/to/famly-archiver` with the actual path where you downloaded this project)

5. **Install the project dependencies:**
   ```bash
   mise install
   ```

### Step 2: Capture Your Famly Feed Data

**You need to capture your feed data from the Famly website first.**

1. **Open your web browser** (Firefox or Chrome work best)

2. **Go to the Famly website:** Type `app.famly.co` in the address bar and press Enter

3. **Log in** to your Famly account with your username and password

4. **Open the Developer Console:**
   - **On Mac:** Press `Cmd + Option + I`
   - **On Windows/Linux:** Press `F12` or `Ctrl + Shift + I`
   - **Alternative:** Right-click anywhere on the page and select "Inspect" or "Inspect Element"

5. **Find the Console tab:**
   - You'll see several tabs like "Elements", "Console", "Network", etc.
   - Click on the **"Console"** tab

6. **Load the capture script:**
   - Open the file called `famly_capture.js` (in the same folder as this README)
   - Copy ALL the text from that file (`Ctrl+A` to select all, then `Ctrl+C` to copy)
   - Go back to your browser console
   - Click in the console area (where it says something like `>`)
   - Paste the code (`Ctrl+V`) and press Enter

7. **Start capturing:**
   - Type this command in the console: `famlyCapture.start()`
   - Press Enter
   - You should see a green message saying capture has started

8. **Scroll through your entire feed:**
   - **Important:** Scroll slowly through your ENTIRE feed from newest to oldest
   - Go all the way back to your child's first posts
   - The script captures data as the website loads it
   - You'll see messages in the console showing what's being captured

9. **Stop capturing:**
   - When you've scrolled through everything, type: `famlyCapture.stop()`
   - Press Enter

10. **Download your data:**
    - Type: `famlyCapture.download()`
    - Press Enter
    - A file will download (something like `famly_feed_2025-08-29.json`)
    - **Remember where this file is saved!**

### Step 3: Create Your Archive

**Now we'll turn your captured data into a beautiful offline archive.**

1. **Go back to your terminal** (the black window with text)

2. **Make sure you're in the right folder:**
   ```bash
   cd path/to/famly-archiver
   ```

3. **Run the archiver:**
   ```bash
   mise archive path/to/your/downloaded/famly_feed_file.json
   ```
   
   **Replace `path/to/your/downloaded/famly_feed_file.json` with the actual path to the file you downloaded.**
   
   **Example:** If your file is in your Downloads folder and called `famly_feed_2025-08-29.json`, you might type:
   ```bash
   mise archive ~/Downloads/famly_feed_2025-08-29.json
   ```

4. **Wait for it to finish:**
   - The tool will download all your photos (this might take a while!)
   - You'll see progress messages showing what's happening
   - When it's done, you'll see a success message with the location of your archive

5. **Open your archive:**
   - The tool will create a folder like `famly_archive_2025-08-29`
   - Inside that folder, open `index.html` in your web browser
   - **This is your complete offline archive!**

## What You Get

Your archive will include:
- **Beautiful HTML website** that looks just like Famly but works offline
- **All your photos** downloaded in full resolution
- **All posts and observations** with original text and formatting
- **Development area tags** and learning assessments
- **Likes and comments** from teachers and other parents
- **Complete offline viewing** - no internet required once created

## Files in This Project

- `famly_capture.js` - Browser script to capture feed data from Famly website
- `famly_downloader.py` - Downloads all images from your feed data
- `famly_generator.py` - Creates the HTML archive website
- `famly_archiver.py` - Runs both download and generate steps together
- `README.md` - This instruction file

## Helpful Tips

- **Scroll slowly** through your feed to make sure all posts load properly
- **Check progress** by typing `famlyCapture.status()` in the browser console
- **Multiple sessions** - You can run the capture multiple times; the script removes duplicates
- **Large feeds** - If you have lots of photos, downloading might take 10-30 minutes
- **Save everything** - The tool captures posts, observations, photos, and even development assessments

## Troubleshooting

**"The script isn't working"**
- Make sure you're on `app.famly.co` (not a different Famly URL)
- Try refreshing the page and running the script again
- Check that you pasted the entire `famly_capture.js` file

**"Images aren't downloading"**
- Check your internet connection
- Some very old images might have expired links (this is normal)
- The script will skip broken images and continue with the rest

**"I can't find my downloaded file"**
- Check your browser's Downloads folder
- The file will be named something like `famly_feed_2025-08-29.json`

**"The terminal commands don't work"**
- Make sure you're in the right folder (`cd path/to/famly-archiver`)
- Try the alternative method without mise (see above)
- On Windows, you might need to use `python` instead of `python3`

**"I'm not comfortable with the terminal"**
- Ask a tech-savvy friend or family member to help
- The browser part (Step 2) is the most important - you can always get help with the terminal part later

## Privacy & Security

- **Everything runs on your computer** - no data is sent to external servers
- **Only downloads from Famly** - the tool only contacts Famly's servers to download your own photos
- **No account access** - the tool doesn't store or transmit your login information
- **Your data stays yours** - all files are saved locally on your computer

## Need Help?

If you get stuck:
1. **Read the error messages** - they often tell you exactly what's wrong
2. **Try the alternative method** without mise if the main method doesn't work
3. **Ask for help** - find someone comfortable with computers to assist you
4. **Take your time** - there's no rush, and you can always try again

Remember: The most important step is capturing your data from the Famly website (Step 2). Once you have that JSON file downloaded, you can always get help with the rest later!
