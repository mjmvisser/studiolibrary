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
import logging

from PySide import QtGui

import studioqt
import studiolibrary


__all__ = ["Folder"]

logger = logging.getLogger(__name__)


class InvalidPathError(Exception):
    """
    """


class Folder(studiolibrary.MasterPath):

    META_PATH = "<PATH>/.studioLibrary/folder.dict"
    ORDER_PATH = "<PATH>/.studioLibrary/order.list"

    def __init__(self, path):
        """
        :type path: str
        """
        if not path:
            raise InvalidPathError("Invalid folder path specified")

        studiolibrary.MasterPath.__init__(self, path)
        self._pixmap = None

    def save(self, force=False):
        """
        """
        logger.debug("Saving folder '%s'" % self.path())

        if "." in os.path.basename(self.path()):
            raise ValueError('Invalid token "." (dot) found in name')

        if self.exists():
            if force:
                self.retire()
            else:
                raise Exception("Folder already exists!")

        self.metaFile().save()
        logger.debug("Saved folder '%s'" % self.path())

    def reset(self):
        """
        :type: None
        """
        if 'bold' in self.metaFile().data():
            del self.metaFile().data()['bold']

        if 'color' in self.metaFile().data():
            del self.metaFile().data()['color']

        if 'iconPath' in self.metaFile().data():
            del self.metaFile().data()['iconPath']

        if 'iconVisibility' in self.metaFile().data():
            del self.metaFile().data()['iconVisibility']

        self.metaFile().save()
        self._pixmap = None

    def setColor(self, color):
        """
        :type color: QtGui.QColor
        """
        self._pixmap = None
        if isinstance(color, QtGui.QColor):
            color = ('rgb(%d, %d, %d, %d)' % color.getRgb())
        self.metaFile().set("color", color)
        self.metaFile().save()

    def color(self):
        """
        :rtype: QtGui.QColor or None
        """
        color = self.metaFile().get('color', None)
        if not color and self.isDefaultIcon():
            color = "rgb(255,255,255,220)"

        if color:
            r, g, b, a = eval(color.replace('rgb', ""), {})
            return QtGui.QColor(r, g, b, a)
        else:
            return None

    def setIconVisible(self, value):
        """
        :type value: bool
        """
        self.metaFile().set("iconVisibility", value)
        self.metaFile().save()

    def isIconVisible(self):
        """
        :rtype: bool
        """
        return self.metaFile().get("iconVisibility", True)

    def setBold(self, value, save=True):
        """
        :type value: bool
        :type save: bool
        """
        self.metaFile().set("bold", value)
        if save:
            self.metaFile().save()

    def isBold(self):
        """
        :rtype: bool
        """
        return self.metaFile().get("bold", False)

    def name(self):
        """
        :rtype: str
        """
        return os.path.basename(self.path())

    def setPixmap(self, pixmap):
        """
        :type pixmap: QtGui.QPixmap
        """
        self._pixmap = pixmap

    def setIconPath(self, iconPath):
        """
        :type iconPath: str
        """
        self._pixmap = None
        self.metaFile().set('iconPath', iconPath)
        self.metaFile().save()

    def isDefaultIcon(self):
        """
        :rtype: bool
        """
        return not self.metaFile().get("iconPath", None)

    def iconPath(self):
        """
        :rtype: str
        """
        iconPath = self.metaFile().get("icon", None)  # Legacy
        iconPath = self.metaFile().get("iconPath", iconPath)

        if not iconPath:
            iconPath = studiolibrary.resource().get("icons", "folder")

        return iconPath

    def pixmap(self):
        """
        :rtype: QtGui.QPixmap
        """
        if not self.isIconVisible():
            return studiolibrary.resource().pixmap("")

        if not self._pixmap:
            color = self.color()
            iconPath = self.iconPath()
            self._pixmap = studioqt.Pixmap(iconPath, color=color)

            if color:
                self._pixmap.setColor(color)

        return self._pixmap

    def orderPath(self):
        """
        :rtype: str
        """
        path = self.ORDER_PATH
        return self.resolvePath(path)

    def setOrder(self, order):
        """
        :type order: list[str]
        :rtype: None
        """
        path = self.orderPath()
        dirname = os.path.dirname(path)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(path, "w") as f:
            f.write(str(order))

    def order(self):
        """
        :rtype: list[str]
        """
        order = []
        path = self.orderPath()

        if os.path.exists(path):

            with open(path, "r") as f:
                data = f.read().strip()

                if data:
                    order = eval(data, {})

        return order
