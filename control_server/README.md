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


## Running tests
1. Install the required prerequisites, as described in Section above.
2. Navigate to the `control_server` directory in a terminal.
3. Set up a MongoDB server so that it is accessible from control server using the settings specified in the `.env` file, or configure the `.env` file so that `MOCK_DB` is set to `True` to use the mock database for running tests.    
4. Run the following command: `pytest tests/`
