#!/bin/bash
cd "`dirname "$0"`"
pip install -r requirements.txt --target ./packages
if [ -d packages ]; then
	cd packages
	find . -name "*.pyc" -delete
	find . -name "*.egg-info" | xargs rm -rf
	# zip -9mrv packages.zip .
	# mv packages.zip ..
	# cd ..
	# rm -rf packages
fi
