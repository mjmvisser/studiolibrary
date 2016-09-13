#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary\core\pluginmanager.py
import os
import imp
import logging
from . import utils
__all__ = ['PluginManager']
logger = logging.getLogger(__name__)

class PluginManager:

    def __init__(self):
        """
        """
        self._plugins = {}

    def plugins(self):
        """
        :rtype: dict
        """
        return self._plugins

    def unloadPlugins(self):
        """
        :rtype: None
        """
        for plugin in self.plugins().values():
            self.unloadPlugin(plugin)

    def unloadPlugin(self, plugin):
        """
        :type plugin: Plugin
        """
        logger.debug('Unloading plugin: %s' % plugin.path())
        plugin.unload()
        if plugin.path() in self.plugins():
            del self.plugins()[plugin.path()]

    def loadedPlugins(self):
        """
        :rtype: dict
        """
        return self.plugins()

    def loadPlugin(self, path, **kwargs):
        """
        :type path: str
        """
        logger.debug('Loading plugin: %s' % path)
        path = path.replace('\\', '/')
        if path in self.plugins():
            plugin = self.plugins().get(path)
            logger.debug("Skipping: Plugin '%s' is already loaded!" % plugin.name())
            return plugin
        if os.path.exists(path):
            dirname, basename, extension = utils.splitPath(path)
            module = imp.load_source(basename, path)
        else:
            exec 'import ' + path
            module = eval(path)
        plugin = module.Plugin(**kwargs)
        plugin.setPath(path)
        plugin.load()
        self.plugins().setdefault(path, plugin)
        return plugin
