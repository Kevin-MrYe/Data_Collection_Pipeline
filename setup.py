from setuptools import setup,find_packages

setup(name='pipelines-metrics',
       version='1.0',
       packages=find_packages(),
       install_requires=[
           'selenium',
           'tqdm',
           'pandas',
           'sqlalchemy',
           'python-dotenv',
           'boto3',
           'psycopg2',
        ])