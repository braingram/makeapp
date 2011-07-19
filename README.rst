=====
What is this?
=====
This is a simple script to convert scripts (built for python may work with others) into app bundles to easily run on Mac OS X.

Usage
-------

Basic command syntax::
    makeapp.py main supporting_module(s) -r resource1 -r resource2... [options]

Where the various parts are:

main
    the script to execute

supporting_module(s)
    other scripts or modules that will be placed in the same (Contents/MacOS) directory as main

resource(s)
    files that will be placed in Contents/Resources. Multiple resources can be defined with -r resource

options 
    described below

Options
-------

-d, --dir       destination directory for app

-i, --icon      icon file (.icns) to use [default = None]

-l, --launcher  use a launcher script to set the working directory to Contents/MacOS

-n, --name      name of the resulting app (without .app) [default = basename of main script]

-r, --resource  defines one of potentially many resource files

-s, --script    add a script (either a file or text) to the launcher script. This text will be executed with sh 
                after changing the working directory and prior to executing main

Plans
-------
Maybe add configuration/build files or integrate with distribute setup.