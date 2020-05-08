from django.test import TestCase
import os
from random import seed
from random import randint

from tiled_math.settings import BASE_DIR
from problems.models import Problem
from folder.models import Folder, ProblemPlace

def add_sample_problems():
    path = os.path.join(BASE_DIR, 'problems/files/sample_statements.tex')
    with open(path) as input_file:
        added_problems = 0
        for line in input_file:
            line = line.replace('\n', '')
            problem = Problem(statement=line)
            problem.save()
            added_problems += 1

def add_problems_to_folders_randomly():
    problems = Problem.objects.all()
    for folder in Folder.objects.all():
        if not Folder.objects.filter(parent=folder):
            for i in range(10):
                index = randint(0, problems.count() - 1)
                problem = problems[index]
                if not folder.problem_set.filter(id=problem.id).exists():
                    cnt_p_inside_f = folder.problem_set.count()
                    ProblemPlace.objects.create(
                        folder = folder,
                        problem = problem,
                        place = cnt_p_inside_f
                    )
