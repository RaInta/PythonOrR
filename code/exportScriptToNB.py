#!/usr/bin/env python
#
###########################################
#
# File: exportScriptToNB.py
# Author: Ra Inta
# Description:
# Created: June 25, 2019
# Last Modified: June 25, 2019
#
###########################################

from IPython.nbformat import v3, v4

with open("webinar.py") as fpin:
    text = fpin.read()

text += """
# <markdowncell>

# If you can read this, reads_py() is no longer broken!
"""

nbook = v3.reads_py(text)
nbook = v4.upgrade(nbook)  # Upgrade v3 to v4

jsonform = v4.writes(nbook) + "\n"

with open("test.ipynb", "w") as fpout:
    fpout.write(jsonform)




###########################################
# End of exportScriptToNB.py
###########################################
