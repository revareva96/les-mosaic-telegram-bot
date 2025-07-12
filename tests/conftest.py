import random
import string
from pytest import fixture


@fixture()
def username():
    return '@' + ''.join(random.choices(string.ascii_lowercase, k=5))
