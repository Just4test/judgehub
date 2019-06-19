CFN_STACK_NAME ?= judgehub
CFN_PACKAGE_S3_BUCKET_NAME ?= cfnpackagetemp

S3_FILES_DIR := src/s3
S3_FILES_MONACO_DIR := $(S3_FILES_DIR)/static/problems/.monaco-editor
S3_BUCKET_NAME ?= judgehub

MONACO_VERSION := $(shell npm info monaco-editor version)
MONACO_URL := $(shell npm info monaco-editor dist.tarball)

VPC_JUDGE_CIDR_BLOCK ?= 10.96.0.0/16

.PHONY: s3sync
s3sync:
	if [ ! -d $(S3_FILES_MONACO_DIR) ]; then \
		mkdir -p $(S3_FILES_MONACO_DIR).temp; \
		echo Download monaco-editor...; \
		echo Download $(MONACO_VERSION) from $(MONACO_URL); \
		curl $(MONACO_URL) | tar xvz --strip 1 -C $(S3_FILES_MONACO_DIR).temp package/min; \
		mv $(S3_FILES_MONACO_DIR).temp $(S3_FILES_MONACO_DIR); \
	fi
	aws s3 sync $(S3_FILES_DIR) s3://$(S3_BUCKET_NAME) --delete --exclude "*.DS_Store"

.PHONY: package
package: 
	cd src; \
	dep2layer download; \
	sam package --template-file .dep2layer-template.yaml --output-template-file .packaged-template.yaml --s3-bucket $(CFN_PACKAGE_S3_BUCKET_NAME)

.PHONY: deploy
deploy:
	cd src; \
	aws cloudformation deploy --template-file .packaged-template.yaml  --capabilities CAPABILITY_IAM --stack-name $(CFN_STACK_NAME) --parameter-overrides UseCurrentS3Bucket=$(S3_BUCKET_NAME) JudgeVpcCidrBlock=$(VPC_JUDGE_CIDR_BLOCK)