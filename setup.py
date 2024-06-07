from setuptools import setup, find_packages

setup(
    name="aci2apstra",
    version="0.1.0",
    author="Adam Jarvis",
    author_email="ajarvis@juniper.net",
    description="A tool for converting an ACI APIC configuration to an Apstra configuration, outputted as a Terraform configuration.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/iamjarvs/Conversion_ACItoAPSTRA",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jinja2",
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'aci_to_apstra=src.main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)