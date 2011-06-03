import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = 'charlie_test_manager',
    version = '0.1',
    packages = find_packages(),
    author = 'AGRaud',
    author_email = 'augiraud@gmail.com',
    description = 'Software Testing Manager',
    url = 'https://github.com/nire/Charlie',
    include_package_data = True
)
