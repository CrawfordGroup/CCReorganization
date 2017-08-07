#! /usr/bin/env python
"""
This is a setup script to build the reorg plugin and make it importable.
Requires that Psi4 is installed, and the cmake is available.

If any requirements are not met, this script provides an env command which will
create a conda environment with all dependencies available.
"""

import setuptools
from setuptools.command.install import install

import os
import subprocess as sp
import shutil


def sanitize_cmake(output):
    print_out = []

    # Cut out a few warnings that are a bit annoying, GCC wont let us override them
    warnings = [
        ' warning: section "__textcoal_nt"',
        'note: change section name to "__const"',
        'change section name to "__text"',
        'note: change section name to "__data"',
        ' warning: section "__datacoal_nt"', 'warning: section "__const_coal"'
    ]
    x = 0
    while x < len(output):

        if any(warn in output[x] for warn in warnings):
            x += 3
            continue

        print_out.append(output[x])
        x += 1

    print_out = "\n".join(print_out)
    return print_out


class cmake_build(install):

    def _which(self, progname):
        output = sp.check_output(['which', progname]).decode('utf-8').strip()
        return output

    #    description = 'Build the nested CMake'

    def run(self):

        print("Checking for psi4...")
        try:
            output = self._which('psi4')
            print(">>> which psi4")
            print("{}".format(output))
        except sp.CalledProcessError:
            print("""
            Psi4 could not be found!

            If you have a working build env make sure you activate it before
            trying to build:
            >>> source activate <build_env_name>
            >>> python setup.py clean
            >>> python setup.py cmake

            If you need a build environment created for you use:

            >>> python setup.py easyenv
            >>> source activate ccreorg
            >>> python setup.py clean
            >>> python setup.py cmake
            """)


        # Find build directory (in-place)
        abspath = os.path.abspath(os.path.dirname(__file__))
        build_path = os.path.join(abspath, "ccreorg", "core")
        os.chdir(build_path)
        print(">>> cd {}".format(build_path))

        # Capture cmake command
        print("Acquiring CMake cache...")
        output = sp.check_output(["psi4", "--plugin-compile"]).decode("UTF-8")
        print(">>> psi4 --plugin-compile\n{}".format(output))
        if "cmake -C" not in output:
            raise Exception("Psi4 Cache Error.\n")

        # Run CMake command
        print("Building CMake structures...")
        output = sp.check_output(output.strip().split()).decode("UTF-8")
        print("{}".format(output))
        if "Build files have been" not in output:
            raise Exception("CMake error.\n")

        # Run install
        print("Compiling...")
        output = sp.check_output(
            ["make", "-j2", "VERBOSE=1"],
            stderr=sp.STDOUT).decode("UTF-8").splitlines()
        print_out = sanitize_cmake(output)
        #print_out = '\n'.join(output)
        print(">>> make -j2\n{}".format(print_out))

        if "[100%]" not in print_out:
            raise Exception("Build error.\n")


class cmake_clean(install):
    def run(self):

        # Find build directory (in-place)
        abspath = os.path.abspath(os.path.dirname(__file__))
        build_path = os.path.join(abspath, "ccreorg", "core")
        os.chdir(build_path)
        print("Removing CMake build files...")

        try:
            shutil.rmtree("CMakeFiles")
        except:
            pass

        files = [
            "CMakeCache.txt", "Makefile", "timer.dat", "cmake_install.cmake",
            "core.so"
        ]
        for f in files:
            try:
                os.remove(f)
            except OSError:
                pass

        print("...finished")


class easyenv(install):
    miniconda_instrucitons_OSX = """
    To install miniconda please use the following steps:
        Note: "$HOME/miniconda" can be replaced with any path you prefer.


    >>> curl https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O
    >>> bash Miniconda3-latest-MacOSX-x86_64.sh -b -p $HOME/miniconda
    >>> echo PATH="\$HOME/miniconda/bin:\$PATH" >> ~/.bash_profile

    """

    miniconda_instructions_linux = """
    To install miniconda please use the following steps:
        Note: "$HOME/miniconda" can be replaced with any path you prefer.

    >>> wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    >>> bash miniconda.sh -b -p $HOME/miniconda
    >>> echo PATH="\$HOME/miniconda/bin:\$PATH" >> ~/.bash_profile

    """

    def _which(self, progname):
        output = sp.check_output(['which', progname]).decode('utf-8').strip()
        return output

    def run(self):
        #detect osx/linux
        systype = sp.check_output(['uname']).decode('utf-8').strip()
        print(">>> uname\n{}".format(systype))
        try:
            conda_exe = self._which('conda')
        except sp.CalledProcessError:
            if systype.lower() == 'linux':
                print(self.miniconda_instructions_linux)
            else:
                print(self.miniconda_instructions_OSX)
            raise Exception('conda is required to generate easyenv')
        print(">>> which conda\n{}".format(conda_exe))

        conda_pkg_list = [
            'psi4', 'numpy', 'lawrap', 'cmake', 'jupyter', 'numexpr',
            'mkl-include', 'gcc-5-mp'
        ]
        # first blank needed for "-c ".join... to work
        conda_channels = [' ', 'intel', 'psi4/label/dev', 'psi4']
        if systype.lower() == 'darwin':
            conda_pkg_list += ['gnu']
            print(">>> sysctl machdep | grep features | grep -o AVX2")
            try:
                avx2 = sp.check_output(
                    "sysctl machdep | grep features | grep -o AVX2",
                    shell=True).decode('utf-8').strip()
                print(avx2)
            except:
                print("<not found>")
                conda_pkg_list += ['sse41']

        conda_cmd = "conda create --yes -n ccreorg python=3.5 "
        conda_cmd += " ".join(conda_pkg_list)
        conda_cmd += " -c ".join(conda_channels)

        print("conda cmd:\n")
        print("{}".format(conda_cmd))

        output = sp.check_output(
            conda_cmd, shell=True,
            stderr=sp.STDOUT).decode('utf-8').splitlines()
        print(">>> {}".format(conda_cmd))
        print("\n".join(output))
        print("... Finished")

        print("Now activate the environment ")
        print(">>> source activate ccreorg")
        print("Then clean out the build files")
        print(">>> python setup.py clean")
        print("Then build ")
        print(">>> python setup.py cmake")


if __name__ == "__main__":
    setuptools.setup(
        name='ccreorg',
        version="0.1.1",
        description='A Psi4 plugin for prototyping new cc* tech',
        author='The Crawford Research Group',
        author_email='crawdad@vt.edu',
        url="https://github.com/CrawfordGroup/CCReorganize",
        license='LGPL-3.0',
        packages=setuptools.find_packages(),
        # psi4 is also required, but not in PyPI
        install_requires=['numpy>=1.7', ],
        extras_require={
            'docs': [
                'sphinx==1.2.3',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
            ],
        },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=False,
        cmdclass={
            'cmake': cmake_build,
            'clean': cmake_clean,
            'easyenv': easyenv,
        }, )
