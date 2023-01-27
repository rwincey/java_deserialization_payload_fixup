import argparse
import struct
import os
import binascii

# local class incompatible: stream classdesc serialVersionUID = 2, local class serialVersionUID = -4756260244412887918
# BDFE 5E81 E875 0C92

# Replace major version with Java 1.1 so the following error will never happen
# java.lang.UnsupportedClassVersionError: Bad version number in .class file
def fixup_major(data):

    java_version_1 = 45
    version_bytes = struct.pack('>H', java_version_1)

    ret_data = data[:6]
    ret_data += version_bytes
    ret_data += data[8:]

    return ret_data

# Replace serial numbers in incompatible classes
# local class incompatible: stream classdesc serialVersionUID = 2, local class serialVersionUID = -4756260244412887918
def replace_serial(data, find, replace):

    ret_data = b''
    try:

        find_bytes = struct.pack('>q', int(find))
        print("[+] Bytes to find %s" % binascii.hexlify(find_bytes))
        replace_bytes = struct.pack('>q', int(replace))
        print("[+] Bytes to replace %s" % binascii.hexlify(replace_bytes))

        byte_offset = 0
        while len(data) > 0 and byte_offset != -1:

            byte_offset = data.find(find_bytes)
            if byte_offset != -1:
                print("[*] Serial found at offset %d" % byte_offset)
                ret_data = data[:byte_offset]
                ret_data += replace_bytes

                # Search again
                data = data[byte_offset+8:]

        ret_data += data

    except Exception as e:
        print(e)

    return ret_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--payload", help="Java Payload", required=True)
    parser.add_argument("-o", "--output_file", help="Fixed Payload", required=True)
    parser.add_argument("-t", "--target_serial", help="Java class serial to replace (signed integer)", required=True)
    parser.add_argument("-r", "--new_serial", help="Replacement Java class serial (signed integer)", required=True)
    
    args = parser.parse_args()

    # Get args
    output_file = args.output_file
    input_file = args.payload
    if os.path.exists(input_file):
        f = open(input_file, 'rb')
        data = f.read()
        f.close()

    # Fix the version
    data = fixup_major(data)

    # Fix class serial versions
    target_serial = args.target_serial
    new_serial = args.new_serial
    data = replace_serial(data, target_serial, new_serial)

    # Write it out
    if len(data) > 0:
        f = open(output_file, 'wb')
        f.write(data)
        f.close()
