import json
import os

class Constants:
    def __init__(self):
        
        self._config_file = 'config.json'
        self._database_path_entry = 'database_path'
        self._database_path = self.loadDatabasePath()
        self.database_name = "SATDatabase.db"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.main_icon_location = os.path.join(script_dir, '..', 'resources/logos', 'favicon.png')


    def loadDatabasePath(self):
        try:
            with open(self._config_file, 'r') as file:
                config = json.load(file)
        except:
            config = {}

        config.setdefault(self._database_path_entry, '')

        with open(self._config_file, 'w') as file:
            json.dump(config, file, indent=2)

        return config[self._database_path_entry]

    def getDatabasePath(self):
        return self.loadDatabasePath()
    
    def setDatabasePath(self, new_path):

        if(self.validatePath(new_path) == False):
            raise ValueError("Illegal path")
        
        new_path = os.path.normpath(new_path)

        new_path = new_path.replace('\\', '/')
        self._database_path = new_path

        with open(self._config_file, 'r') as json_file:
            data = json.load(json_file)

        if self._database_path_entry not in data:
            self.loadDatabasePath()

        data[self._database_path_entry] = self._database_path

        with open(self._config_file, 'w') as json_file:
            json.dump(data, json_file, indent=2)


    def validatePath(self, path):
        try:
            # Attempt to normalize the path
            normalized_path = os.path.normpath(path)

            # Check if the normalized path is valid on Windows in this case
            if os.path.isabs(normalized_path) and os.name == 'nt':
                return True
            else:
                return False
        except:
            return False