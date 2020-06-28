from setuptools import setup, find_packages

setup(
    name="simple_env_config",
    url="https://github.com/freininghaus/simple_env_config",
    description="Make use of environment variables for configuration easy",
    keywords="env environment config decorator",
    version="0.1",
    license="MIT",
    author="Frank Reininghaus",
    author_email="frank78ac@googlemail.com",
    packages=find_packages(exclude=["tests"]),
)