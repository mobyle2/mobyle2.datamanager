import os

import logging
logging.basicConfig(level=logging.DEBUG)

import mobyle.data.manager

from yapsy.PluginManager import PluginManager

class DataPluginManager:

    manager = None
    supported_protocols = {}

    @staticmethod
    def get_manager():
        if DataPluginManager.manager is None:
            DataPluginManager.manager = PluginManager()
            DataPluginManager.manager.setPluginPlaces([os.path.dirname(os.path.realpath(__file__))+'/plugins'])
            # Load all plugins
            DataPluginManager.manager.collectPlugins()

            DataPluginManager.supported_protocols = {}
            # Activate all loaded plugins
            for pluginInfo in DataPluginManager.manager.getAllPlugins():
                (protocol,name) = pluginInfo.plugin_object.register()
                DataPluginManager.supported_protocols[name] = protocol
                DataPluginManager.manager.activatePluginByName(pluginInfo.name)
                pluginInfo.plugin_object.print_name()
        return DataPluginManager.manager

