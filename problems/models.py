from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    statement = models.TextField(default='')
    solution  = models.TextField(default='')
    hints     = models.TextField(default='')
    answer    = models.TextField(default='')
    answer_checker   = models.TextField(default='')
    staff_comment    = models.TextField(default='')
    solution_comment = models.TextField(default='')

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='problems_created')

    def __str__(self):
        return self.statement[:20] + "..."

    def has_answer_checker(self):
        return self.answer_checker != ''

def convert_string_to_number_list(l):
    l = l.split(',')
    if l == ['']:
        l = []
    assert len(l) % 4 == 0
    ret = []
    for i in range(len(l) // 4):
        x = [int(l[4 * i + j]) for j in range(4)]
        a, b, c, d = x[0], x[1], x[2], x[3]
        assert d > 0
        assert c >= 0 and c != 1
        if b == 0 or c == 0:
            assert b == 0 and c == 0
        def nwd(a, b): return nwd(b, a % b) if b else a
        assert nwd(nwd(a, b), d) == 1
        for i in range(2, c):
            assert c % (i * i) != 0
        ret.append(x)
    return ret

def reformat_string_number_list(s):
    l = convert_string_to_number_list(s)
    s = ''
    for x in l:
        for y in x:
            s += str(y) + ','
    return s[:-1]

class SolutionScore(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claiming = models.BooleanField(default=False)
    assigned_score = models.IntegerField(default=-1)

    def get_score(self):
        if self.assigned_score != -1:
            return self.assigned_score
        return int(self.claiming)

# enforcing that there is max one pair (problem, user)
# create if not exists
def get_solutionscore(problem, user):
    if SolutionScore.objects.filter(problem=problem, user=user).exists():
        return SolutionScore.objects.get(problem=problem, user=user)
    ss = SolutionScore(problem=problem, user=user)
    ss.save()
    return ss

def has_solved_task(problem, user):
    if SolutionScore.objects.filter(problem=problem, user=user).exists():
        return bool(SolutionScore.objects.get(problem=problem, user=user).get_score())
    return False

