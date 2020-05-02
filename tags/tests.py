from django.test import TestCase
import os
from random import seed
from random import randint

from tiled_math.settings import BASE_DIR
from tags.models import Tag
from problems.models import Problem
from problems.views import process_tags

def add_sample_tags():
    path = os.path.join(BASE_DIR, 'tags/files/sample_tags.txt')
    with open(path) as input_file:
        added_tags = 0
        cur_category = -1
        for line in input_file:
            line = line.replace('\n', '')
            if len(line) and line[0] == '#':
                cur_category += 1
            else:
                tag = Tag(name=line, type_id=cur_category)
                tag.save()
                added_tags += 1

def add_tags_to_problems_randomly():
    seed(2137)
    tags = Tag.objects.exclude(type_id=7).filter(attachable=True)
    for problem in Problem.objects.all():
        tag_list = []
        for i in range(3):
            index = randint(0, tags.count() - 1)
            tag_list.append(tags[index].id)
        process_tags(problem, tag_list).save()
