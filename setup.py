import setuptools

import osgeo4w_installer

setuptools.setup(
    name=osgeo4w_installer.__name__,
    version=osgeo4w_installer.__version__,
    author=osgeo4w_installer.__author__,
    description='a tool to download osgeo4w distribution and install packages on its python interpreter',
    license='gpl-2.0',
    url='https://github.com/talos-gis/osgeo4w_setup_script',
    packages=['osgeo4w_installer'],
    python_requires='>=3.6.0',
    include_package_data=True,
    data_files=[
        ('', ['README.md', 'LICENSE']),
    ],
)
