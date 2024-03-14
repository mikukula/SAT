import json
import os
import re

class ConstantsAndUtilities:
    def __init__(self):
        
        self._config_file = 'config.json'
        self._database_path_entry = 'database_path'
        self._database_path = self.loadDatabasePath()
        self.database_name = "SATDatabase.db"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.main_icon_location = os.path.join(script_dir, '..', 'resources/logos', 'favicon.png')
        self.keyring_service_name = "SAT"
        self.keyring_user_name = "user_token"


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

        #unify the path to only include "/" characters
        new_path = new_path.replace('\\', '/')

        # Split the path into directory and filename parts
        directory, filename = os.path.split(new_path)

        # Check if the path contains a filename
        if "." in filename:
            # Remove the filename part if it does
            new_path = directory
        
        self._database_path = new_path

        # open the json file and check if it contains the database path
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

            # Check if the normalized path is valid on Windows
            if os.path.isabs(normalized_path) and os.name == 'nt':
                return True
            elif os.path.isabs(normalized_path) and os.name == 'posix':
                # Additional checks for a Linux path
                if normalized_path.startswith('/'):
                    return True
            else:
                return False
        except:
            return False
    
    #create folder for specified user's data
    #might be needed if multiple users log in from the same machine
    def createUserFolder(self, username):
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'user_data', username))
        os.makedirs(directory, exist_ok=True)

    def getUserFolder(self, username):
        self.createUserFolder(username)
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'user_data', username))
        
    def checkPasswordStrength(self, password):
        # Check if the password has at least 12 characters
        if len(password) < 12:
            return False

        # Check if the password contains at least 1 symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False

        # Check if the password contains at least 1 uppercase letter
        if not any(char.isupper() for char in password):
            return False

        # If all conditions are met, the password is strong
        return True
    
    def checkUsernameReq(self, username):
        if(len(username) < 5):
            return False
        
        return True
    
    def formatHTML(self, text: str, center = False, font_size = 12, font_weight=400):
        if(center == True):
            start_html = f"<html><head/><body><p align='center'><span style=' font-size:{font_size}pt; font-weight:{font_weight}'>"
        else:
            start_html = f"<html><head/><body><p><span style=' font-size:{font_size}pt; font-weight:{font_weight}'>"
        end_html = "</span></p></body></html>"
            
        return start_html + text + end_html