def add_problems():
    print("Creating problems")
    from problems.models import Problem
    with open('testing/statements.tex') as input_file:
        for line in input_file:
            line = line.replace('\n', '')
            problem = Problem(statement=line)
            problem.save()

def add_tags():
    print("Creating tags")
    from tags.models import Tag
    with open('testing/tags.txt') as input_file:
        cur_category = -1
        for line in input_file:
            line = line.replace('\n', '')
            if len(line) and line[0] == '#':
                cur_category += 1
            else:
                tag = Tag(name=line, type_id=cur_category)
                tag.save()

def add_tags_to_problems():
    print("Adding tags to problems")
    from problems.models import Problem
    from problems.views import process_tags
    from tags.models import Tag
    from random import seed
    from random import randint
    seed(2137)
    
    tags = Tag.objects.exclude(type_id=7).filter(attachable=True)
    for problem in Problem.objects.all():
        tag_list = []
        for i in range(3):
            index = randint(0, tags.count() - 1)
            tag_list.append(tags[index].id)
        process_tags(problem, tag_list).save()

def add_folders():
    print("Creating contests")
    from folder.models import Folder
    from folder.views import convert_pretty_to_folder_name

    folder_stack = [Folder.objects.get(parent=None)]
    with open('testing/contests.txt') as input_file:
        for line in input_file:
            line = line.replace('\n', '')
            name = line.lstrip(' ')
            if name == '':
                continue

            leading_spaces = len(line) - len(name)
            while leading_spaces != len(folder_stack) - 1:
                folder_stack.pop()

            formatted_name = convert_pretty_to_folder_name(name)
            folder = Folder(parent=folder_stack[-1], pretty_name=name, folder_name=formatted_name, created_by=None)
            folder.save()
            folder_stack.append(folder)

def add_problems_to_folders():
    print("Adding problems to contests")
    from problems.models import Problem
    from folder.models import Folder, ProblemPlace
    from random import seed
    from random import randint

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


add_problems()
add_tags()
add_tags_to_problems()
add_folders()
add_problems_to_folders()
