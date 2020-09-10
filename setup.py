
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="harquery-evaneldemachki", # Replace with your own username
    version="0.0.1",
    author="Evan Eldemachki, Justin Chudley",
    author_email="evaneldemachki@gmail.com",
    description="Comprehensive HTTP Profiler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/evaneldemachki/harquery",
    install_requires=[
            'browsermob-proxy==0.8.0',
            'certifi==2020.6.20',
            'chardet==3.0.4',
            'idna==2.10',
            'requests==2.24.0',
            'selenium==3.141.0',
            'urllib3==1.25.10'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)