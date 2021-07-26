import datetime
import base64
import json
import boto3
import os
import sys
import linecache
import calendar


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def check_payload(payload, tag):
    try:
        data = payload[tag]
        return True
    except Exception as e:
        return False


def lambda_handler(event, context):
    excp_cnt = 0
    s3 = boto3.resource('s3')

    total_records = len(event['Records'])
    print("Total records received: %s" % total_records)

    for record in event['Records']:
        try:

            payload = base64.b64decode(record['kinesis']['data']).decode("utf-8")
            l_json = json.loads(payload)
            l_creation = datetime.datetime.fromtimestamp(float(calendar.timegm(datetime.datetime.utcnow().timetuple())))

            print(l_json)
            print(l_creation)

            l_path_wo_hour = str(l_creation.year) + '/' + str(l_creation.strftime('%m')) + '/' + str(
                l_creation.strftime('%d')) + '/'

            # fetch parameters
            l_raw_bucket = os.environ.get('databucket')
            l_exception_bucket = os.environ.get('failedbucket')

            # validate payload
            try:
                if not check_payload(l_json, 'payload'):
                    raise Exception('Payload tag missing')
            except Exception as e:
                excp_cnt = excp_cnt + 1
                PrintException()
                s3.Bucket(l_exception_bucket).put_object(Key='Kinesis/failed_meesages/' + l_path_wo_hour + 'payload_'
                                                             + '.json',
                                                         Body=json.dumps(l_json))
                continue

            l_payload = l_json['payload']
            l_metadata = l_json['metadata']

            l_source = l_metadata['section']

            s3.Bucket(l_raw_bucket).put_object(
                Key='Kinesis/' + l_source + '/json/' + l_source + '_section/' + '/' + l_path_wo_hour + 'payload_' + '.json',
                Body=json.dumps(l_payload))

        except Exception as e:
            excp_cnt = excp_cnt + 1
            PrintException()
            s3.Bucket(l_exception_bucket).put_object(
                Key='Kinesis/failed_meesages/' + l_path_wo_hour + 'payload' + '.json',
                Body=json.dumps(l_json))
            PrintException()

    print(f'completed processing {total_records} records.')
    return 'True'
