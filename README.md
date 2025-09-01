# Famly Archiver

A tool to help download and archive photos and posts from the daycare platform Famly. It downloads all photos, posts, observations, and composes an offline HTML archive that links against photos on disk.

## How to Use

The process of downloading photos is a bit manual, I'm afraid. 

**Part 1** - Download feed data:
 * Log in to Famly in your browser
 * Right click on the page and click "Inspect"
 * At the bottom you can now click "Console"
 * Copy/Paste the entire content of [family_capture.js](https://raw.githubusercontent.com/arnfred/famly-archiver/refs/heads/main/famly_capture.js) in to the console
 * Write `famlyCapture.start()` in the console
 * Scroll through the _entire_ feed (this will take a while!)
 * Save the data by writing `famlyCapture.download()`

**Part 2** - Download Images:

If you already have [mise](https://mise.jdx.dev/) set up, clone this directory, copy the feed file you've downloaded from firefox and run `mise run download <name of feed file.json>`.
If not, visit: https://mise.jdx.dev/installing-mise.html

Once all images have been downloaded, run `mise run generate famly_archive/metadata.json` to create the html file in `./famly_archive`.
