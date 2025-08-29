#!/usr/bin/env python3
"""
Famly HTML Generator
Generates a static HTML archive from downloaded images and metadata.
"""

import json
import os
import sys
from datetime import datetime
import html
from pathlib import Path

class FamlyGenerator:
    def __init__(self, metadata_file):
        self.metadata_file = Path(metadata_file)
        self.output_dir = self.metadata_file.parent
        
        # Load metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        self.processed_items = self.metadata['processed_items']
        self.observations = self.metadata.get('observations', {})
    
    def format_date(self, date_str):
        """Format date string for display"""
        try:
            # Parse the date from the feed
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_str
    
    def generate_html(self):
        """Generate the HTML archive"""
        total_photos = sum(len(item['images']) + len(item.get('observation_images', [])) for item in self.processed_items)
        
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
        .navigation {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .nav-link {{
            display: inline-block;
            padding: 8px 16px;
            margin: 0 8px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        }}
        .nav-link:hover {{
            background: #0056b3;
        }}
        .nav-link.current {{
            background: #28a745;
        }}
    </style>
</head>
<body>
    <div class="navigation">
        <a href="index.html" class="nav-link current">All Posts & Observations</a>
        <a href="posts-only.html" class="nav-link">Posts Only</a>
    </div>
    
    <div class="archive-header">
        <h1>Famly Feed Archive</h1>
        <p>Exported on {datetime.now().strftime("%B %d, %Y")}</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(self.processed_items)}</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat">
                <div class="stat-number">{total_photos}</div>
                <div class="stat-label">Photos</div>
            </div>
        </div>
    </div>
"""
        
        for item in self.processed_items:
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
            embed = item.get('embed')
            if embed and embed.get('type') == 'Observation':
                observation_id = embed.get('observationId')
                if observation_id and observation_id in self.observations:
                    obs = self.observations[observation_id]
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
                    
                    # Observation images (already downloaded)
                    if item.get('observation_images'):
                        html_content += '            <div class="images-grid">\n'
                        for obs_image in item['observation_images']:
                            html_content += f"""                <div class="image-container">
                    <img src="images/{obs_image['filename']}" alt="Observation Photo" loading="lazy">
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
    
    def generate_posts_only_html(self):
        """Generate HTML archive with posts only (no observations)"""
        # Filter out items that are observations
        posts_only = [item for item in self.processed_items 
                     if not (item.get('embed') and item.get('embed', {}).get('type') == 'Observation')]
        
        total_photos = sum(len(item['images']) for item in posts_only)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Famly Feed Archive - Posts Only</title>
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
        .navigation {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .nav-link {{
            display: inline-block;
            padding: 8px 16px;
            margin: 0 8px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        }}
        .nav-link:hover {{
            background: #0056b3;
        }}
        .nav-link.current {{
            background: #28a745;
        }}
    </style>
</head>
<body>
    <div class="navigation">
        <a href="index.html" class="nav-link">All Posts & Observations</a>
        <a href="posts-only.html" class="nav-link current">Posts Only</a>
    </div>
    
    <div class="archive-header">
        <h1>Famly Feed Archive - Posts Only</h1>
        <p>Exported on {datetime.now().strftime("%B %d, %Y")}</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(posts_only)}</div>
                <div class="stat-label">Posts</div>
            </div>
            <div class="stat">
                <div class="stat-number">{total_photos}</div>
                <div class="stat-label">Photos</div>
            </div>
        </div>
    </div>
"""
        
        for item in posts_only:
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
            
            # Handle regular images only
            if item['images']:
                html_content += '        <div class="images-grid">\n'
                for image in item['images']:
                    html_content += f"""            <div class="image-container">
                <img src="images/{image['filename']}" alt="Photo" loading="lazy">
            </div>
"""
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

    def create_html_archive(self):
        """Create the HTML archive"""
        print(f"🎨 Generating HTML archive from {self.metadata_file}")
        print(f"📁 Output directory: {self.output_dir}")
        
        # Generate main HTML with all content
        html_content = self.generate_html()
        
        # Write main HTML file
        html_file = self.output_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate posts-only HTML
        posts_html_content = self.generate_posts_only_html()
        
        # Write posts-only HTML file
        posts_html_file = self.output_dir / "posts-only.html"
        with open(posts_html_file, 'w', encoding='utf-8') as f:
            f.write(posts_html_content)
        
        total_photos = sum(len(item['images']) + len(item.get('observation_images', [])) for item in self.processed_items)
        posts_only_count = len([item for item in self.processed_items 
                               if not (item.get('embed') and item.get('embed', {}).get('type') == 'Observation')])
        
        print(f"\n✅ HTML archive created successfully!")
        print(f"📁 Location: {self.output_dir.absolute()}")
        print(f"🌐 Main archive: {html_file.absolute()}")
        print(f"📝 Posts only: {posts_html_file.absolute()}")
        print(f"📊 Final stats: {len(self.processed_items)} total items ({posts_only_count} posts, {len(self.processed_items) - posts_only_count} observations), {total_photos} photos archived")

def main():
    if len(sys.argv) != 2:
        print("Usage: python famly_generator.py <metadata.json>")
        sys.exit(1)
    
    metadata_file = sys.argv[1]
    if not os.path.exists(metadata_file):
        print(f"Error: File {metadata_file} not found")
        sys.exit(1)
    
    generator = FamlyGenerator(metadata_file)
    generator.create_html_archive()

if __name__ == "__main__":
    main()
