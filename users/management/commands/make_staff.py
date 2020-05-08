from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise CommandError('Boolean value expected.')

class Command(BaseCommand):
    help = 'Manages staff/teacher accounts'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--nick', type=str, help='Sets target nickname')
        parser.add_argument('-a', '--all', action='store_true', help='Sets everyone as target')
        parser.add_argument('-w', '--value', type=str2bool, nargs='?', const=True, 
                default=True, help='Sets is_staff to given value')

    def handle(self, *args, **kwargs):
        sum = bool(kwargs['nick']) + bool(kwargs['all'])
        if sum == 0:
            print("Use --help")
        if sum != 1:
            raise CommandError('Exactly one of --nick or --all must be set')

        if kwargs['nick']:
            try:
                user = User.objects.get(username=kwargs['nick'])
            except:
                raise CommandError('There is no user with given nick')
            user.is_staff = kwargs['value']
            user.save()
        else:
            for user in User.objects.all():
                user.is_staff = kwargs['value']
                user.save()
