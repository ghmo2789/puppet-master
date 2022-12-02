# Client

Client application that is supposed to be installed on target hosts that should be included in the client network.

## How to build and run application

1. Before building the client application, the environment variables in ``client/.cargo/config.toml`` must be set. In
   this file, communication protocol and URL/IP address to the control server is set.

2. When the variables are set, the client application can be built by run the following commands:
```
cd client/
cargo run --release
```

If not building for a release and want to test the application with debug output, remove the ``--release`` flag.

Note that if wanting to make changes to the configuration files between compilations, you may be required to remove your
previous compiled version. To do this, remove the generated ``client/target`` directory.

## How to run tests locally

If testing the client locally, you must first set the configuration file located in ``client/.cargo/config.toml`` as
following:

```
# Environment variables used during compile time
[env]
# Defines what protocol the client should use, set to either "https" or "udp"
PROTOCOL = "https"

# If using HTTPS as protocol, this defines the control server URL.
# Note that https:// should be used if traffic over https is desired
CONTROL_SERVER_URL = "http://127.0.0.1:8080"

# If using UDP as protocol, this defines the IP and port used by the control server
REMOTE_HOST = "127.0.0.1"
REMOTE_PORT = "65500"
```

To run the tests locally, you must also run the mock server that the client is using for testing. You can run the tests
with the following commands:

```
cd client/
python test/mock_server.py &  

cargo test
```

Make sure to let the mock server process start properly before running the tests with cargo!

If wanting to test the client with UDP communication, change the config to ``PROTOCOL= "udp"`` and run the mock server
and client with:

```
python test/mock_server.py --udp &

cargo run
```

Note that unit testing is not supported when running with UDP.