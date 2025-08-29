#!/usr/bin/env python3
"""
Famly Posts Image Extractor
Extracts and copies images that appear in posts-only.html to a separate directory.
"""

import json
import os
import sys
import shutil
from pathlib import Path
import re

class FamlyPostsExtractor:
    def __init__(self, metadata_file):
        self.metadata_file = Path(metadata_file)
        self.archive_dir = self.metadata_file.parent
        self.images_dir = self.archive_dir / "images"
        self.posts_images_dir = self.archive_dir / "post_images"
        
        # Create post_images directory
        self.posts_images_dir.mkdir(exist_ok=True)
        
        # Load metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        self.processed_items = self.metadata['processed_items']
    
    def get_posts_only_images(self):
        """Get list of images that appear in posts-only (not observations)"""
        posts_only = [item for item in self.processed_items 
                     if not (item.get('embed') and item.get('embed', {}).get('type') == 'Observation')]
        
        image_filenames = []
        for item in posts_only:
            if item.get('images'):
                for image in item['images']:
                    image_filenames.append(image['filename'])
        
        return image_filenames
    
    def copy_posts_images(self):
        """Copy images from posts-only to the post_images directory"""
        print(f"🎯 Extracting post images from {self.metadata_file}")
        print(f"📁 Archive directory: {self.archive_dir}")
        print(f"📂 Post images directory: {self.posts_images_dir}")
        
        # Get list of images used in posts-only
        posts_image_filenames = self.get_posts_only_images()
        
        if not posts_image_filenames:
            print("⚠️  No post images found to extract")
            return
        
        print(f"📸 Found {len(posts_image_filenames)} images in posts-only")
        
        copied_count = 0
        failed_count = 0
        
        for filename in posts_image_filenames:
            source_path = self.images_dir / filename
            dest_path = self.posts_images_dir / filename
            
            try:
                if source_path.exists():
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
                    print(f"Copied: {filename}")
                else:
                    print(f"⚠️  Source not found: {filename}")
                    failed_count += 1
            except Exception as e:
                print(f"❌ Error copying {filename}: {e}")
                failed_count += 1
        
        print(f"\n✅ Post images extraction completed!")
        print(f"📊 Results: {copied_count} copied, {failed_count} failed")
        print(f"📁 Post images location: {self.posts_images_dir.absolute()}")
        
        # Calculate total size
        try:
            total_size = sum(f.stat().st_size for f in self.posts_images_dir.glob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            print(f"💾 Total size: {size_mb:.1f} MB")
        except Exception as e:
            print(f"⚠️  Could not calculate total size: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python famly_extract_posts.py <metadata.json>")
        sys.exit(1)
    
    metadata_file = sys.argv[1]
    if not os.path.exists(metadata_file):
        print(f"Error: File {metadata_file} not found")
        sys.exit(1)
    
    extractor = FamlyPostsExtractor(metadata_file)
    extractor.copy_posts_images()

if __name__ == "__main__":
    main()
