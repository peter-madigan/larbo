from setuptools import setup

def read_req(filename):
    with open(filename, 'r') as infile:
        return infile.readlines()

setup(
    name='data_logging',
    py_modules=['data_logging'],
    install_requires=read_req('requirements.txt')
)
