from setuptools import setup

setup(
	name = "mcsearch",
	version = "0.1.0",    
	description = "A package allowing for searching the data in minecraft region files",
	url = "https://github.com/CapnOdin/mcsearch",
	author = "Cap'n Odin",
	author_email = "capnodin@gmail.com",
	license = "Unspecified",
	packages = ["mcsearch"],
	install_requires =	[	
							"nbt",
							"anvil-parser",
						],
	long_description_content_type = "text/markdown",

    classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: End Users/Desktop",
		"Topic :: Games/Entertainment",
		"Environment :: Console",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
    ],
)
