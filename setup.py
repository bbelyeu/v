from distutils.core import setup

setup(
    name='V',
    version='0.2',
    packages=['v', ],
    license='GNU',
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['v = v:main']
    },
    install_requires=[
    ]
)
