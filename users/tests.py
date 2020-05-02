from django.test import TestCase, Client
from django.contrib.auth.models import User

from problems.models import Problem
from folder.models import Folder, ProblemPlace
from tags.models import Tag
from folder.tests import add_sample_folders
from tags.tests import add_sample_tags
from problems.tests import add_sample_problems

def add_dummy_users():
    def add_user(username):
        user = User.objects.create(username=username)
        user.save()
        return user
    staff = add_user('staff')
    staff.is_staff = True
    student1 = add_user('student1')
    student2 = add_user('student2')
    tag1 = Tag(type_id=7, name="tag student")
    tag1.save()
    tag2 = Tag(type_id=7, name="tag nobody")
    tag2.save()
    student1.tag_set.add(tag1)
    student2.tag_set.add(tag2)
    staff.tag_set.add(tag2)
    for u in [staff, student1, student2]:
        u.save()

class UserPermissions(TestCase):
    def setUp(self):
        add_sample_folders()
        add_sample_tags()
        add_sample_problems()
        add_dummy_users()
        self.assertEqual(len(User.objects.all()), 3)

        self.user_staff, self.user_student1, self.user_student2 = [User.objects.get(username=x) for x in ['staff', 'student1', 'student2']]

        self.client_staff = Client()
        self.client_staff.force_login(self.user_staff)
        self.client_student1 = Client()
        self.client_student1.force_login(self.user_student1)
        self.client_student2 = Client()
        self.client_student2.force_login(self.user_student2)

        self.mid_folder = Folder.objects.get(pretty_name='Wielomiany')
        self.mid_folder.tag_set.add(Tag.objects.get(name="tag student"))
        self.mid_folder.save()

        self.paths = {Folder.objects.get(parent=None): 'all'}
        def dfs(prefix, f):
            self.paths[f] = prefix
            for son in Folder.objects.filter(parent=f).all():
                dfs(prefix + '/' + son.folder_name, son)
        for son in Folder.objects.filter(parent=Folder.objects.get(parent=None)).all():
            dfs(son.folder_name, son)
        self.assertEqual(len(self.paths), Folder.objects.count())

    def test_folder_access(self):
        for f in Folder.objects.all():
            url = '/contest/' + self.paths[f]
            response = self.client_staff.get(url)
            self.assertEqual(response.status_code, 200)
            response = self.client_student2.get(url)
            self.assertEqual(response.status_code, 200 if f.parent == None else 403)

        access_list = [self.mid_folder, self.mid_folder.parent, Folder.objects.get(parent=None)]
        for son in Folder.objects.filter(parent=self.mid_folder).all():
            access_list.append(son)
        for f in Folder.objects.all():
            url = '/contest/' + self.paths[f]
            response = self.client_student1.get(url)
            self.assertEqual(response.status_code, 200 if f in access_list else 403)

    def check(self, url, code_list):
        def assert_response(client, code):
            response = client.get(url)
            self.assertEqual(response.status_code, code)
        clients = [self.client_staff, self.client_student1, self.client_student2]
        for i in range(len(clients)):
            assert_response(clients[i], code_list[i])

    def test_staff_only(self):
        self.check('/users/', [200, 403, 403])

    def test_userpage_access(self):
        self.check('/users/2', [200, 200, 403])

    def test_problem_access(self):
        url = '/problems/1/'
        self.check(url, [200, 403, 403])
        son = Folder.objects.filter(parent=self.mid_folder).all()[0]
        problem = Problem.objects.get(id=1)
        ProblemPlace(problem=problem, folder=son, place=1).save()
        self.check(url, [200, 200, 403])

