import sys
from distutils.core import setup


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


if sys.version_info < (3, 6):
    msg = 'run-batch works with Python 3.6 and later.\nDetected %s.' % str(sys.version)
    sys.exit(msg)


lib_version = get_version(filename='brun/__init__.py')

setup(
    name = 'brun',
    packages = [
        'brun',
        'brun.generators',
        'brun.combinators',
    ],
    version = lib_version,
    license='MIT',
    description = 'Utility used to run parameterized shell commands',
    author = 'Andrea F. Daniele',
    author_email = 'afdaniele@ttic.edu',
    url = 'https://github.com/afdaniele/',
    download_url = f'https://github.com/afdaniele/run-batch/tarball/{lib_version}',
    zip_safe=False,
    include_package_data=True,
    keywords = ['batch', 'parameterized', 'commands', 'shell'],
    install_requires=[],
    scripts=['brun/brun'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
