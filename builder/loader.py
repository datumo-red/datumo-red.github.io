import certifi
import dateutil.parser
import os
import re
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from . import config, opengraph

SHEETS_URL_BASE = 'https://sheets.googleapis.com/v4/spreadsheets'
RANGES = [
    'Website!B2:C',
    'Announcements!A2:C',
    'Members!A2:H',
    'Research!A2:G',
    'Tags!A2:F',
    'Links!A2:G',
    'Pages!A2:C',
    'Redirects!A2:B',
    'Personal!A2:B',
]
PERSONAL_RANGES = [
    'Website!B2:C',
    'Contents!A2:B',
]
# Fetched on its own so that a document without a News tab still builds: one
# unknown range makes the whole batch request fail with a 400.
NEWS_RANGES = [
    'News!A2:E',
]

def get_doc_id(data_url):
    tokens = data_url.split('/')
    doc_id = ''
    # Use a heuristic method for finding document ID from the URL.
    for token in tokens:
        if re.match(r'[a-zA-Z0-9]+', token) is not None:
            if len(token) > len(doc_id):
                doc_id = token
    return doc_id

def load_ranges(doc_id, ranges):
    params = '&'.join(['ranges=%s' % urllib.parse.quote(r) for r in ranges])
    url = '%s/%s/values:batchGet?%s&key=%s' % (SHEETS_URL_BASE, doc_id, params, config.API_KEY)

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, cafile=certifi.where()) as response:
            data = response.read()
    except urllib.error.HTTPError as e:
        # The API explains what went wrong in the response body, which HTTPError hides.
        raise RuntimeError('Sheets API %s for document %s: %s' % (
            e.code, doc_id, e.read().decode('utf-8', 'replace'))) from None
    data_dict = json.loads(data)
    # An empty tab comes back without a 'values' key at all.
    return [r.get('values', []) for r in data_dict['valueRanges']]

def load_optional_ranges(doc_id, ranges):
    try:
        return load_ranges(doc_id, ranges)
    except RuntimeError as e:
        print('Skipping optional ranges %s: %s' % (', '.join(ranges), e))
        return None

def row_to_dict(row, keys, start_at=0):
    i = start_at
    result_dict = {}
    for key in keys:
        if len(row) > i:
            result_dict[key] = row[i]
        else:
            result_dict[key] = ''
        i += 1
    return result_dict

def conv_website(table):
    items = {}
    for row in table:
        items[row[0]] = row[1] if len(row) > 1 else ''
    return items

def conv_announcements(table):
    items = []
    for row in table:
        if row[2]:
            expire_at = dateutil.parser.parse(row[2]) 
            now = datetime.now(timezone.utc)
            if expire_at <= now:
                # This is already expired.
                continue
        items.append({
            'title': row[0],
            'content': row[1]
        })
    return items

def get_group(groups, index, title, items_key):
    """Find or start the section named `title`, keeping first-seen order.

    Rows sharing a section title belong together wherever they sit in the
    sheet, so a row inserted out of place does not split the section in two.
    Sections appear in the order their titles first show up.
    """
    if title not in index:
        index[title] = {'title': title, items_key: []}
        groups.append(index[title])
    return index[title]

def conv_members(table):
    groups, index = [], {}
    for row in table:
        group = get_group(groups, index, row[0], 'members')
        member = row_to_dict(row, ['name', 'email', 'image', 'description', 'links', 'degree', 'year'], 1)
        group['members'].append(member)
    return groups

def get_research_slug(value):
    # The slug becomes both a file name and a URL, so keep it to characters
    # that are safe in each and cannot climb out of the research directory.
    slug = (value or '').strip().strip('/')
    return slug if re.match(r'^[A-Za-z0-9_-]+$', slug) else ''

def get_research_file(slug):
    return os.path.join(config.RESEARCH_PATH, '%s.md' % slug)

def load_research_content(slug):
    with open(get_research_file(slug), 'r') as f:
        return f.read()

def conv_research(table):
    groups, index = [], {}
    for row in table:
        group = get_group(groups, index, row[0], 'rows')
        item = row_to_dict(row, ['title', 'authors', 'booktitle', 'links', 'tags', 'path'], 1)
        if 'tags' in item:
            item['tags'] = [tag.strip() for tag in (item['tags'] or '').split(',') if tag]
        item['path'] = get_research_slug(item['path'])
        # Only papers with a write-up on disk get a page of their own.
        item['has_page'] = bool(item['path']) and os.path.exists(get_research_file(item['path']))
        group['rows'].append(item)
    return groups

def conv_tags(table):
    tags = {}
    for row in table:
        tags[row[0]] = {
            'title': row[1],
            'tag': row[2],
            'color': row[3],
        }
    return tags

def conv_links(table):
    groups, index = [], {}
    for row in table:
        group = get_group(groups, index, row[0], 'rows')
        item = row_to_dict(row, ['title', 'full_title', 'url', 'query', 'call_month', 'event_month'], 1)
        group['rows'].append(item)
    return groups

def conv_personal_website(table):
    items = {}
    for row in table:
        if not row or not row[0].strip():
            continue
        items[row[0]] = row[1] if len(row) > 1 else ''
    return items

def conv_personal_contents(table):
    contents = []
    for row in table:
        if len(row) < 2 or not row[0].strip():
            continue
        contents.append({'title': row[0], 'content': row[1]})
    return contents

def load_personal(table):
    websites = []
    for row in table:
        pathname = row[0].strip()
        url = row[1].strip()
        if not pathname or not url:
            continue
        websites.append({'path': pathname, 'url': url})
    
    for website in websites:
        data_url = website['url']
        doc_id = get_doc_id(data_url)
        tables = load_ranges(doc_id, PERSONAL_RANGES)
        website['website'] = conv_personal_website(tables[0])
        website['contents'] = conv_personal_contents(tables[1])

    return websites

def conv_news(table):
    items = []
    for row in table:
        item = row_to_dict(row, ['url', 'title', 'description', 'image', 'date'])
        url = item['url'].strip()
        if not url:
            continue
        # Values written in the sheet win, so a link whose preview is missing or
        # wrong can be fixed by hand without changing any code. A row that fills
        # in everything needs no request at all.
        filled_in = all(item[key].strip() for key in ('title', 'description', 'image'))
        preview = {} if filled_in else (opengraph.get_preview(url) or {})
        image = item['image'].strip() or preview.get('image') or ''
        if image.startswith('http'):
            # Keep a copy so the card survives the publisher moving the file.
            # A thumbnail we could not fetch is dropped rather than linked, so
            # the template falls back to the default image instead of rendering
            # a broken one.
            image = opengraph.download_image(
                image, config.NEWS_IMAGE_PATH, config.NEWS_IMAGE_URL_BASE) or ''
        items.append({
            'url': url,
            'title': item['title'].strip() or preview.get('title') or url,
            'description': item['description'].strip() or preview.get('description') or '',
            'image': image,
            'source': preview.get('site_name') or urllib.parse.urlparse(url).netloc,
            'date': item['date'].strip(),
        })
    return items

def load_news(doc_id):
    tables = load_optional_ranges(doc_id, NEWS_RANGES)
    if tables is None:
        return []
    return conv_news(tables[0])

def conv_pages(table):
    pages = []
    for row in table:
        if len(row) < 3 or not row[0].strip():
            continue
        pathname = row[0].strip()
        title = row[1].strip()
        content = row[2]
        if not pathname or not title or not content:
            continue
        pages.append({'path': pathname, 'title': title, 'content': content})
    return pages

def conv_redirects(table):
    redirects = []
    for row in table:
        if len(row) < 2 or not row[0].strip():
            continue
        pathname = row[0].strip()
        url = row[1].strip()
        if not pathname or not url:
            continue
        redirects.append({'path': pathname, 'url': url})
    return redirects

def load_data():
    data_url = config.DATA_URL
    doc_id = get_doc_id(data_url)
    tables = load_ranges(doc_id, RANGES)
    return {
        'website': conv_website(tables[0]),
        'announcements': conv_announcements(tables[1]),
        'members': conv_members(tables[2]),
        'research': conv_research(tables[3]),
        'tags': conv_tags(tables[4]),
        'links': conv_links(tables[5]),
        'pages': conv_pages(tables[6]),
        'redirects': conv_redirects(tables[7]),
        'personal': load_personal(tables[8]),
        'news': load_news(doc_id),
    }

