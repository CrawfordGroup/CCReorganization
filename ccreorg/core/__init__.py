import os
plugdir = os.path.split(os.path.abspath(__file__))[0]
PLUGIN_SOFILE = plugdir + '/' + os.path.split(plugdir)[1] + '.so'
#don't load plugin here load one up instead
