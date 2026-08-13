import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_PATH = os.path.join(BASE_PATH, 'docs')

def get_secret(name):
    # GitHub Actions exposes action inputs as INPUT_*, so check that first and
    # fall back to a plain environment variable for local builds.
    value = os.getenv('INPUT_%s' % name, '') or os.getenv(name, '')
    if not value:
        raise RuntimeError(
            '%s is not set. Add it as a repository secret under '
            'Settings > Secrets and variables > Actions, or export it in your '
            'shell to build locally.' % name)
    return value

API_KEY = get_secret('API_KEY')
DATA_URL = get_secret('DATA_URL')
