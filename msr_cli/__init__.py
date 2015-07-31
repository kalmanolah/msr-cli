"""Magnetic stripe card reader command-line utility."""
import logging
import argparse
import json
import usb.core
import usb.util


logger = logging.getLogger(__name__)
__VERSION__ = '0.0.1'


class MsrCli:

    """
    Magnetic stripe card reader command-line utility.

    Based on code from http://marker.to/bjAbN4.

    """

    def __init__(self, device_vendor_id, device_product_id, debug=False):
        """Constructor."""
        self.debug = debug
        self.device_vendor_id = device_vendor_id
        self.device_product_id = device_product_id
        self.data_length = 537

    def load_device_endpoint(self):
        """Initialize the device and load the correct endpoint."""
        self.device = usb.core.find(idVendor=self.device_vendor_id, idProduct=self.device_product_id)

        if not self.device:
            raise ValueError('Device not found')

        if self.device.is_kernel_driver_active(0):
            try:
                self.device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise e
                # sys.exit("Could not detatch kernel driver: %s" % str(e))

        try:
            self.device.set_configuration()
            self.device.reset()
        except usb.core.USBError as e:
            raise e
            # sys.exit("Could not set configuration: %s" % str(e))

        self.device_endpoint = self.device[0][(0, 0)][0]

    def read_data(self):
        """Attempt to read, process and return card data."""
        data = []
        swiped = False

        while True:
            try:
                if swiped:
                    return self.process_data(data)

                data += self.device.read(self.device_endpoint.bEndpointAddress, self.device_endpoint.wMaxPacketSize)

                if len(data) >= self.data_length:
                    swiped = True

            except usb.core.USBError as e:
                if e.args == ('Operation timed out',):
                    logger.error('Invalid swipe, discarding %s bytes of data', len(data))

                    data = []
                    swiped = False

                    continue

    def process_data(self, data):
        """Process magnetic card strip data."""
        encoding_formats = ['ISO/ABA', 'AAMVA', 'CADL', 'Blank', 'Other', 'Undetermined', 'None']

        parsed = {}
        parsed['encoding_type'] = encoding_formats[data[6]]
        parsed['tracks'] = [{}, {}, {}]

        data_offset = 9

        # Process all 3 tracks
        for i in range(0, 3):
            track = {}
            parsed['tracks'][i] = track

            track['length'] = data[i + 3]

            if not track['length']:
                continue

            track['raw'] = ''.join(map(chr, data[data_offset:data_offset + track['length'] + 1]))
            track['data'] = track['raw'].strip('\x10\t\n\r\0')

            data_offset += track['length'] + 1

            # Remove raw data
            track.pop('raw', None)

            # Skip empty tracks
            if not len(track['data']):
                continue

            if parsed['encoding_type'] == 'ISO/ABA':
                if i == 0:
                    format_code_offset = track['data'].find('%', 0)
                    primary_account_number_offset = format_code_offset + 1
                    name_offset = track['data'].find('^', format_code_offset + 1)
                    additional_data_offset = track['data'].find('^', name_offset + 1)

                    track['format_code'] = track['data'][format_code_offset + 1]
                    track['primary_account_number'] = track['data'][primary_account_number_offset + 1:name_offset]

                    track['name'] = track['data'][name_offset + 1:additional_data_offset]
                    track['last_name'], track['first_name'] = track['name'].split('/')

                    track['expiration_year'] = track['data'][additional_data_offset + 1:additional_data_offset + 3]
                    track['expiration_month'] = track['data'][additional_data_offset + 3:additional_data_offset + 5]
                elif i == 1:
                    primary_account_number_offset = track['data'].find(';', 0)
                    additional_data_offset = track['data'].find('=', primary_account_number_offset + 1)

                    track['primary_account_number'] = track['data'][primary_account_number_offset + 1:
                                                                    additional_data_offset]

                    track['expiration_year'] = track['data'][additional_data_offset + 1:additional_data_offset + 3]
                    track['expiration_month'] = track['data'][additional_data_offset + 3:additional_data_offset + 5]

        return parsed


def auto_int(x):
    """Convert a string to int with auto base detection."""
    return int(x, 0)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(prog='msr-cli', description='%(prog)s is a CLI for reading magnetic card data.')
    parser.add_argument('-dvid', '--device-vendor-id', required=True, type=auto_int)
    parser.add_argument('-dpid', '--device-product-id', required=True, type=auto_int)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __VERSION__)
    args = parser.parse_args()

    logging.basicConfig()

    msr = MsrCli(**vars(args))
    msr.load_device_endpoint()

    while True:
        try:
            data = msr.read_data()

            if data:
                print(json.dumps(data), flush=True)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    """Standard import guard."""
    main()
