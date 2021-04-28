import os
import boto3
import json
import tempfile
from farmsync import config
from farmsync.utility import logger
from botocore.exceptions import ClientError

s3_resource = boto3.resource('s3', region_name=config.AWS_REGION)
s3_client = boto3.client('s3', region_name=config.AWS_REGION)
img_rekog_client = boto3.client('rekognition', region_name=config.AWS_REGION)

# Export Credentials to Environment
def set_aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = config.AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = config.AWS_SECRET_ACCESS_KEY

def create_s3_dir(key):
    try:
        s3_client.put_object(
            Bucket=config.S3_BUCKET,
            Body='',
            Key=key + "/"
        )
        return os.path.join(config.S3_BUCKET, key)
    except Exception as e:
        raise Exception('Failed to create S3 dir: {} with error: {}'
                        .format(key, str(e)))

def get_s3_files(bucket, prefix):
    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    file_names = []
    for response in response_iterator:
        for object_data in response['Contents']:
            key = object_data['Key']
            if not key.endswith("/"):
                file_names.append(os.path.basename(key))

    return file_names

def list_s3_objects(bucket, key):
    objs = []
    if not key.endswith("/"):
        key = key + "/"
    result = s3_client.list_objects(Bucket=bucket,
                                    Prefix=key,
                                    Delimiter='/')
    if 'CommonPrefixes' not in result.keys():
        return objs
    for obj in result.get('CommonPrefixes'):
        objs.append(os.path.basename(obj.get('Prefix').rstrip('/')))

    return objs

def upload_file_to_s3(bucket, source_file, dest_file):
    try:
        s3_client.upload_file(source_file, bucket, dest_file)
        logger.info("Successfully uploaded file {} to s3".format(source_file))
    except Exception as e:
        raise Exception("Failed to upload file: {} to S3 with error: {}" \
                        .format(source_file, str(e)))

def detect_image_labels(image):
    labels = {}
    try:
        with open(image, 'rb') as out:
            labels = img_rekog_client.detect_labels(Image={'Bytes': out.read()})
            labels = labels.get('Labels')
    except Exception as e:
        logger.error("Failed to detect lables from image: {} with error :{}" \
                    .format(image, str(e)))
    return labels
