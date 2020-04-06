from requests import Request, Session
import sys
import json

global ses
ses = Session()
# first two lines were taken by capturing Set-Cookie response header to login in
# third cookie was taken by copying a form csrf_token
csrftoken = 'rzf0NH2Qw4ilZcwm13ovc1yUsO2IkGbGPSHaMT28g7PW3k3gfQKFLkl1q23F1Ufd'
sessionid = 'oir7qgn8vinvxl6ol4speo6vzj1g2tg7'
csrfmiddlewaretoken = 'tDUZfLZW1LiJsjuSh2LpsdVh0YjolzwRRWm9eXZeLOPkwr1MvP7z1wIoYckl2NAo'
host = "http://127.0.0.1:8000"

def add_problem(statement):
    #print(ses.cookies)
    url = host + '/problems/add'
    req = Request('POST', url, data = {
        "statement" : statement,
        'answer': '',
        'hints': '',
        'solution': '',
        'csrfmiddlewaretoken': csrfmiddlewaretoken,
    }, cookies = {
        'csrftoken': csrftoken,
        'sessionid': sessionid,
    })
    resp = ses.send(ses.prepare_request(req))

def get_statements():
    ret = []
    with open('file.tex') as input_file:
        for line in input_file:
            line = line.replace('\n', '')
            ret.append(line)
            print(line)
    return ret

statements = get_statements()
for s in statements:
    add_problem(s)
