# Control Server
This is the control server for the puppet-master system, which is responsible 
for handling communication with, and delegation of tasks to, the client.

## Installation
1. Make sure a recent version of Python is installed, along with tools like pip.
2. Install the required packages with `pip install -r requirements.txt`.
3. Set up the required settings in a `.env` file within the `control_server` 
   directory. See [sample.env](sample.env) for examples of how the settings
   can be configured.

## Usage
1. Navigate to the control_server directory in a terminal.
2. Set the environment variable `FLASK_APP=src/router.py:init`, or use the 
   `--app=src/router.py:init` flag later in the next step, when running the `flask`
   command.
3. Run the server with `python -m flask run --host=0.0.0.0`.
4. If all settings and dependencies were set up correctly, the server will be
   should be available at `http://localhost:5000`.