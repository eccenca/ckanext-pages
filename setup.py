from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-pages',
	version=version,
	description='Extended CMS extension for ckan',
	long_description='',
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Henri Knochenhauer',
	author_email='henri.knochenhauer@eccenca.com',
	url='http://eccenca.com',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.pages'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
        pages=ckanext.pages.plugin:PagesPlugin

	""",
)
