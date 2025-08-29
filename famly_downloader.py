#!/usr/bin/env python3
"""
Famly Image Downloader
Downloads images from Famly feed data and creates a metadata file.
"""

import json
import os
import sys
import requests
from urllib.parse import urlparse
from pathlib import Path
import re

class FamlyDownloader:
    def __init__(self, json_file, output_dir=None):
        self.json_file = json_file
        
        # Extract timestamp from filename if not provided
        if output_dir is None:
            # Look for pattern like famly_feed_2025-08-29_20h25m.json
            match = re.search(r'famly_feed_(\d{4}-\d{2}-\d{2}_\d{2}h\d{2}m)', json_file)
            if match:
                timestamp = match.group(1)
                output_dir = f"famly_archive_{timestamp}"
            else:
                output_dir = "famly_archive"
        
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        
        # Load feed data
        with open(json_file, 'r') as f:
            self.feed_data = json.load(f)
        
        # Create observation lookup dictionary
        self.observations = {}
        if 'observations' in self.feed_data:
            for obs in self.feed_data['observations']:
                self.observations[obs['id']] = obs
    
    def download_image(self, image_url, image_id):
        """Download an image and return the local filename"""
        try:
            # Use the big image URL for better quality
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Get file extension from URL
            parsed_url = urlparse(image_url)
            path_parts = parsed_url.path.split('.')
            ext = path_parts[-1] if len(path_parts) > 1 else 'jpg'
            
            # Clean extension (remove query params)
            ext = ext.split('?')[0]
            
            filename = f"{image_id}.{ext}"
            filepath = self.images_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error downloading {image_url}: {e}")
            return None
    
    def download_observation_image(self, image_data):
        """Download an observation image from GraphQL format"""
        try:
            secret = image_data['secret']
            # Use the exact URL format: prefix/key/WIDTHxHEIGHT/path?expires=EXPIRES
            width = image_data.get('width', 520)
            height = image_data.get('height', 1040)
            
            # Build URL matching the working format
            image_url = f"{secret['prefix']}/{secret['key']}/{width}x{height}/{secret['path']}"
            if secret.get('expires'):
                # URL encode the expires parameter properly
                expires = secret['expires'].replace(':', '%3A').replace('+', '%2B')
                image_url += f"?expires={expires}"
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Get file extension from path
            path_parts = secret['path'].split('.')
            ext = path_parts[-1] if len(path_parts) > 1 else 'jpg'
            
            filename = f"{image_data['id']}.{ext}"
            filepath = self.images_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded observation image: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error downloading observation image: {e}")
            return None
    
    def process_feed_item(self, item, current_index=None, total_items=None):
        """Process a single feed item and download its images"""
        progress_info = ""
        if current_index is not None and total_items is not None:
            percentage = (current_index / total_items) * 100
            progress_info = f" [{current_index}/{total_items} - {percentage:.1f}%]"
        
        print(f"Processing feed item: {item.get('feedItemId', 'unknown')}{progress_info}")
        
        # Download images
        local_images = []
        if 'images' in item:
            for image in item['images']:
                # Use url_big for better quality, fallback to url
                image_url = image.get('url_big', image.get('url'))
                if image_url:
                    local_filename = self.download_image(image_url, image['imageId'])
                    if local_filename:
                        local_images.append({
                            'filename': local_filename,
                            'width': image.get('width', 0),
                            'height': image.get('height', 0),
                            'createdAt': image.get('createdAt', {}).get('date', ''),
                            'tags': image.get('tags', [])
                        })
        
        # Check if this is an observation embed and download observation images
        observation_images = []
        embed = item.get('embed')
        if embed and embed.get('type') == 'Observation':
            observation_id = embed.get('observationId')
            if observation_id and observation_id in self.observations:
                obs = self.observations[observation_id]
                if obs.get('images'):
                    for obs_image in obs['images']:
                        local_filename = self.download_observation_image(obs_image)
                        if local_filename:
                            observation_images.append({
                                'filename': local_filename,
                                'width': obs_image.get('width', 0),
                                'height': obs_image.get('height', 0),
                                'id': obs_image['id']
                            })
        
        return {
            'feedItemId': item.get('feedItemId', ''),
            'sender': item.get('sender', {}),
            'receivers': item.get('receivers', []),
            'body': item.get('body', ''),
            'richTextBody': item.get('richTextBody', ''),
            'createdDate': item.get('createdDate', ''),
            'images': local_images,
            'likes': item.get('likes', []),
            'comments': item.get('comments', []),
            'embed': embed,
            'observation_images': observation_images
        }
    
    def download_all_images(self):
        """Download all images and create metadata file"""
        print(f"🚀 Starting image download from {self.json_file}")
        print(f"📁 Output directory: {self.output_dir}")
        
        feed_items = self.feed_data.get('feedItems', [])
        print(f"📸 Found {len(feed_items)} feed items to process")
        
        # Sort by date (newest first)
        feed_items.sort(key=lambda x: x.get('createdDate', ''), reverse=True)
        
        # Process each feed item
        processed_items = []
        total_items = len(feed_items)
        print(f"\n📋 Starting to download images from {total_items} feed items...")
        
        for i, item in enumerate(feed_items, 1):
            processed_item = self.process_feed_item(item, i, total_items)
            processed_items.append(processed_item)
            
            # Show progress every 10 items or at the end
            if i % 10 == 0 or i == total_items:
                percentage = (i / total_items) * 100
                print(f"📊 Progress: {i}/{total_items} items processed ({percentage:.1f}%)")
        
        # Save metadata for HTML generation
        metadata = {
            'processed_items': processed_items,
            'observations': self.observations,
            'export_date': self.feed_data.get('exportDate'),
            'total_items': len(processed_items)
        }
        
        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        total_photos = sum(len(item['images']) + len(item.get('observation_images', [])) for item in processed_items)
        print(f"\n✅ Image download completed!")
        print(f"📁 Location: {self.output_dir.absolute()}")
        print(f"📊 Downloaded: {total_photos} photos from {len(processed_items)} posts")
        print(f"💾 Metadata saved to: {metadata_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python famly_downloader.py <feed_data.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    
    downloader = FamlyDownloader(json_file)
    downloader.download_all_images()

if __name__ == "__main__":
    main()
