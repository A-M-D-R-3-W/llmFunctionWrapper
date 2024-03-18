import pathlib
import setuptools

setuptools.setup(
    name="llmFunctionWrapper",
    version="1.0.0",
    description="A simplified function wrapper for OpenAI and LiteLLM API calls.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/A-M-D-R-3-W/llmFunctionWrapper/",
    author="A-M-D-R-3-W",
    author_email="AMDR3W@proton.me",
    license="MIT",
    project_urls={
        "Documentation": "https://github.com/A-M-D-R-3-W/llmFunctionWrapper/blob/main/README.md",
        "Source": "https://github.com/A-M-D-R-3-W/llmFunctionWrapper/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    packages=setuptools.find_packages(),
    include_package_data=True,
)