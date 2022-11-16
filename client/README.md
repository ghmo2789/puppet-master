# Client

Client application that is supposed to be installed on target hosts that should be included in the client network.

## How to build

To build the client application, run the following commands:

```
cd client/
export CONTROL_SERVER_URL=https://example.com
cargo build --release
```

If not building for a release and want to test the application with debug output, remove the ``--release`` flag.

Note that the control-server URL that the client call home to is set by the environment variable
``CONTROL_SERVER_URL``. The URL should only be the base URL and if using ``HTTPS/HTTP``, make sure to add the desired
protocol in the URL.