from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from problems.models import Problem
from tags.models import Tag
from tags.views import tag_types
from bs4 import BeautifulSoup
from PIL import Image

import sys, requests
from files.models import save_image

archive_url = "https://archom.ptm.org.pl"

def get_js_cookie():
    r = requests.get(archive_url)
    cookies = {}
    for script in BeautifulSoup(r.text, 'html.parser').find_all('script'):
        script_string = str(script)
        for line in script_string.splitlines():
            if(line.startswith('createCookie')):
                s = line.split("'")
                cookies[s[1]] = s[3]
    return cookies

js_cookie = get_js_cookie()

def download_image(url):
    print(url)
    r = requests.get(url)
    return save_image(ContentFile(r.content))

def traverse_problem(soup):
    ret = []
    for child in soup.children:
        line = str(child)
        line = line.replace('\n', ' ')
        if child.name is None:
            if not line.isspace():
                ret.append(line)
        elif child.name == 'img':
            alt = str(child.get('alt'))
            if alt.endswith('jpg'):
                location = '/files/' + str(download_image(archive_url + str(child.get('src'))))
                ret.append('![' + alt + '](' + location + ')')
            else:
                ret.append(alt)
                if alt.startswith('$$') and alt.endswith('$$'):
                    ret.append('\n')
                elif alt.startswith('\[') and alt.endswith('\]'):
                    ret.append('\n')
        else:
            name = str(child.name)
            if name.startswith('h') and name != 'hr':
                ret.append('\n')
                for i in range(int(name[1:])):
                    ret.append('#')
                ret.append(' ')
            for r in traverse_problem(child):
                ret.append(r)
            if name.startswith('h'):
                ret.append('\n')
            if child.name == 'br':
                ret.append(' ')
            if child.name == 'p':
                ret.append('\n\n')
    return ret

def format_statement(statement):
    statement = statement.replace('<br />', ' ')
    statement = statement.replace('\[ \n', '\[ ')
    statement = statement.replace('\n\]', '\]')
    statement = statement.split('‹')[0]
    statement = statement.split('## Rozwiązanie')
    if len(statement) == 1:
        statement.append('')
    return statement

def fetch_statement(soup, content_id):
    content = soup.find(id=content_id)
    statement = ""
    for line in traverse_problem(content):
        statement += str(line)
    return format_statement(statement)

def fetch_tags(soup):
    title = str(soup.find('h1', {'class': 'title'}).text) 
    # XLIII OM - III - Zadanie 4
    s = title.split(' ')
    return [s[0] + ' ' + s[1], s[3] + ' etap']

def download_problem(id):
    url = archive_url + "/?q=node/" + id
    print(url)
    r = requests.get(url, cookies=js_cookie)
    soup = BeautifulSoup(r.text, 'html.parser')

    problem_data = fetch_statement(soup, 'node-' + id)
    statement = problem_data[0]
    solution = problem_data[1]

    problem = Problem(statement=statement, solution=solution)
    problem.save()

    for tag_name in fetch_tags(soup):
        if Tag.objects.filter(name=tag_name):
            tag = Tag.objects.get(name=tag_name)
        else:
            tag = Tag(name=tag_name, type_id=tag_types.index('Źródło'))
            tag.save()
        
        problem.tag_set.add(tag)

    problem.save()

def download_archom():
    r = requests.get(archive_url, cookies=js_cookie)
    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        title = link.get('title')
        s = str(title).split(' ')
        if len(s) >= 2 and s[-2] == 'Zadanie':
            download_problem(href.split('/')[-1])

class Command(BaseCommand):
    help = 'Downloads problems from OM Archive'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--problem', type=int, help='Download a single problem')

    def handle(self, *args, **kwargs):
        problem = kwargs['problem']
        if problem:
            download_problem(str(problem))
        else:
            download_archom()

