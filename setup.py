from setuptools import setup, find_packages

setup(
    name="cbridge-agent",
    version="0.1.0",
    description="The All-in-One Local Memory Bridge for AI Agents",
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
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "cbridge=cbridge:cli",
        ],
    },
)
