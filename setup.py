from setuptools import setup, find_packages

setup(
    name="project_name",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "jinja2",
    ],
    entry_points={
        'console_scripts': [
            'project_name=main:main',
        ],
    },
)

