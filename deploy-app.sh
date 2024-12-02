#!/bin/bash

# Check if the required arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: package.sh <DATABRICKS_WORKSPACE_PATH> <LAKEHOUSE_APP_NAME> <PROFILE>"
    exit 1
fi

LAKEHOUSE_APP_NAME=$1
DATABRICKS_WORKSPACE_PATH=$2
PROFILE=$3


# build the frontend
yarn --cwd src/frontend build

# code to package the application-related files into a separate folder and then upload it to Databricks Workspace

# Create a folder to store the application-related files
rm -rf ./.build
mkdir -p ./.build

# Copy the application-related files to the folder

mkdir -p ./.build/src
rsync -av --exclude='__pycache__' ./src/terrametria ./.build/src/

# generate requirements.txt

hatch run pip freeze --exclude-editable >./.build/requirements.txt

# copy app.yml

cp app.yml ./.build/

# upload the application-related files to Databricks Workspace

databricks -p ${PROFILE} workspace import-dir --overwrite ./.build ${DATABRICKS_WORKSPACE_PATH}

echo "Deploying the app to Databricks for app name: ${LAKEHOUSE_APP_NAME} and source code path: ${DATABRICKS_WORKSPACE_PATH}"

databricks apps -p ${PROFILE} deploy ${LAKEHOUSE_APP_NAME} --source-code-path ${DATABRICKS_WORKSPACE_PATH}

echo "Successfully deployed the app to Databricks!"
