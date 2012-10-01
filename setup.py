""" Standard setup.py for easy install

For development do
# python setup.py develop 
for install and
# python setup.py develop -u 
for uninstall

"""

from setuptools import setup

version = 0.8.2

setup(name='swarm',
      author='DmitriKo',
      author_email='dmitrikozhevin@gmail.com',
      version=version,
      packages=['swarm'],
      install_requires=['tornado', 'pika'])

