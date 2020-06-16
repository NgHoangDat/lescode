import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quiver",
    version="0.1.0",
    author="nghoangdat",
    author_email="18.hoang.dat.12@gmail.com",
    description="quiver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NgHoangDat/quiver.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'dataclasses; python_version=="3.6"',
        'msgpack',
        'python-dateutil',
        'pyyaml',
        'toolz'
    ]
)