####################################
######### NUMPY and PANDAS #########
####################################
Numpy
NumPy is the fundamental package for scientific computing with Python. It contains among other things:
⦁	a powerful N-dimensional array object
⦁	sophisticated (broadcasting) functions
⦁	tools for integrating C/C++ and Fortran code
⦁	useful linear algebra, Fourier transform, and random number capabilities
Documentation https://numpy.org/doc/
⦁	In 2008, pandas development began at AQR Capital Management. By the end of 2009 it had been open sourced, and is actively supported today by a community of like-minded individuals around the world who contribute their valuable time and energy to help make open source pandas possible. Thank you to all of our contributors.
⦁	pandas aims to be the fundamental high-level building block for doing practical, real world data analysis in Python. Additionally, it has the broader goal of becoming the most powerful and flexible open source data analysis / manipulation tool available in any language.
⦁	Tools for reading and writing data between in-memory data structures and different formats: CSV and text files, Microsoft Excel, SQL databases, and the fast HDF5 format;
⦁	Intelligent data alignment and integrated handling of missing data: gain automatic label-based alignment in computations and easily manipulate messy data into an orderly form;
⦁	Intelligent label-based slicing, fancy indexing, and subsetting of large data sets;
⦁	Highly optimized for performance, with critical code paths written in Cython or C.
⦁	Python with pandas is in use in a wide variety of academic and commercial domains, including Finance, Neuroscience, Economics, Statistics, Advertising, Web Analytics, and more.
Documentation: https://pandas.pydata.org/docs/

##################################
######### VISUALIZATION ##########
##################################
Matplotlib
⦁	Matplotlib is a Sponsored Project of NumFOCUS, a 501(c)(3) nonprofit charity in the United States
⦁	Matplotlib is the brainchild of John Hunter (1968-2012), who, along with its many contributors, have put an immeasurable amount of time and effort into producing a piece of software utilized by thousands of scientists worldwide.
⦁	Documentation link: https://matplotlib.org/contents.html
⦁	Some of this walkthrough is adapted from here this matplotlib tutorial
⦁	https://matplotlib.org/3.2.1/tutorials/introductory/lifecycle.html
⦁	A large gallery showcasing various types of plots matplotlib can create.
⦁	http://matplotlib.org/gallery.html
⦁	A great set of cheatsheets and tips compiled into .jpg files
⦁	https://github.com/matplotlib/cheatsheets

MatPlot Object-Oriented Methods
⦁	Matplotlib has two interfaces. The first is an object-oriented (OO) interface. In this case, we utilize an instance of axes.Axes in order to render visualizations on an instance of figure.Figure. The second is the pyplot interface, which you have seen above.
⦁	Important Items to Remember:
⦁	The Figure is the final image that may contain 1 or more Axes.
⦁	The Axes represent an individual plot (don't confuse this with the word "axis", which refers to the x/y axis of a plot).
Legends
⦁	The label="" keyword argument allows you to create legend labels when plots or other objects are added to the figure, and then using the legend method without arguments to add the legend to the figure.
⦁	The legend function takes an optional keyword argument loc that can be used to specify where in the figure the legend is to be drawn. The allowed values of loc are numerical codes for the various places the legend can be drawn. See the documentation page for details.
⦁	Most common loc values:
⦁	ax.legend(loc=1) - upper right corner
⦁	ax.legend(loc=2) - upper left corner
⦁	ax.legend(loc=3) - lower left corner
⦁	ax.legend(loc=4) - lower right corner
##################################
######### DATA GATHERING #########
##################################
Data Gathering
This lecture highlights the immense capabilities python has when it comes to gathering data and automating the processes. By the end of this exercise you will understand the basics of web-scraping, web-crawling, and API data-gathering.
API Data Gathering
⦁	API - Application Programming Interface
⦁	Many places offer up data to those who are interested. Certain organizations even allow you to utilize python to connect to their code base and download their data.
⦁	This section will describe three options you have when you need to gather data.
⦁	This is not an exhaustive list of data options, but some of these options are to be used throughout the semester.

yfinance
⦁	yfinance was created solely to replace PDR's lacking Yahoo! data access.
⦁	This is the most up to date Yahoo! Finance data API and the most popular at the moment.
⦁	PyPi link: https://pypi.org/project/yfinance/
Tiingo
⦁	https://www.tiingo.com/
⦁	Free individual usage with account setup
⦁	Users can see usage levels -- > https://api.tiingo.com/account/api/usage
⦁	500 "unique" symbols per month.
⦁	500 requests per hour
⦁	20,000 requests per day
⦁	END OF DAY ONLY. No intra-day values.
⦁	Current session values cannot be gathered.