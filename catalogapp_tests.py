# some tests go here
import autopep8
import application
import unittest
import init_database


def clean(fname):
    file_string = open(fname, 'r').read()
    return autopep8.fix_code(file_string)


class myTestCase(unittest.TestCase):

    def testDuplicateName(self):
        self.assertTrue(application.check_duplicate("Soccer"))

    def testDecoratorWrapsCorrectly(self):
        exp = """Inside __call__()
func1 key1 key2
After self.f(*args)
"""
        self.assertEquals(func1(), exp)


class decorator(object):

    def __init__(self, f):
        """
        If there are no decorator arguments, the function
        to be decorated is passed to the constructor.
        """
        self.f = f

    def __call__(self, *args):
        """
        The __call__ method is not called until the
        decorated function is called.
        """
        s = "Inside __call__()\n"
        s += self.f(*args) + "\n"
        s += "After self.f(*args)" + "\n"
        return s


@decorator
def func1(key1="key1", key2="key2"):
    return "func1 " + key1 + " " + key2


if __name__ == '__main__':
    # Uncomment to print out fixed python code
    # print clean('init_database.py')
    # print clean('database_setup.py')+'\n'
    # print clean('application.py')
    # print clean('catalogapp_tests.py')

    # run main tests
    unittest.main()
