import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_PATH = os.path.join(BASE_PATH, 'docs')
# News thumbnails are cached here rather than under docs/, which is wiped on
# every build. copy_assets() publishes them to docs/assets/news.
NEWS_IMAGE_PATH = os.path.join(BASE_PATH, 'assets', 'news')
NEWS_IMAGE_URL_BASE = '/assets/news'
# Long-form write-ups for individual papers. The spreadsheet holds the paper
# list; the prose and its images live here, where they can be edited and
# reviewed like any other file.
RESEARCH_PATH = os.path.join(BASE_PATH, 'research')
RESEARCH_URL_BASE = '/research'
# One file per stage of the safety pipeline, describing the research behind it.
TOPICS_PATH = os.path.join(BASE_PATH, 'topics')

def get_secret(name):
    # GitHub Actions exposes action inputs as INPUT_*, so check that first and
    # fall back to a plain environment variable for local builds.
    # Secrets pasted into the GitHub UI often keep a trailing newline, which
    # would end up inside the request URL.
    value = (os.getenv('INPUT_%s' % name, '') or os.getenv(name, '')).strip()
    if not value:
        raise RuntimeError(
            '%s is not set. Add it as a repository secret under '
            'Settings > Secrets and variables > Actions, or export it in your '
            'shell to build locally.' % name)
    return value

API_KEY = get_secret('API_KEY')
DATA_URL = get_secret('DATA_URL')
