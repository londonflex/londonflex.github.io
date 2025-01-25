import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

def get_channel_id(channel_name):
   url = f"https://www.youtube.com/@{channel_name}"
   r = requests.get(url)
   soup = BeautifulSoup(r.text, 'html.parser')
   for script in soup.find_all('script'):
       if 'channelId' in str(script):
           return str(script).split('"channelId":"')[1].split('"')[0]
   return None

def get_relative_time(date):
   now = datetime.now()
   diff = now - date
   if diff.days == 0:
       if diff.seconds < 3600:
           return f"{diff.seconds // 60} minutes ago"
       return f"{diff.seconds // 3600} hours ago"
   if diff.days == 1:
       return "Yesterday"
   if diff.days < 7:
       return f"{diff.days} days ago"
   if diff.days < 30:
       weeks = diff.days // 7
       return f"{weeks} week{'s' if weeks > 1 else ''} ago"
   return date.strftime('%b %d, %Y')

def generate_html(videos):
   html = '''
   <!DOCTYPE html>
   <html>
   <head>
       <title>Latest YouTube Videos</title>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1">
       <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
       <style>
           * { margin: 0; padding: 0; box-sizing: border-box; }
           body { 
               background: #121212; 
               font-family: 'Inter', -apple-system, sans-serif;
               color: #E1E1E1;
           }
           .grid { 
               display: grid; 
               grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
               gap: 24px; 
               padding: 32px;
               max-width: 1600px;
               margin: 0 auto;
           }
           .video {
               background: #1E1E1E;
               border-radius: 12px;
               overflow: hidden;
               transition: transform 0.2s;
           }
           .video:hover {
               transform: translateY(-4px);
           }
           .video-info {
               padding: 16px;
           }
           img { 
               width: 100%; 
               height: 200px; 
               object-fit: cover; 
           }
           h3 { 
               font-size: 16px; 
               margin-bottom: 8px;
               line-height: 1.4;
           }
           .channel { 
               font-size: 14px;
               color: #8B5CF6;
               margin-bottom: 8px;
           }
           .date { 
               color: #888; 
               font-size: 14px; 
           }
           a { 
               color: inherit; 
               text-decoration: none; 
           }
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
                   <div class="video-info">
                       <h3>{video['title']}</h3>
                       <div class="channel">{video['channel']}</div>
                       <div class="date">{get_relative_time(video['date'])}</div>
                   </div>
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
           print(f"Failed to get channel ID for: {channel}")
           continue
           
       feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
       feed = feedparser.parse(feed_url)
       
       two_weeks_ago = datetime.now() - timedelta(days=14)
       
       for entry in feed.entries:
           date = datetime.strptime(entry.published[:19], '%Y-%m-%dT%H:%M:%S')
           if date > two_weeks_ago:
               videos.append({
                   'title': entry.title,
                   'link': entry.link,
                   'date': date,
                   'channel': channel,
                   'thumbnail': f"https://i.ytimg.com/vi/{entry.yt_videoid}/mqdefault.jpg"
               })
   
   generate_html(videos)

if __name__ == "__main__":
   main()
