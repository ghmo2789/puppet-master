# Client

Client application that is supposed to be installed on target hosts that should be included in the client network.

## How to build and run application

To build and the client application, run the following commands:

```
cd client/
export CONTROL_SERVER_URL=https://example.com
cargo run --release
```

If not building for a release and want to test the application with debug output, remove the ``--release`` flag.

Note that the control-server URL that the client call home to is set by the environment variable
``CONTROL_SERVER_URL``. The URL should be the base URL and if using ``HTTPS/HTTP``, make sure to add the desired
protocol in the URL.

## How to run tests locally

To run the tests locally, you must also run the mock server that the client is using for testing. You can run the tests
with the following commands:

```
cd client/
export CONTROL_SERVER_URL=http://127.0.0.1:8080
python test/mock_server.py &  

cargo test
```

Make sure to let the mock server process start properly before running the tests with cargo!
