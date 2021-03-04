""" test code to read/write to S3"""

# import os
# import boto3
# import botocore
# import awscli
#
# files = ['Hazard_AllTotal_EAL_1.png']
#
# bucket = 'uri-test-1'
#
# dest = 'test.png'
#
# s3 = boto3.resource('s3')
#
# for file in files:
#    try:
#        s3.Bucket(bucket).download_file(file, dest)
#    except botocore.exceptions.ClientError as e:
#        if e.response['Error']['Code'] == "404":
#            print("The object does not exist.")
#        else:
#            raise



#%%  follow tutorial at https://www.youtube.com/watch?v=QV8OGJW-Fj4&list=PLI8raxzYtfGyJM30-lltxkhgrxjWimxt3

import boto3

aws_resource = boto3.resource("s3")
bucket=aws_resource.Bucket("totaltechnology-tutorial2021")

for bucket in aws_resource.buckets.all():
    print(bucket.name)

response = bucket.create(
    ACL='public-read-write',
    CreateBucketConfiguration={
        'LocationConstraint': 'eu-central-1'
    },
)

print(response)
