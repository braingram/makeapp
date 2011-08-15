#!/usr/bin/env python
"""
An uber-simple python script to app converter
"""

import logging, os, shutil, stat, sys
# logging.basicConfig(level=logging.DEBUG)
from optparse import OptionParser


launcherHead="""#!/bin/sh
DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR
"""
launcherTail="""
exec ./%s
"""

def error(string, exception=Exception):
    logging.error(string)
    raise exception, string


# parse command line options
parser = OptionParser(usage="usage: %prog [options] main.py resource(s)...")
parser.add_option("-i", "--icon", dest="icon",
                    help="icon file [icns] to use as the icon")
parser.add_option("-n", "--name", dest="name",
                    help="name of the resulting app [without .app]")
parser.add_option("-d", "--dir", dest="dir",
                    help="destination directory for .app")
parser.add_option("-r", "--resource", action="append", dest="resources",
                    help="resource files", default=[])
parser.add_option("-l", "--launcher", dest="launcher",
                    action="store_true", default=False,
                    help="construct and use a launcher shell script")
parser.add_option("-s", "--script", dest="script",
                    help="script to run as part of launcher")

(options, args) = parser.parse_args()
if len(args) == 0:
    parser.print_usage()
    error("len(args) == 0", ValueError)

main = args.pop(0)
supporting = args
resources = options.resources


# check if main, supporting and resources exist and make paths absolute
if not os.path.exists(main): error("main does not exist: %s" % main, ValueError)
main = os.path.abspath(main)
logging.debug("input main: %s" % main)

for (i,r) in enumerate(resources[:]):
    if not os.path.exists(r): error("resource does not exist: %s" % r, ValueError)
    resources[i] = os.path.abspath(r)
logging.debug("input resources: %s" % str(resources))

for (i,s) in enumerate(supporting[:]):
    if not os.path.exists(s): error("supporting file does not exist: %s" % s, ValueError)
    supporting[i] = os.path.abspath(s)
logging.debug("input supporting: %s" % str(supporting))


# construct options from input values
if options.name is None:
    options.name = os.path.splitext(os.path.basename(main))[0] + '.app'
else:
    if os.path.splitext(options.name)[1] != '.app':
        options.name = options.name + '.app'
logging.debug("app name: %s" % options.name)

if options.dir is None:
    options.dir = '.'
options.dir = os.path.abspath(options.dir)
logging.debug("output dir: %s" % options.dir)

appName = options.dir + '/' + options.name
logging.debug("output name: %s" % appName)


# check if current directory exists and delete it
if os.path.exists(appName):
    logging.debug("output file already exists, deleting")
    shutil.rmtree(appName)
    if os.path.exists(appName): error("failed to delete: %s" % appName, IOError)

logging.debug("making directories")
exeDir = appName+'/Contents/MacOS/'
os.makedirs(exeDir)
resourceDir = appName+'/Contents/Resources/'
os.makedirs(resourceDir)
exeName = os.path.basename(main)

# construct launcher
if options.launcher or (not (options.script is None)):
    logging.debug("Making launcher")
    launcher = launcherHead
    if options.script is None:
        script = ""
    else:
        if os.path.exists(options.script):
            logging.debug("Found launcher file: %s" % options.script)
            scriptFile = open(options.script, 'r')
            script = scriptFile.read()
            scriptFile.close()
        else:
            script = options.script
    launcher += script
    launcher += launcherTail % os.path.basename(main)
    
    # write launcher to file
    exeName = 'launch.sh'
    launcherFilename = exeDir + '/' + exeName
    logging.debug("Writing launcher file: %s" % launcherFilename)
    launcherFile = open(launcherFilename, 'w')
    launcherFile.write(launcher)
    launcherFile.close()
    
    # make launcher executable
    logging.debug("making launcher executable")
    if os.system('chmod u+x %s' % launcherFilename): error("failed to set main %s as executable" % launcherFilename, IOError)

# move files
logging.debug("copying main")
shutil.copy2(main, exeDir)
logging.debug("making main executable")

# make main executable
dstMain = exeDir + '/' + os.path.basename(main)
if os.system('chmod u+x %s' % dstMain): error("failed to set main %s as executable" % dstMain, IOError)

# # main main/launcher executable
# dstExe = exeDir + '/' + exeName
# logging.debug("making main/launcher executable")
# if os.system('chmod u+x %s' % dstExe): error("failed to set permissions on app", IOError)

logging.debug("copying supporting files")
for s in supporting:
    logging.debug("copying supporting: %s" % s)
    if os.path.isdir(s):
        shutil.copytree(s, exeDir+'/'+os.path.basename(os.path.abspath(s)))
    else:
        shutil.copy2(s, exeDir)

logging.debug("copying resources")
for r in resources:
    logging.debug("copying resouce: %s" % r)
    if os.path.isdir(r):
        shutil.copytree(s, exeDir+'/'+os.path.basename(os.path.abspath(s)))
    else:
        shutil.copy2(r, resourceDir)

logging.debug("making plist")
plist = '{\n'
if not options.icon is None:
    icon = os.path.abspath(options.icon)
    if not os.path.exists(icon): error("icon file does not exist: %s" % icon, IOError)
    shutil.copy2(icon, resourceDir)
    plist += 'CFBundleIconFile = "%s";\n' % os.path.basename(icon)

plist += 'CFBundleExecutable = "%s";\n' % os.path.basename(exeName)
plist += '}\n'

logging.debug("writing plist")
plistFile = open(appName+'/Contents/Info.plist','w')
plistFile.write(plist)
plistFile.close()