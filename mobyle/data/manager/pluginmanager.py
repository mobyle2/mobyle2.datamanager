'''
Plugin manager for ObjectManager
'''

import os

import logging
logging.basicConfig(level=logging.DEBUG)


from yapsy.PluginManager import PluginManager


class DataPluginManager:
    '''
    This class manages the plugins for the datamanager. It loads the plugins
     with yapsy in the subdirectory named plugins.
    '''

    manager = None
    supported_protocols = {}

    @staticmethod
    def get_manager():
        '''
        Returns the plugin manager singleton
        '''
        if DataPluginManager.manager is None:
            DataPluginManager.manager = PluginManager()
            DataPluginManager.manager.setPluginPlaces(
                [os.path.dirname(os.path.realpath(__file__)) + '/plugins'])
            # Load all plugins
            DataPluginManager.manager.collectPlugins()

            DataPluginManager.supported_protocols = {}
            # Activate all loaded plugins
            for plugin_info in DataPluginManager.manager.getAllPlugins():
                (protocol, name) = plugin_info.plugin_object.register()
                DataPluginManager.supported_protocols[name] = protocol
                DataPluginManager.manager.activatePluginByName(plugin_info.name)
                plugin_info.plugin_object.print_name()
        return DataPluginManager.manager

