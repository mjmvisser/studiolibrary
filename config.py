# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os

import studiolibrary

studiolibrary.Library.DEFAULT_PLUGINS = [
    "studiolibraryplugins.lockplugin",
    "studiolibraryplugins.poseplugin",
    "studiolibraryplugins.animationplugin",
    "studiolibraryplugins.mirrortableplugin",
    "studiolibraryplugins.selectionsetplugin"
]

# studiolibrary.Library.DEFAULT_COLOR = "rgb(0,200,100)"
# studiolibrary.Library.DEFAULT_BACKGROUND_COLOR = "rgb(60,100,180)"

studiolibrary.CHECK_FOR_UPDATES_ENABLED = False

studiolibrary.Analytics.ENABLED = False
studiolibrary.Analytics.DEFAULT_ID = "UA-50172384-1"

studiolibrary.FoldersWidget.CACHE_ENABLED = True
studiolibrary.FoldersWidget.SELECT_CHILDREN_ENABLED = False

studiolibrary.Settings.DEFAULT_PATH = os.getenv('APPDATA') or os.getenv('HOME')
studiolibrary.Settings.DEFAULT_PATH += "/studiolibrary"

# Meta paths and version paths are camel case for legacy reasons
studiolibrary.Record.META_PATH = "<PATH>/.studioLibrary/record.dict"
studiolibrary.Folder.META_PATH = "<PATH>/.studioLibrary/folder.dict"
studiolibrary.Folder.ORDER_PATH = "<PATH>/.studioLibrary/order.list"

studiolibrary.MasterPath.VERSION_CONTROL_ENABLED = True
studiolibrary.MasterPath.VERSION_PATH = "<DIRNAME>/.studioLibrary/<NAME><EXTENSION>/<NAME><VERSION><EXTENSION>"
