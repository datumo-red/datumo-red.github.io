from .renderer import *

class Page:
    def __init__(self, path, renderer):
        self.path = path
        self.renderer = renderer

def get_safe_path(pathname):
    if pathname.endswith('.html'):
        return pathname
    else:
        return '%s/index.html' % pathname

def get_research_items(data):
    return [
        item
        for group in data['research']
        for item in group['rows']
        if item['has_page']
    ]

def get_pages(data):
    return [
        Page('index.html', render_index),
        Page('members.html', render_members),
        Page('research.html', render_research),
        Page('topics.html', render_topics),
        Page('news.html', render_news),
        Page('contact.html', render_contact),
    ] + [
        Page(
            get_safe_path('research/%s' % item['path']),
            lambda x, item=item: render_research_detail(x, item),
        ) for item in get_research_items(data)
    ] + [
        Page(
            get_safe_path(page['path']),
            lambda x, page=page: render_page(x, page),
        ) for page in data['pages']
    ] + [
        Page(
            get_safe_path(redirect['path']),
            lambda x, redirect=redirect: render_redirect(x, redirect),
        ) for redirect in data['redirects']
    ] + [
        Page(
            get_safe_path(website['path']),
            lambda x, website=website: render_personal_website(x, website),
        ) for website in data['personal']
    ]