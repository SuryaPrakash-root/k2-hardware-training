import re
from urllib.parse import urlparse
from pathlib import Path


def is_youtube_url(url: str) -> bool:
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)',
    ]
    return any(re.search(p, url) for p in patterns)


def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\s?]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def parse_url(url: str) -> dict:
    if is_youtube_url(url):
        return parse_youtube(url)
    else:
        return parse_website(url)


def parse_website(url: str) -> dict:
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            tag.decompose()
        
        title = soup.title.string if soup.title else urlparse(url).path
        
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and ('content' in x.lower() if isinstance(x, str) else any('content' in c.lower() for c in x))) or soup.find('body')
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 20]
        clean_text = '\n\n'.join(lines)
        
        if len(clean_text) < 100:
            return {
                'url': url,
                'title': 'Insufficient Content',
                'text': f'The page at {url} does not contain enough text content to extract. This may be due to JavaScript rendering or access restrictions.',
                'type': 'error'
            }
        
        return {
            'url': url,
            'title': title.strip() if title else 'Untitled',
            'text': clean_text[:50000],
            'type': 'website'
        }
    except requests.exceptions.HTTPError as e:
        return {
            'url': url,
            'title': f'HTTP Error {e.response.status_code}',
            'text': f'The website returned an error: {e.response.status_code} {e.response.reason}. The URL may be invalid or the page may be restricted.',
            'type': 'error'
        }
    except requests.exceptions.ConnectionError:
        return {
            'url': url,
            'title': 'Connection Error',
            'text': f'Could not connect to {url}. Please check the URL and your internet connection.',
            'type': 'error'
        }
    except Exception as e:
        return {
            'url': url,
            'title': 'Error',
            'text': f'Failed to fetch URL: {str(e)}',
            'type': 'error'
        }


def parse_youtube(url: str) -> dict:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        video_id = extract_video_id(url)
        if not video_id:
            return {
                'url': url,
                'title': 'Invalid YouTube URL',
                'text': 'Could not extract video ID from URL',
                'type': 'error'
            }
        
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        
        full_text = ' '.join([entry.text for entry in transcript.snippets])
        
        return {
            'url': url,
            'title': f'YouTube Video: {video_id}',
            'text': full_text,
            'type': 'youtube',
            'video_id': video_id
        }
    except Exception as e:
        return {
            'url': url,
            'title': 'YouTube Error',
            'text': f'Failed to fetch transcript: {str(e)}',
            'type': 'error'
        }
