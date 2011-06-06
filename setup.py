from distutils.core import setup
setup(
    name = 'charlie_test_manager',
    version = '0.1',
    packages = ['charlie'],
    author = 'AGRaud',
    author_email = 'augiraud@gmail.com',
    description = 'Software Testing Manager',
    url = 'https://github.com/nire/Charlie',
    include_package_data = True,
    depends = 'django suds memcached python-memcached django-nose ez_setup virtualenv simplejson'
)
