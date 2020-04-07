from requests import Request, Session
import sys
import json

global ses
ses = Session()
# first two lines were taken by capturing Set-Cookie response header to login in
# third cookie was taken by copying a form csrf_token
csrftoken = 'YcRDFxCPjHDNnoLYksFMt8RsfVAQ7H9H7SwiyfSqjEGe7BzkqjB8x2xd9uBqs3JZ'
sessionid = 'kb5x1miq3rmje844w848trfqkx3nlbj6'
csrfmiddlewaretoken = 'IBaYKpoXNdvGLwIFU4vair3axctZP1svRhPDD7EyNay7vJw10VrwmlJVrLuzan2N'
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
    with open('statements.tex') as input_file:
        for line in input_file:
            line = line.replace('\n', '')
            ret.append(line)
            print(line)
    return ret

statements = get_statements()
for s in statements:
    add_problem(s)
