from setuptools import setup, find_packages 

setup(
    name = "east-logging",
    version = "0.0.1",
    keywords =("logging","easy","multi-process"),
    description = "Easy Logging, No painfal to use. :)",
    author = "Yuhui Jin",
    author_email = "jyh_inori@163.com",
    license = "MIT License",
    packages = find_packages(), 
    include_package_data = True, 
    install_requires = ["concurrent-log-handler"]
)
