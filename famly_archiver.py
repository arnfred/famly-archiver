#!/usr/bin/env python3
"""
Famly Feed Archiver
Downloads images and creates a static HTML archive from Famly feed data.
"""

import json
import os
import sys
import requests
from urllib.parse import urlparse
from datetime import datetime
import html
from pathlib import Path
import re

class FamlyArchiver:
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
            image_url = f"{secret['prefix']}/{secret['key']}"
            
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
    
    def format_date(self, date_str):
        """Format date string for display"""
        try:
            # Parse the date from the feed
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_str
    
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
        
        # Check if this is an observation embed
        observation_data = None
        embed = item.get('embed')
        if embed and embed.get('type') == 'Observation':
            observation_id = embed.get('observationId')
            if observation_id and hasattr(self, 'observations'):
                observation_data = self.observations.get(observation_id)
        
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
            'observation': observation_data
        }
    
    def generate_html(self, processed_items):
        """Generate the HTML archive"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Famly Feed Archive</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .feed-item {{
            background: white;
            border-radius: 12px;
            margin-bottom: 24px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .sender {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }}
        .sender-image {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 12px;
            background-color: #ddd;
        }}
        .sender-info {{
            flex: 1;
        }}
        .sender-name {{
            font-weight: 600;
            color: #333;
        }}
        .post-date {{
            color: #666;
            font-size: 14px;
        }}
        .receivers {{
            color: #666;
            font-size: 14px;
            margin-bottom: 12px;
        }}
        .post-body {{
            margin-bottom: 16px;
            line-height: 1.5;
        }}
        .images-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}
        .image-container {{
            position: relative;
        }}
        .image-container img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            cursor: pointer;
        }}
        .likes {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 14px;
        }}
        .like {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .archive-header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: white;
            border-radius: 12px;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 16px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: 600;
            color: #333;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .observation {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 16px;
            margin: 16px 0;
            border-radius: 4px;
        }}
        .observation h4 {{
            margin: 0 0 12px 0;
            color: #007bff;
        }}
        .observation-text {{
            margin: 12px 0;
            line-height: 1.5;
        }}
        .development-areas {{
            margin: 12px 0;
        }}
        .area-tag {{
            display: inline-block;
            background: #e9ecef;
            padding: 4px 8px;
            margin: 2px 4px 2px 0;
            border-radius: 12px;
            font-size: 12px;
            color: #495057;
        }}
    </style>
</head>
<body>
    <div class="archive-header">
        <h1>Famly Feed Archive</h1>
        <p>Exported on {datetime.now().strftime("%B %d, %Y")}</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(processed_items)}</div>
                <div class="stat-label">Posts</div>
            </div>
            <div class="stat">
                <div class="stat-number">{sum(len(item['images']) for item in processed_items)}</div>
                <div class="stat-label">Photos</div>
            </div>
        </div>
    </div>
"""
        
        for item in processed_items:
            sender = item['sender']
            sender_name = html.escape(sender.get('name', 'Unknown'))
            post_date = self.format_date(item['createdDate'])
            receivers = ', '.join(item['receivers']) if item['receivers'] else ''
            
            # Use richTextBody if available, otherwise use body
            post_body = item.get('richTextBody', item.get('body', ''))
            if post_body and not post_body.startswith('<'):
                post_body = html.escape(post_body).replace('\n', '<br>')
            elif not post_body:
                post_body = ''
            
            html_content += f"""
    <div class="feed-item">
        <div class="sender">
            <div class="sender-image"></div>
            <div class="sender-info">
                <div class="sender-name">{sender_name}</div>
                <div class="post-date">{post_date}</div>
            </div>
        </div>
"""
            
            if receivers:
                html_content += f'        <div class="receivers">To: {html.escape(receivers)}</div>\n'
            
            if post_body:
                html_content += f'        <div class="post-body">{post_body}</div>\n'
            
            # Handle regular images
            if item['images']:
                html_content += '        <div class="images-grid">\n'
                for image in item['images']:
                    html_content += f"""            <div class="image-container">
                <img src="images/{image['filename']}" alt="Photo" loading="lazy">
            </div>
"""
                html_content += '        </div>\n'
            
            # Handle observation content
            if item.get('observation'):
                obs = item['observation']
                html_content += '        <div class="observation">\n'
                html_content += '            <h4>📝 Observation</h4>\n'
                
                # Observation author
                if obs.get('createdBy'):
                    author = obs['createdBy']['name']['fullName']
                    html_content += f'            <p><strong>Observer:</strong> {html.escape(author)}</p>\n'
                
                # Observation remark
                if obs.get('remark'):
                    remark = obs['remark']
                    remark_body = remark.get('richTextBody', remark.get('body', ''))
                    if remark_body:
                        html_content += f'            <div class="observation-text">{remark_body}</div>\n'
                    
                    # Development areas
                    if remark.get('areas'):
                        html_content += '            <div class="development-areas">\n'
                        html_content += '                <strong>Development Areas:</strong>\n'
                        for area in remark['areas']:
                            area_info = area['area']
                            refinement = area.get('refinement', '')
                            html_content += f'                <span class="area-tag">{html.escape(area_info["title"])} ({refinement})</span>\n'
                        html_content += '            </div>\n'
                
                # Observation images
                if obs.get('images'):
                    html_content += '            <div class="images-grid">\n'
                    for obs_image in obs['images']:
                        local_filename = self.download_observation_image(obs_image)
                        if local_filename:
                            html_content += f"""                <div class="image-container">
                    <img src="images/{local_filename}" alt="Observation Photo" loading="lazy">
                </div>
"""
                    html_content += '            </div>\n'
                
                html_content += '        </div>\n'
            
            if item['likes']:
                html_content += '        <div class="likes">\n'
                for like in item['likes']:
                    reaction = like.get('reaction', '❤️')
                    name = html.escape(like.get('name', 'Someone'))
                    html_content += f'            <div class="like">{reaction} {name}</div>\n'
                html_content += '        </div>\n'
            
            html_content += '    </div>\n'
        
        html_content += """
</body>
</html>"""
        
        return html_content
    
    def create_archive(self):
        """Create the complete archive"""
        print(f"🚀 Creating archive from {self.json_file}")
        print(f"📁 Output directory: {self.output_dir}")
        
        feed_items = self.feed_data.get('feedItems', [])
        print(f"📸 Found {len(feed_items)} feed items to archive")
        
        # Sort by date (newest first)
        feed_items.sort(key=lambda x: x.get('createdDate', ''), reverse=True)
        
        # Process each feed item
        processed_items = []
        total_items = len(feed_items)
        print(f"\n📋 Starting to process {total_items} feed items...")
        
        for i, item in enumerate(feed_items, 1):
            processed_item = self.process_feed_item(item, i, total_items)
            processed_items.append(processed_item)
            
            # Show progress every 10 items or at the end
            if i % 10 == 0 or i == total_items:
                percentage = (i / total_items) * 100
                print(f"📊 Progress: {i}/{total_items} items processed ({percentage:.1f}%)")
        
        # Generate HTML
        print(f"\n🎨 Generating HTML archive...")
        html_content = self.generate_html(processed_items)
        
        # Write HTML file
        html_file = self.output_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        total_photos = sum(len(item['images']) for item in processed_items)
        print(f"\n✅ Archive created successfully!")
        print(f"📁 Location: {self.output_dir.absolute()}")
        print(f"🌐 Open: {html_file.absolute()}")
        print(f"📊 Final stats: {len(processed_items)} posts, {total_photos} photos archived")

def main():
    if len(sys.argv) != 2:
        print("Usage: python famly_archiver.py <feed_data.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    
    archiver = FamlyArchiver(json_file)
    archiver.create_archive()

if __name__ == "__main__":
    main()
