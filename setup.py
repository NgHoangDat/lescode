import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


__VERSION__ = "0.2.11.7"


setuptools.setup(
    name="lescode",
    packages=setuptools.find_packages(),
    version=__VERSION__,
    author="nghoangdat",
    author_email="18.hoang.dat.12@gmail.com",
    description="quiver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NgHoangDat/lescode.git",
    download_url=f"https://github.com/NgHoangDat/lescode/archive/v{__VERSION__}.tar.gz",
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