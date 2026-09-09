from setuptools import setup
from glob import glob
import os

package_name = 'practise_description'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yu Shen',
    maintainer_email='your@email.com',
    description='Description of my_arm',
    license='MIT',
   entry_points={
    'console_scripts': [
        'ex_practise_pick_and_place = practise_description.ex_practise_pick_and_place:main',
    ],
},
)
