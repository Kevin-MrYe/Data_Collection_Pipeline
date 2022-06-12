from setuptools import setup,find_packages

setup(name='pipelines-metrics',
       version='1.0',
       packages=find_packages(),
       install_requires=[
           'selenium',
           'tqdm',
           'pandas',
           'sqlalchemy',
           'pyyaml',
           'boto3',
           'psycopg2-binary',
           'htmltestrunner-rv',
        ])