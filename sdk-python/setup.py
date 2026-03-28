from setuptools import setup, find_packages

setup(
    name="promptthread",
    version="0.1.0",
    description="Git for prompts. Version control and performance tracking for AI prompts.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Eugene Mawuli",
    url="https://github.com/eugene001dayne/prompt-thread",
    py_modules=["promptthread"],
    install_requires=["httpx"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)