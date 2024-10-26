from os.path import abspath, dirname, join

root_dir = abspath(dirname(dirname(__file__)))
my_path = lambda path: join(root_dir, path)
