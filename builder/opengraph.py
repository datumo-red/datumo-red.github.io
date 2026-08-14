import certifi
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)
TIMEOUT = 15
# Open Graph tags live in <head>, so there is no reason to read whole pages.
MAX_BYTES = 512 * 1024

class MetaParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.meta = {}
        self.title = ''
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attributes = dict(attrs)
            key = attributes.get('property') or attributes.get('name') or ''
            content = attributes.get('content') or ''
            if key and content:
                # First tag wins; some pages repeat properties.
                self.meta.setdefault(key.lower(), content.strip())
        elif tag == 'title':
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and not self.title:
            self.title = data.strip()

def get_preview(url):
    """Read Open Graph metadata for a link.

    Returns a dict with 'title', 'description', 'image' and 'site_name'. Any
    field the page does not provide comes back as an empty string. Returns None
    when the page cannot be read at all, so the caller can fall back.
    """
    request = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT,
        'Accept-Language': 'ko,en;q=0.8',
    })
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, cafile=certifi.where()) as response:
            charset = response.headers.get_content_charset() or 'utf-8'
            body = response.read(MAX_BYTES)
            final_url = response.geturl()
    except (urllib.error.URLError, OSError, ValueError) as e:
        print('  ! could not read %s: %s' % (url, e))
        return None

    parser = MetaParser()
    try:
        parser.feed(body.decode(charset, 'replace'))
    except AssertionError:
        # HTMLParser gives up on badly broken markup; keep whatever it collected.
        pass

    meta = parser.meta
    image = meta.get('og:image') or meta.get('twitter:image') or ''
    if image:
        # og:image is often protocol-relative or site-relative.
        image = urllib.parse.urljoin(final_url, image)
    return {
        'title': meta.get('og:title') or meta.get('twitter:title') or parser.title,
        'description': meta.get('og:description') or meta.get('twitter:description')
                       or meta.get('description') or '',
        'image': image,
        'site_name': meta.get('og:site_name') or urllib.parse.urlparse(final_url).netloc,
    }
