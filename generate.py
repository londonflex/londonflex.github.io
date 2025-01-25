import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_channel_id(channel_name):
    url = f"https://www.youtube.com/@{channel_name}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for script in soup.find_all('script'):
        if 'channelId' in str(script):
            return str(script).split('"channelId":"')[1].split('"')[0]
    return None

def generate_html(videos):
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Latest YouTube Videos</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
            .video { border: 1px solid #ddd; padding: 10px; border-radius: 8px; }
            img { width: 100%; border-radius: 4px; }
            a { color: #000; text-decoration: none; }
            .date { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="grid">
    '''
    
    for video in sorted(videos, key=lambda x: x['date'], reverse=True):
        html += f'''
            <div class="video">
                <a href="{video['link']}" target="_blank">
                    <img src="{video['thumbnail']}" alt="{video['title']}">
                    <h3>{video['title']}</h3>
                    <p class="date">{video['date'].strftime('%Y-%m-%d')}</p>
                </a>
            </div>
        '''
    
    html += '''
        </div>
    </body>
    </html>
    '''
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    videos = []
    with open('channels.txt') as f:
        channels = [line.strip() for line in f if line.strip()]
    
    for channel in channels:
        time.sleep(1)  # Avoid rate limiting
        channel_id = get_channel_id(channel)
        if not channel_id:
            continue
            
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:5]:  # Get latest 5 videos from each channel
            videos.append({
                'title': entry.title,
                'link': entry.link,
                'date': datetime.strptime(entry.published[:19], '%Y-%m-%dT%H:%M:%S'),
                'thumbnail': f"https://i.ytimg.com/vi/{entry.yt_videoid}/mqdefault.jpg"
            })
    
    generate_html(videos)

if __name__ == "__main__":
    main()
