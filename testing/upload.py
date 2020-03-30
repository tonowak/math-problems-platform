from requests import Request, Session
import sys
import json

global ses
ses = Session()
host = "http://127.0.0.1:8000"

def add_problem(statement):
    #print(ses.cookies)
    csrftoken = ses.cookies.get_dict()['csrftoken']
    url = host + '/problems/add/'
    req = Request('POST', url, data = {"statement" : statement, 'csrfmiddlewaretoken': csrftoken})
    resp = ses.send(ses.prepare_request(req))

def get_statements():
    ret = []
    with open('file.tex') as input_file:
        for line in input_file:
            line = line.replace('\n', '')
            ret.append(line)
            print(line)
    return ret

req = Request('GET', host + "/problems/add/")
ses.send(ses.prepare_request(req))

statements = get_statements()
for s in statements:
    add_problem(s)
