import re
import os

from setuptools import setup, find_packages

def package_files(directory_list):
    paths = []
    for directory in directory_list:
        for (path, directories, filenames) in os.walk(directory):
            for filename in filenames:
                paths.append(os.path.join('..', path, filename))
    return paths

project_package = 'farmsync'
project_info = {}

static_dir = os.path.join(project_package, "static")
templates_dir = os.path.join(project_package, "templates")
imgs_dir = os.path.join(project_package, "images")
extra_files = package_files([static_dir, templates_dir, imgs_dir])

classifiers = """
Development Status :: 1 - Planning
Intended Audience :: Science/Research
Topic :: Software Development
License :: Other/Proprietary License
Programming Language :: Python :: 3.6
"""

with open('{}/__init__.py'.format(project_package), 'r') as f:
    for _ in f.read().splitlines():
        b = re.search(r'^__(.*)__\s*=\s*[\'"]([^\'"]*)[\'"]', _)
        if b:
            project_info[b.group(1)] = b.group(2)

setup(
    name="farmsync",
    version=project_info['version'],
    author=project_info['author'],
    author_email=project_info['author_email'],
    url=project_info['url'],
    license=project_info['license'],
    description=project_info['description'],
    long_description="",
    packages=find_packages(),
    include_package_data=True,
    package_data={'farmsync': extra_files},
    keywords='cli',
    classifiers=classifiers.splitlines()[1:]
)
