import setuptools

from src.version import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fce-ipmi",
    version=VERSION,
    author="Przemyslaw Hausman",
    description="Wrapper for various IPMI-related utilities",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phausman/fce-ipmi",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    py_modules=["app", "main", "messages", "utils", "version"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires=">=3.6.9",
    entry_points={
        "console_scripts": [
            "fce-ipmi=main:cli",
        ],
    },
    setup_requires=["wheel"],
    install_requires=["click>=7.1.2", "PyYAML>=5.3.1", "colorlog>=4.6.2"],
)
