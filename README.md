## msr-cli

`msr-cli` is a command-line tool for reading USB magnetic stripe card reader
data.

### Installing

```
pip3 install -U git+https://github.com/kalmanolah/msr-cli.git
```

## Usage

From the command line:

```
$ msr-cli --device-vendor-id 0x03f0 --device-product-id 0x2724
```

From python:

```python
from msr-cli import MsrCli

msr = MsrCli(device_vendor_id=0x03f0, device_product_id=0x2724)
msr.load_device_endpoint()

while True:
    try:
        data = msr.read_data()

        if data:
            print(json.dumps(data))
    except KeyboardInterrupt:
        break
```
