#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\imagesequencetimer.py
import os
from PySide import QtGui
from PySide import QtCore
__all__ = ['ImageSequenceTimer', 'ImageSequenceWidget']

class ImageSequenceTimerSignal(QtCore.QObject):
    onFrameChanged = QtCore.Signal(str)


class ImageSequenceTimer(QtCore.QObject):
    DEFAULT_FPS = 24

    def __init__(self, *args):
        QtCore.QObject.__init__(self, *args)
        self._fps = self.DEFAULT_FPS
        self._timer = None
        self._frame = 0
        self._frames = []
        self._dirname = None
        self._paused = False
        self.signal = ImageSequenceTimerSignal()
        self.onFrameChanged = self.signal.onFrameChanged

    def setDirname(self, dirname):
        self._dirname = dirname
        if os.path.isdir(dirname):
            self._frames = [ dirname + '/' + filename for filename in os.listdir(dirname) ]
            self._frames.sort()

    def dirname(self):
        return self._dirname

    def reset(self):
        if not self._timer:
            self._timer = QtCore.QTimer(self.parent())
            self._timer.setSingleShot(False)
            self.connect(self._timer, QtCore.SIGNAL('timeout()'), self._frameChanged)
        if not self._paused:
            self._frame = 0
        self._timer.stop()

    def pause(self):
        self._paused = True
        self._timer.stop()

    def stop(self):
        self._frame = 0
        self._timer.stop()

    def start(self):
        self.reset()
        if self._timer:
            self._timer.start(1000.0 / self._fps)

    def frames(self):
        return self._frames

    def _frameChanged(self):
        if not self._frames:
            return
        self._frame += 1
        if self._frame >= len(self._frames) or self._frame <= 0:
            self._frame = 0
        self.onFrameChanged.emit(self._frames[self._frame])

    def frameChanged(self, filename):
        pass

    def percent(self):
        if len(self._frames) == self._frame + 1:
            _percent = 1
        else:
            _percent = float(len(self._frames) + self._frame) / len(self._frames) - 1
        return _percent

    def duration(self):
        return len(self._frames)

    def currentFilename(self):
        try:
            return self._frames[self.currentFrame()]
        except IndexError:
            pass

    def currentFrame(self):
        return self._frame

    def setCurrentFrame(self, frame):
        if frame < self.duration():
            self._frame = frame


class ImageSequenceWidget(QtGui.QToolButton):

    def __init__(self, *args):
        QtGui.QToolButton.__init__(self, *args)
        self.setStyleSheet('border: 0px solid rgb(0, 0, 0, 20);')
        self._filename = None
        self._sequenceTimer = ImageSequenceTimer(self)
        self._sequenceTimer.onFrameChanged.connect(self.frameChanged)
        self.setSize(150, 150)
        self.setMouseTracking(True)

    def isControlModifier(self):
        """
        :rtype: bool
        """
        modifiers = QtGui.QApplication.keyboardModifiers()
        return modifiers == QtCore.Qt.ControlModifier

    def setSize(self, w, h):
        self._size = QtCore.QSize(w, h)
        self.setIconSize(self._size)
        self.setFixedSize(self._size)

    def currentIcon(self):
        return QtGui.QIcon(self._sequenceTimer.currentFilename())

    def setDirname(self, dirname):
        self._sequenceTimer.setDirname(dirname)
        if self._sequenceTimer.frames():
            icon = self.currentIcon()
            self.setIcon(icon)

    def enterEvent(self, event):
        self._sequenceTimer.start()

    def leaveEvent(self, event):
        self._sequenceTimer.pause()

    def mouseMoveEvent(self, event):
        if self.isControlModifier():
            percent = 1.0 - float(self.width() - event.pos().x()) / float(self.width())
            frame = int(self._sequenceTimer.duration() * percent)
            self._sequenceTimer.setCurrentFrame(frame)
            icon = self.currentIcon()
            self.setIcon(icon)

    def frameChanged(self, filename):
        if not self.isControlModifier():
            self._filename = filename
            icon = self.currentIcon()
            self.setIcon(icon)

    def paintEvent(self, event):
        QtGui.QToolButton.paintEvent(self, event)
        painter = QtGui.QPainter()
        painter.begin(self)
        if self._filename:
            r = event.rect()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 80, 80)))
            painter.drawRect(r.x(), r.y(), self._sequenceTimer.percent() * r.width() - 1, 2)
        painter.end()
