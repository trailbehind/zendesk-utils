import sys

import localize.project_settings as settings
from helpcenter_to_pdf.ZendeskPDFMaker import ZendeskPDFMaker


def print_usage():
    print("\nparameters are: create, post, ping_slack, run\n")


zdpm = ZendeskPDFMaker()
if len(sys.argv) < 2:
    print_usage()
    sys.exit(2)

if sys.argv[1] == "create":
    zdpm.create_pdfs()
elif sys.argv[1] == "post":
    zdpm.post_pdfs_to_s3()
elif sys.argv[1] == "ping_slack":
    zdpm.ping_slack()
elif sys.argv[1] == "run":
    zdpm.create_pdfs()
    zdpm.post_pdfs_to_s3()
    if settings.SLACK_NOTIFICATION_URL:
        zdpm.ping_slack()
else:
    print_usage()


# # AWS IAM Role

# # create an STS client object that represents a live connection to the
# # STS service
# sts_client = boto3.client('sts')

# # Call the assume_role method of the STSConnection object and pass the role
# # ARN and a role session name.
# assumed_role_object=sts_client.assume_role(
#     RoleArn="arn:aws:iam::account-of-role-to-assume:role/name-of-role",
#     RoleSessionName="AssumeRoleSession1"
# )

# # From the response that contains the assumed role, get the temporary
# # credentials that can be used to make subsequent API calls
# credentials=assumed_role_object['Credentials']

# # Use the temporary credentials that AssumeRole returns to make a
# # connection to Amazon S3
# s3_resource=boto3.resource(
#     's3',
#     aws_access_key_id=credentials['AccessKeyId'],
#     aws_secret_access_key=credentials['SecretAccessKey'],
#     aws_session_token=credentials['SessionToken'],
# )

# # Use the Amazon S3 resource object that is now configured with the
# # credentials to access your S3 buckets.
# for bucket in s3_resource.buckets.all():
#     print(bucket.name)
