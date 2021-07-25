import datetime
import base64
import json
import boto3
import re
import os
import sys
import linecache
import calendar
import uuid


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
    s3 = boto3.resource('s3')

    total_records = len(event['Records'])
    print("Total records received: %s" % total_records)

    for record in event['Records']:
        try:
            # Kinesis data is base64 encoded so decode here, convert bytes to string
            payload = base64.b64decode(record['kinesis']['data']).decode("utf-8")
            l_json = json.loads(payload)
            l_creationTS = datetime.datetime.fromtimestamp(float(l_json['creationTS']))
            print(l_json)

            l_path_wo_hour = str(l_creationTS.year) + '/' + str(l_creationTS.strftime('%m')) + '/' + str(
                l_creationTS.strftime('%d')) + '/'

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
                                                             + l_guid + '.json',
                                                         Body=json.dumps(l_json))
                # process next record
                continue

            l_payload = l_json['payload']

            l_source = 'website-1'

            s3.Bucket(l_raw_bucket).put_object(
                Key='Kinesis/' + l_source + '/json/' + l_source + '_trade/' + l_assetClass + '/' + l_path_wo_hour + 'payload_' + l_guid + '.json',
                Body=json.dumps(l_new_json))


        except Exception as e:
            excp_cnt = excp_cnt + 1
            # print("error: %s" % str(e))
            PrintException()
            s3.Bucket(l_exception_bucket).put_object(
                Key='Kinesis/failed_meesages/' + l_path_wo_hour + 'payload' + '.json',
                Body=json.dumps(l_json))
            PrintException()

    print(f'completed processing {total_records} records.')
    return 'True'
