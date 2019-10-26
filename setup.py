from setuptools import setup, find_packages
setup(
    name="Dunder Bands: The Rock Engine",
    version="1.5",
    packages=find_packages(),
    scripts=['run.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },

    # metadata to display on PyPI
    author="Evan T. Deubner",
    author_email="withinmyself@gmail.com",
    description="My passion project/portfolio",
    keywords="find music dunder band rock engine",
    url="https://dunderbands.herokuapp.com/search/",   # project home page, if any
    project_urls={
        "withinmyself@github.com"
    },
    

    # could also include long_description, download_url, etc.
)