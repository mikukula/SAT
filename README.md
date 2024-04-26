Setup instructions for the SAT:

NOTE: The specific commands may vary depending on your setup
Full testing was only performed on Windows

Detailed instructions for running from command line:
1. Make sure Python (at least 3.10) is installed and available from the
    command line (for example by adding it to the PATH environmet variables)
2. Place the "SAT" folder in your directory of choice
3. Open the terminal in the SAT directory
4. (Recommended) If you don't want to clutter your python installation then create a virtual environment
and activate it (refer https://docs.python.org/3/library/venv.html for instructions). This can also be useful to avoid 
already installed libraries from interfering.
5. Run "pip install -r requirements.txt" in the terminal. This will install all the required libraries.
    In case of issues proceed with step 4 and install the libraries in your virtual environment
6. Run "python src/main.py" to run the application.
7. After going through the setup process in the app you can
     delete the contents of config.json file to restart it.


General instructions for running in different environments:
1. Install the Python libraries inside the requirements.txt file using your package manager
2. Run the main.py file in src folder to start the application
3. Deleting the config.json file or its contents will reset the app initial setup process