import boto3
import os


def read_file(file, directory):
    try:
        with open(os.path.join(directory, file), 'r') as payload_file:
            payload = payload_file.read()
    except IOError as ex:
        print("Problem reading: %s | %s | %s" % (directory, file, str(ex)), exc_info=True)
    return payload


kinesis_client = boto3.client('kinesis', 'eu-west-1')
payload = read_file('log_1.json',
                    'C:\\Users\\sanchit.latawa\\Desktop\\Data-Streaming-Using-Aws-Kinesis-Lambda-S3\\tests\\data')
put_response = kinesis_client.put_record(
    StreamName='sl-incoming-kinesis-stream',
    Data=payload,
    PartitionKey='test')
print(put_response)

payload = read_file('log_2.json',
                    'C:\\Users\\sanchit.latawa\\Desktop\\Data-Streaming-Using-Aws-Kinesis-Lambda-S3\\tests\\data')
put_response = kinesis_client.put_record(
    StreamName='sl-incoming-kinesis-stream',
    Data=payload,
    PartitionKey='test')
print(put_response)

payload = read_file('log_3.json',
                    'C:\\Users\\sanchit.latawa\\Desktop\\Data-Streaming-Using-Aws-Kinesis-Lambda-S3\\tests\\data')

put_response = kinesis_client.put_record(
    StreamName='sl-incoming-kinesis-stream',
    Data=payload,
    PartitionKey='test')
print(put_response)
print('done')
