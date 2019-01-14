from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='getrealty',
      version='1.1',
      description='''python engine for property information from appraisal
      sites and storing in sqlite db''',
      url='http://github.com/jfrerich/getrealty',
      author='Jason Frerich',
      author_email='',
      license='MIT',
      packages=['getrealty'],
      zip_safe=False)

