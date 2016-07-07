from setuptools import setup, find_packages

setup(name='missmatch',
      version="0.0.1",
      packages=find_packages(),
      description='Miss Match is a HTML Parser designed to identify mismatched HTML tags.',
      url='https://github.com/DistilledLtd/missmatch',
      author='Distilled Ltd',
      author_email='randd@distilled.net',
      install_requires=['requests']
      )
