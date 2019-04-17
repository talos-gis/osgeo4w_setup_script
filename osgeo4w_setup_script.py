""" osgeo4w setup automation script.

This script does the following:
    0. downloads the osgeo4w setup file.
    1. runs the setup with given packages list.
    2. makes an osgeo4w py3 batch file.
    3. installs additional python3 packages using pip.
    4. works for 32bit and/or 64bit setups

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = "Idan Miara, Yael Abitbol"
__copyright__ = "Copyright 2018, The Authors"
__credits__ = ["Idan Miara", "Yael Abitbol"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Idan Miara"
__email__ = "idan@miara.com"
__status__ = "Production"


import os
import subprocess
import urllib.request
from shutil import copyfile


def osgeo4w_setup_run(setup_exe_path, site, osgeo4w_root, local_package_dir, osgeo4w_packages):
    osgeo4w_install_cmd = ' '.join(
        [setup_exe_path,
         '--quiet-mode --autoaccept --advanced',
         '--site', site,
         '--root', '"' + osgeo4w_root + '"',
         '--local-package-dir', '"' + local_package_dir + '"',
         *['--packages {}'.format(p) for p in osgeo4w_packages]])
    print(osgeo4w_install_cmd)
    return subprocess.call(osgeo4w_install_cmd, shell=True)


def osgeo4w_py3_batchfile_create(OSGeobat, OSGeo4W_root):
    new_batch_filename = r"OSGeo4W3.bat"
    new_batch_filepath = os.path.join(OSGeo4W_root, new_batch_filename)

    o4w_line = r'call "%~dp0\bin\o4w_env.bat"'
    qt5_line = r'call "%~dp0\bin\qt5_env.bat"'
    py3_line = r'call "%~dp0\bin\py3_env.bat"'

    with open(new_batch_filepath, 'w+') as osgeo4w_py3_batch_file:
        for line in open(OSGeobat, 'r'):
            osgeo4w_py3_batch_file.write(line)
            if line.rstrip() == o4w_line:
                osgeo4w_py3_batch_file.write(qt5_line + '\n')
                osgeo4w_py3_batch_file.write(py3_line + '\n')

    return new_batch_filepath


def osgeo4w_py_install(osgeo4w_py3_batchfile, python_pack):
    py_packages = ' '.join(python_pack)
    py_install = '"{}" {} {} '.format(osgeo4w_py3_batchfile, 'python -m pip install', py_packages)
    print(py_install)
    res = subprocess.call(py_install, shell=True)
    return res


def osgeo4w_install(is64, base_url, osgeo4w_setup_exe_dir, osgeo4w_root, local_package_dir, osgeo4w_packages, python_packages):
    setup_filename = "osgeo4w-setup-x86{}.exe".format('_64' if is64 else '')
    setup_exe_path = os.path.join(osgeo4w_setup_exe_dir, setup_filename)

    print('-' * 50)
    print('OSGeo4W setup{}: '.format('64' if is64 else '32') + setup_exe_path)
    print('OSGeo4W Root: ' + osgeo4w_root)
    print('OSGeo4W Local package dir: ' + local_package_dir)
    print('OSGeo4W Package list: ' + str(osgeo4w_packages))
    print('Python3 Package list: ' + str(python_packages))
    print('-' * 50)

    if not os.path.isfile(setup_exe_path):
        if not os.path.isdir(osgeo4w_setup_exe_dir):
            os.makedirs(osgeo4w_setup_exe_dir)
        url = base_url + setup_filename
        print('downloading {}...'.format(url))
        urllib.request.urlretrieve(url, setup_exe_path)

    ret = osgeo4w_setup_run(setup_exe_path, base_url, osgeo4w_root, local_package_dir, osgeo4w_packages)
    if ret != 0:
        print('installation failed')
        return ret
    osgeo4w_batch_filename = os.path.join(osgeo4w_root, 'OSGeo4W.bat')
    osgeo4w_batch_filename = osgeo4w_py3_batchfile_create(osgeo4w_batch_filename, osgeo4w_root)
    osgeo4w_py_install(osgeo4w_batch_filename, python_packages)
    if not copy_geos_c_dll(osgeo4w_root):
        print('{}: copy geos_c.dll failed'.format(osgeo4w_root))


def osgeo4w_installs(is64_arcs, osgeo4w_root_base, dir_suffix):
    base_url = 'http://download.osgeo.org/osgeo4w/'
    osgeo4w_packages = ['python3-gdal', 'python3-pip', 'python3-setuptools', 'gdal-ecw', 'gdal-mrsid', 'python3-pandas',
                        'python3-matplotlib', 'pyqt5']
    python_packages = ['angles', 'geographiclib', 'shapely']
    # python_packages2 = ['pandas', 'geopandas']

    for is64 in is64_arcs:
        arch_suffix = '64' if is64 else '32'
        osgeo4w_root = osgeo4w_root_base + arch_suffix + dir_suffix
        local_package_dir = osgeo4w_root + '-Setup'
        osgeo4w_setup_exe_dir = local_package_dir
        osgeo4w_install(is64, base_url, osgeo4w_setup_exe_dir, osgeo4w_root, local_package_dir, osgeo4w_packages, python_packages)


def copy_geos_c_dll(path):
    src = os.path.join(path, r'bin\geos_c.dll')
    if not os.path.isfile(src):
        return False
    dst = os.path.join(path, r'apps\Python37\Library\lib\geos_c.dll')
    if os.path.isfile(dst):
        return True
    dst_dir = os.path.split(dst)[0]
    os.makedirs(dst_dir, exist_ok=True)
    copyfile(src, dst)
    return True


if __name__ == '__main__':
    osgeo4w_root_base = r"D:\OSGeo4W"
    dir_suffix = ''
    is64_arcs = [True, False]
    osgeo4w_installs(is64_arcs, osgeo4w_root_base, dir_suffix)
