from setuptools import setup, find_packages

from version import VERSION


def long_description():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="simple_env_config",
    url="https://github.com/freininghaus/simple_env_config",
    description="Make use of environment variables for configuration easy",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    keywords="env environment config decorator",
    version=VERSION,
    license="MIT",
    author="Frank Reininghaus",
    author_email="frank78ac@googlemail.com",
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
