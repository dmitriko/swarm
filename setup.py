""" Standard setup.py for easy install

For development do
# python setup.py develop 
for install and
# python setup.py develop -u 
for uninstall

"""

from setuptools import setup, find_packages

version = '0.8.4'

setup(name='swarm',
      author='DmitriKo',
      author_email='dmitrikozhevin@gmail.com',
      version=version,
      entry_points = {'console_scripts': [
            'swarm-node = swarm.node_main:main',
            'swarm-manager = swarm.manager_main:main']},
      data_files = [('/etc/init', ['swarm/scripts/swarm-node.conf'])],
      packages=find_packages(),
      install_requires=['tornado', 'pika==0.9.8'])

