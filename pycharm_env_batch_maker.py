import os
from string import Template
from pathlib import Path


def pycharm_env_batch_maker(filename):
    years = range(2020, 2015, -1)
    quart = [3, 2, 1]
    builds = range(9, -1, -1)
    versions = ('{}.{}.{}'.format(year, q, b) for year in years for q in quart for b in builds)
    # print(versions)

    prefix = 'if not exist %PYCHARM% SET PYCHARM='
    pf64 = Path(r'C:\Program Files')
    pf32 = Path(r'C:\Program Files (x86)')
    jb = r'JetBrains\PyCharm '
    community = r'Community Edition '
    bin64 = r'bin\pycharm64.exe'
    bin32 = r'bin\pycharm.exe'

    try:
        with open(filename, mode='w') as f:
            f.write('@echo off\n')
            f.write('set PYCHARM="xxxxxx"\n\n')
            for v in versions:
                if v.endswith('.0'):
                    v = v[:-2]
                f.write(':: version {}\n'.format(v))
                for pf in (pf64, pf32):
                    for comm in (community, ''):
                        for bin_ in (bin64, bin32):
                            path = pf / (jb + comm + v) / bin_
                            f.write('{}"{}"\n'.format(prefix, path))
                f.write('\n')
            f.write('echo %PYCHARM%\n')
            f.write('if not exist %PYCHARM% exit /b 3')
        return True
    except:
        return False


if __name__ == '__main__':
    pycharm_env_batch_maker(r'..\bat\pycharm_env.bat')
