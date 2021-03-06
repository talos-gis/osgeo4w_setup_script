""" osgeo4w downloader and setup automation script.

This script does the following:
    0. downloads the osgeo4w setup file.
    1. runs the setup with given packages list.
    2. makes an extended osgeo4w batch file (with: py3, qt5, pycharm).
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

import datetime
import filecmp
import inspect
import os
import subprocess
import urllib.request
from typing import Sequence
from shutil import copyfile

from osgeo4w_installer.pycharm_env_batch_maker import pycharm_env_batch_maker


def is_list_like(lst):
    return isinstance(lst, Sequence) and not isinstance(lst, str)


def osgeo4w_setup_run(setup_exe_path, site, osgeo4w_root, local_package_dir, osgeo4w_packages, offline_mode, quiet_mode):
    arguments = [
        '--autoaccept',
        '--advanced'
    ]
    if quiet_mode:
        arguments.append('--quiet-mode')
    if offline_mode:
        arguments.append('--local-install')
    osgeo4w_install_cmd = ' '.join(
        [setup_exe_path,
         *arguments,
         '--site', site,
         '--root', '"' + osgeo4w_root + '"',
         '--local-package-dir', '"' + local_package_dir + '"',
         *['--packages {}'.format(p) for p in osgeo4w_packages]])
    print(osgeo4w_install_cmd)
    return subprocess.call(osgeo4w_install_cmd, shell=True)


def osgeo4w_batchfile_extender(osgeo4w_batch, osgeo4w_root, batch_evn, batch_suffix):
    new_batch_filename = "OSGeo4W{}.bat".format(batch_suffix)
    new_batch_filepath = os.path.join(osgeo4w_root, new_batch_filename)

    extra_batches = ['o4w_env']
    for k in batch_evn:
        extra_batches.append(k)

    extra_batches_cmd = [r'call "%~dp0\bin\{}.bat"'.format(b) for b in extra_batches]
    o4w_line = extra_batches_cmd[0]

    with open(new_batch_filepath, 'w+') as osgeo4w_py3_batch_file:
        for line in open(osgeo4w_batch, 'r'):
            osgeo4w_py3_batch_file.write(line)
            if line.rstrip() == o4w_line:
                for batch_line in extra_batches_cmd[1:]:
                    osgeo4w_py3_batch_file.write(batch_line + '\n')

    return new_batch_filepath


def osgeo4w_py_install(osgeo4w_py3_batchfile, python_pack):
    py_packages = ' '.join(python_pack)
    py_install = '"{}" {} {} '.format(osgeo4w_py3_batchfile, 'python -m pip install', py_packages)
    print(py_install)
    res = subprocess.call(py_install, shell=True)
    return res


def osgeo4w_install_base(osgeo4w_root_base=None, root_suffix=..., setup_suffix='-Setup', is64=[True, False], **kwargs):
    if root_suffix is ...:
        root_suffix = '-' + datetime.date.today().strftime("%Y%m%d")

    if not is_list_like(is64):
        is64 = [is64]

    for is64 in is64:
        arch_suffix = '64' if is64 else '32'

        osgeo4w_root_prefix = osgeo4w_root_base + arch_suffix
        osgeo4w_root = osgeo4w_root_prefix + root_suffix
        local_package_dir = osgeo4w_root_base + setup_suffix
        osgeo4w_setup_exe_dir = local_package_dir

        osgeo4w_install(osgeo4w_setup_exe_dir=osgeo4w_setup_exe_dir, osgeo4w_root=osgeo4w_root,
                        local_package_dir=local_package_dir, is64=is64,
                        **kwargs)


def osgeo4w_install(osgeo4w_setup_exe_dir, osgeo4w_root, local_package_dir,
                    is64=True,
                    base_url=..., gdalos_path=..., batch_evn=...,
                    osgeo4w_packages=..., python_packages=...,
                    offline_mode=False, quiet_mode=True, dev=False):
    if base_url is ...:
        base_url = 'http://download.osgeo.org/osgeo4w/'

    if osgeo4w_packages is ...:
        osgeo4w_packages = ['python3-gdal', 'python3-pip', 'python3-setuptools',
                            'gdal-ecw', 'gdal-mrsid', 'gdal-csharp',
                            'python3-pandas', 'python3-matplotlib', 'gdal201dll', 'gdal204dll']
        if dev:
            osgeo4w_packages.append('python3-gdal-dev')
    if batch_evn is ...:
        batch_evn = list()
        batch_evn.append('py3_env')
        batch_evn.append('qt5_env')
        batch_evn.append('pycharm_env')

    if 'qt5_env' in batch_evn:
        osgeo4w_packages.extend(['pyqt5', 'sip-qt5'])

    if python_packages is ...:
        python_packages = ['angles', 'geographiclib', 'shapely', 'pyproj', 'fidget', 'gdalos', 'transmogripy', 'osgeo4w_installer']
        # python_packages = ['pandas', 'geopandas']

    if gdalos_path is ...:
        gdalos_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
        gdalos_path = os.path.join(gdalos_path, r'..\..\gdalos')

    setup_filename = "osgeo4w-setup-x86{}.exe".format('_64' if is64 else '')
    setup_exe_path = os.path.join(osgeo4w_setup_exe_dir, setup_filename)

    print('-' * 50)
    print('OSGeo4W setup{}: '.format('64' if is64 else '32') + setup_exe_path)
    print('OSGeo4W Root: ' + osgeo4w_root)
    print('OSGeo4W Local package dir: ' + local_package_dir)
    print('OSGeo4W Package list: ' + str(osgeo4w_packages))
    print('Python3 Package list: ' + str(python_packages))

    if not os.path.isfile(setup_exe_path):
        if not os.path.isdir(osgeo4w_setup_exe_dir):
            os.makedirs(osgeo4w_setup_exe_dir)
        url = base_url + setup_filename
        print('downloading {}...'.format(url))
        urllib.request.urlretrieve(url, setup_exe_path)

    ret = osgeo4w_setup_run(setup_exe_path=setup_exe_path, site=base_url, osgeo4w_root=osgeo4w_root,
                            local_package_dir=local_package_dir, osgeo4w_packages=osgeo4w_packages,
                            offline_mode=offline_mode, quiet_mode=quiet_mode)
    if ret != 0:
        print('installation failed')
        return ret
    osgeo4w_batch_filename = os.path.join(osgeo4w_root, 'OSGeo4W.bat')
    osgeo4w3_batch_filename = osgeo4w_batchfile_extender(osgeo4w_batch=osgeo4w_batch_filename,
                                                        osgeo4w_root=osgeo4w_root,
                                                        batch_evn=batch_evn,
                                                        batch_suffix='3')
    if dev:
        batch_evn.append('gdal-dev-py3-env')
        batch_evn.append('proj-dev-env')
        osgeo4w3_dev_batch_filename = osgeo4w_batchfile_extender(osgeo4w_batch=osgeo4w_batch_filename,
                                                            osgeo4w_root=osgeo4w_root,
                                                            batch_evn=batch_evn,
                                                            batch_suffix='3-dev')

    fail_success = ('failed', 'succeeded')
    pycharm_batch = os.path.join(osgeo4w_root, 'bin', 'pycharm_env.bat')
    print('{}: creating pycharm_env.bat {}!'.format(osgeo4w_root, fail_success[pycharm_env_batch_maker(pycharm_batch)]))

    osgeo4w_py_install(osgeo4w3_batch_filename, python_packages)

    print('{}: copy geos_c.dll {}!'.format(osgeo4w_root, fail_success[copy_geos_c_dll(osgeo4w_root)]))
    print('{}: patching gdal.py {}!'.format(osgeo4w_root, fail_success[replace_gdal_py(osgeo4w_root, gdalos_path)]))
    print('-' * 50)


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
    return os.path.isfile(dst)


def replace_gdal_py(path, gdalos_path):
    src = os.path.join(gdalos_path, r'gdal_patches\gdal.py')
    dst = os.path.join(path, r'apps\Python37\lib\site-packages\osgeo\gdal.py')
    dst_bak = dst + '.bak'
    src_bak = src + '.bak'
    if not os.path.isfile(src):
        print('cannot replace src gdal.py, file not found: {}'.format(src))
        return False
    if not os.path.isfile(dst):
        print('cannot replace dst gdal.py, file not found: {}'.format(dst))
        return False
    if filecmp.cmp(src, dst):
        return True
    if not filecmp.cmp(src_bak, dst):
        print('cannot replace gdal.py, its contents are different then expected: {} -> {}'.format(src, dst))
        return False
    return file_replace(src, dst, dst_bak)


def file_replace(src, dst, bak=None):
    if not os.path.isfile(src) or not os.path.isfile(dst):
        return False
    if bak is not None:
        if os.path.isfile(bak):
            print('cannot replace gdal.py, bak file already exists: {}'.format(bak))
            return False
        else:
            os.rename(dst, bak)
    copyfile(src, dst)
    return os.path.isfile(dst) and filecmp.cmp(src, dst)


def main():
    osgeo4w_install_base(osgeo4w_root_base=r"D:\OSGeo4W", is64=[True, False], offline_mode=False, quiet_mode=False, dev=True)


if __name__ == '__main__':
    main()
