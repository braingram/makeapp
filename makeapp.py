#!/usr/bin/env python
"""
An uber-simple python script to app converter
"""

import logging, os, shutil, stat, sys
# logging.basicConfig(level=logging.DEBUG)
from optparse import OptionParser

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

logging.debug("moving main")
shutil.copy2(main, exeDir)
dstMain = exeDir + '/' + os.path.basename(main)

logging.debug("making main executable")
if os.system('chmod u+x %s' % dstMain): error("failed to set permissions on app", IOError)

logging.debug("moving supporting files")
for s in supporting:
    logging.debug("moving supporting: %s" % s)
    shutil.copy2(s, exeDir)

logging.debug("moving resources")
for r in resources:
    logging.debug("moving resouce: %s" % r)
    shutil.copy2(r, resourceDir)

logging.debug("making plist")
plist = '{\n'
if not options.icon is None:
    icon = os.path.abspath(options.icon)
    if not os.path.exists(icon): error("icon file does not exist: %s" % icon, IOError)
    shutil.copy2(icon, resourceDir)
    plist += 'CFBundleIconFile = "%s";\n' % os.path.basename(icon)

plist += 'CFBundleExecutable = "%s";\n' % os.path.basename(main)
plist += '}\n'

logging.debug("writing plist")
plistFile = open(appName+'/Contents/Info.plist','w')
plistFile.write(plist)
plistFile.close()