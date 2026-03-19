import os
from setuptools import setup, find_packages

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cbridge-agent",
    version="0.1.12",
    description="The All-in-One Local Memory Bridge for AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="whyischen",
    author_email="whyischen@gmail.com",
    packages=find_packages(),
    py_modules=["cbridge"],
    install_requires=[
        "markitdown",
        "watchdog",
        "chromadb",
        "mcp",
        "pydantic",
        "PyYAML",
        "click",
        "tqdm",
        "rich",
        "fastapi",
        "uvicorn"
    ],
    entry_points={
        "console_scripts": [
            "cbridge=cbridge:cli",
        ],
    },
)
