# Client

Client application that is supposed to be installed on target hosts that should be included in the client network.

## How to build

To build the client application, run the following commands:

```
cd client
CONTROL_SERVER_URL=https://example.com
crate build --release
```

Note that the control-server URL that the client call home to is set by the environment variable
``CONTROL_SERVER_URL``. If using ``HTTPS/HTTP``, make sure to add the desired protocol in the URL.