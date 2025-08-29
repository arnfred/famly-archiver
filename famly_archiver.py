#!/usr/bin/env python3
"""
Famly Feed Archiver (Legacy)
Downloads images and creates a static HTML archive from Famly feed data.
This is the original combined script. Use famly_downloader.py and famly_generator.py for the split workflow.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python famly_archiver.py <feed_data.json>")
        print("This script now runs the split workflow:")
        print("  1. famly_downloader.py - Downloads all images")
        print("  2. famly_generator.py - Generates HTML archive")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    
    print("🔄 Running split workflow...")
    
    # Step 1: Download images
    print("\n📥 Step 1: Downloading images...")
    result = subprocess.run([sys.executable, "famly_downloader.py", json_file])
    if result.returncode != 0:
        print("❌ Image download failed")
        sys.exit(1)
    
    # Step 2: Generate HTML (find metadata.json in the output directory)
    # Extract output directory from the JSON filename
    import re
    match = re.search(r'famly_feed_(\d{4}-\d{2}-\d{2}_\d{2}h\d{2}m)', json_file)
    if match:
        timestamp = match.group(1)
        output_dir = f"famly_archive_{timestamp}"
    else:
        output_dir = "famly_archive"
    
    metadata_file = Path(output_dir) / "metadata.json"
    if not metadata_file.exists():
        print(f"❌ Metadata file not found: {metadata_file}")
        sys.exit(1)
    
    print("\n🎨 Step 2: Generating HTML archive...")
    result = subprocess.run([sys.executable, "famly_generator.py", str(metadata_file)])
    if result.returncode != 0:
        print("❌ HTML generation failed")
        sys.exit(1)
    
    print("\n✅ Complete archive workflow finished!")

if __name__ == "__main__":
    main()
