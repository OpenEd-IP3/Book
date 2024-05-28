from setuptools import setup, find_packages

setup(
    name='sphinx_thebe_pyodide',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['sphinx'],
    entry_points={
        'sphinx.html_themes': [
            'sphinx_thebe_pyodide = sphinx_thebe_pyodide',
        ],
        'sphinx.extensions': [
            'sphinx_thebe_pyodide = sphinx_thebe_pyodide',
        ],
    },
)

