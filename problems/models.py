from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    statement = models.TextField(default='')
    solution  = models.TextField(default='')
    hints     = models.TextField(default='')
    answer    = models.TextField(default='')
    staff_comment    = models.TextField(default='')
    solution_comment = models.TextField(default='')

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='problems_created')

    def __str__(self):
        return self.statement[:20] + "..."

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

