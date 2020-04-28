from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from problems.models import Problem
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
    return statement

def download_problem(id):
    url = archive_url + "/?q=node/" + id
    print(url)
    r = requests.get(url, cookies=js_cookie)
    soup = BeautifulSoup(r.text, 'html.parser')

    content = soup.find(id='node-' + id)
    problem = ""
    for line in traverse_problem(content):
        problem += str(line)

    parsed = format_statement(problem)

    problem = Problem(statement = parsed[0], solution = parsed[1]);
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

