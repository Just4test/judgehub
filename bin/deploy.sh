aws s3 sync ./static s3://${S3_BUCKET_NAME}
sam package --template-file template.yaml --output-template-file .packaged-template.yaml --s3-bucket ${S3_BUCKET_NAME}
echo ==============
aws cloudformation deploy --template-file .packaged-template.yaml  --capabilities CAPABILITY_IAM --stack-name ${1} --parameter-overrides UseCurrentS3Bucket=${S3_BUCKET_NAME} EnvCidrBlock=10.99.0.0/16
echo -en "\a"