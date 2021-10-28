from flask import Flask,render_template,request
import requests
import time
import os
import json
import logging
from datetime import datetime
app = Flask(__name__)

@app.route('/', methods=['GET'])
def summary():
    return render_template('summary.html')

@app.route('/', methods=['POST'])
def initiateETLAndMLPipeline():
    logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('Pipeline Initiated')
    ##Obtain function parameters from request
    try: 
        request_json = request.get_json()
    except ValueError as e:
        logging.info('Error decoding JSON:' + e)
        return "JSON Error", 400
    parameterFilePath = request_json['parameterFilePath']
    parameterFileName = request_json['parameterFileName']
    dataFile = request_json['dataFile']
    dataFileCountLimit = int(request_json['dataFileCountLimit'])
    ## Determine data file count to initiate Fusion Pipeline, if greater than specified count
    DATA_FILE_COUNT = os.popen(
            'sudo gsutil ls ' + dataFile + '|wc -l').read().strip()
    logging.info('Data File Count:' + DATA_FILE_COUNT)
    if int(DATA_FILE_COUNT) >= dataFileCountLimit:
        ## Set environment variables
        AUTH_TOKEN = os.popen('gcloud auth print-access-token').read().strip()
        PARAMETER_FILE_PATH = parameterFilePath + "/parameters.json"
        PARAMETER_FILE_COUNT = os.popen(
            'sudo gsutil ls ' + PARAMETER_FILE_PATH + '|wc -l').read().strip()
        ##Remove existing fusion pipeline parameter file as it will be generated new with every run
        if int(PARAMETER_FILE_COUNT) > 0:
            os.popen('sudo gsutil rm ' + PARAMETER_FILE_PATH).read().strip()
        ##Read re-usable parameter values obtained from Cloud storage file used to perform rest of the function
        os.popen('sudo gsutil -m cp -r ' + parameterFilePath + '/*.json .').read().strip()
        DATA = json.load(open(parameterFileName, 'rb'))
        REGION = DATA["REGION"]
        DATAPROC_LOGS = DATA["DATAPROC_LOGS"]
        MACHINE_TYPE = DATA["MACHINE_TYPE"]
        ZONE = DATA["ZONE"]
        BOOT_DISK_TYPE = DATA["BOOT_DISK_TYPE"]
        BOOT_DISK_SIZE = DATA["BOOT_DISK_SIZE"]
        NUMBER_OF_WORKERS = DATA["NUMBER_OF_WORKERS"]
        IMAGE_VERSION = DATA["IMAGE_VERSION"]
        SERVICE_ACCOUNT = DATA["SERVICE_ACCOUNT"]
        MAX_IDLE_TIME = DATA["MAX_IDLE_TIME"]
        PROJECT = DATA["PROJECT"]
        FUSION_INSTANCE_NAME = DATA["FUSION_INSTANCE_NAME"]
        FUSION_INSTANCE_URL = DATA["FUSION_INSTANCE_URL"] + \
            PROJECT + '/locations/' + REGION
        FUSION_INSTANCE_CREATION_ENDPOINT = FUSION_INSTANCE_URL + \
            '/instances?instanceId=' + FUSION_INSTANCE_NAME
        FUSION_INSTANCE_ENDPOINT = FUSION_INSTANCE_URL + \
            '/instances/' + FUSION_INSTANCE_NAME
        FUSION_PAYLOAD = json.dumps(DATA["FUSION_PAYLOAD"])
        DATAPROC_PROFILE_NAME = DATA["DATAPROC_CLUSTER_NAME"]
        DATAPROC_PROFILE_JSON = open(
            DATA["DATAPROC_PROFILE_FILE"], 'rb').read()
        PIPELINE_JSON = open(DATA["PIPELINE_FILE"], 'rb').read()
        PIPELINE_NAME = DATA["PIPELINE_NAME"]
        PREFERENCE_JSON = json.dumps(DATA["PREFERENCE_JSON"])
        HEADER = {"Content-Type": "application/json",
                "Authorization": "Bearer " + AUTH_TOKEN}
        NAMESPACE = DATA["NAMESPACE"]
        BIGQUERY_CONNECTOR = DATA["BIGQUERY_CONNECTOR"]
        SPARK_BIGQUERY_CONNECTOR = DATA["SPARK_BIGQUERY_CONNECTOR"]
        REMOTE_EXECUTION_FILE_PATH = DATA["REMOTE_EXECUTION_FILE_PATH"]
        METADATA_PARAMETER_1 = DATA["METADATA_PARAMETER_1"]
        USER_NAME = DATA["USER_NAME"]
        METADATA_PARAMETER_2 = DATA["METADATA_PARAMETER_2"]
        KEY_SAVE_PATH = DATA["KEY_SAVE_PATH"]
        METADATA_PARAMETER_3 = DATA["METADATA_PARAMETER_3"]
        METADATA_PARAMETER_4 = DATA["METADATA_PARAMETER_4"]
        DATA_DESTINATION_PATH = DATA["DATA_DESTINATION_PATH"]
        METADATA_PARAMETER_5 = DATA["METADATA_PARAMETER_5"]
        DATA_ARCHIVE_PATH = DATA["DATA_ARCHIVE_PATH"]
        METADATA_PARAMETER_6 = DATA["METADATA_PARAMETER_6"]
        PIPELINE_INPUT_PATH = DATA["PIPELINE_INPUT_PATH"]
        PIPELINE_TRANSFORM_ERROR_PATH = DATA["PIPELINE_TRANSFORM_ERROR_PATH"]
        PIPELINE_BIGQUERY_DATASET = DATA["PIPELINE_BIGQUERY_DATASET"]
        PIPELINE_BIGQUERY_STAGING_TABLE = DATA["PIPELINE_BIGQUERY_STAGING_TABLE"]
        PIPELINE_BIGQUERY_DATA_LOCATION = DATA["PIPELINE_BIGQUERY_DATA_LOCATION"]
        PIPELINE_BIGQUERY_UPDATE_SCRIPT = DATA["PIPELINE_BIGQUERY_UPDATE_SCRIPT"]
        PIPELINE_REMOTE_COMMAND = DATA["PIPELINE_REMOTE_COMMAND"] 
        PIPELINE_BIGQUERY_TRANSFORMATION = DATA["PIPELINE_BIGQUERY_TRANSFORMATION"]
        PIPELINE_MODEL_EVALUATE = DATA["PIPELINE_MODEL_EVALUATE"]   
        ## Create Dataproc cluster if not already running
        CLUSTER_STATE = os.popen('gcloud dataproc clusters describe ' + DATAPROC_PROFILE_NAME + ' --project ' + PROJECT + ' --region ' + REGION +
                                    ' --format "value(status.state)"').read().strip()
        if (CLUSTER_STATE != 'RUNNING') and (CLUSTER_STATE != 'ERROR'):
        ## Fetch Host, Private Key of specific user from Dataproc Master VM for Data Fusion based remote execution plugin
            os.popen('gcloud beta dataproc clusters create ' + DATAPROC_PROFILE_NAME + ' --bucket ' + DATAPROC_LOGS +
                        ' --region ' + REGION + ' --zone ' + ZONE + ' --master-machine-type ' + MACHINE_TYPE + ' --master-boot-disk-type ' + BOOT_DISK_TYPE +
                        ' --master-boot-disk-size ' + BOOT_DISK_SIZE + ' --num-workers ' + NUMBER_OF_WORKERS + ' --worker-machine-type ' + MACHINE_TYPE +
                        ' --worker-boot-disk-type ' + BOOT_DISK_TYPE + ' --worker-boot-disk-size ' + BOOT_DISK_SIZE + ' --image-version ' + IMAGE_VERSION + ' --service-account ' +
                        SERVICE_ACCOUNT + ' --max-idle ' + MAX_IDLE_TIME + ' --project ' + PROJECT + 
                        ' --initialization-actions gs://clusterstartupscripts/startup_script.sh,gs://goog-dataproc-initialization-actions-us-east1/connectors/connectors.sh' +
                        ' --metadata bigquery-connector-version=' + BIGQUERY_CONNECTOR +' --metadata spark-bigquery-connector-version=' + 
                        SPARK_BIGQUERY_CONNECTOR +' --metadata='+ METADATA_PARAMETER_1 + '=' + REMOTE_EXECUTION_FILE_PATH
                                                 +','+ METADATA_PARAMETER_2 + '=' + USER_NAME
                                                 +','+ METADATA_PARAMETER_3 + '=' + KEY_SAVE_PATH
                                                 +','+ METADATA_PARAMETER_4 + '=' + dataFile
                                                 +','+ METADATA_PARAMETER_5 + '=' + DATA_DESTINATION_PATH
                                                 +','+ METADATA_PARAMETER_6 + '=' + DATA_ARCHIVE_PATH).read().strip()
            CLUSTER_STATE = os.popen('gcloud dataproc clusters describe ' + DATAPROC_PROFILE_NAME + ' --project ' + PROJECT + ' --region ' + REGION +
                                        ' --format "value(status.state)"').read().strip()
        if CLUSTER_STATE == 'RUNNING':
            INSTANCE_NAME = os.popen('gcloud dataproc clusters describe ' + DATAPROC_PROFILE_NAME + ' --project ' + PROJECT + ' --region ' + REGION +
                                        ' --format "value(config.masterConfig.instanceNames)"').read().strip()
            HOST = os.popen('gcloud compute instances describe ' +  INSTANCE_NAME + ' --project ' + PROJECT + ' --zone ' + ZONE + 
            ' --flatten="networkInterfaces" --format "value(networkInterfaces.accessConfigs.natIP)"').read().strip()
            os.popen('sudo gsutil cp ' + KEY_SAVE_PATH + '/remote* .').read().strip()
            val1=open('./remoteKey', 'r')
            PRIVATE_KEY=val1.read()
            ##Format and add the public key to Data proc instance metadata for external systems to access the instance remotely            
            val2=open('./remoteKey.pub', 'r')
            PUBLIC_KEY=val2.read()
            pubkey = open("remotepubkey.txt", "w")
            pubkey.write(USER_NAME + ':'+ PUBLIC_KEY)
            pubkey.close()
            os.popen('gcloud compute instances add-metadata '+ INSTANCE_NAME + ' --metadata-from-file ssh-keys=./remotepubkey.txt --zone '+ ZONE).read().strip()
            os.popen('sudo rm remote*').read().strip()
            PIPELINE_ERROR_LOCATION = PIPELINE_BIGQUERY_DATA_LOCATION.lower()
            ## Generate Fusion Pipeline Parameter file and copy to Cloud storage bucket
            parameterDict={
                "arguments" : [
                    {
                    "name": "inputPath",
                    "type": "String",
                    "value": PIPELINE_INPUT_PATH
                    },
                    {
                    "name": "currentProject",
                    "type": "String",
                    "value": PROJECT
                    },
                    {
                    "name": "dataLocation",
                    "type": "String",
                    "value": PIPELINE_BIGQUERY_DATA_LOCATION
                    },
                    {
                    "name": "host",
                    "type": "String",
                    "value": HOST
                    },
                    {
                    "name": "privateKey",
                    "type": "String",
                    "value": PRIVATE_KEY
                    },
                    {
                    "name": "transformErrorPath",
                    "type": "String",
                    "value": PIPELINE_TRANSFORM_ERROR_PATH
                    },
                    {
                    "name": "errorLocation",
                    "type": "String",
                    "value": PIPELINE_ERROR_LOCATION
                    },
                    {
                    "name": "dataSet",
                    "type": "String",
                    "value": PIPELINE_BIGQUERY_DATASET
                    },
                    {
                    "name": "destinationTable",
                    "type": "String",
                    "value": PIPELINE_BIGQUERY_STAGING_TABLE
                    },
                    {
                    "name": "bqUpdateScript",
                    "type": "String",
                    "value": PIPELINE_BIGQUERY_UPDATE_SCRIPT
                    },
                    {
                    "name": "userName",
                    "type": "String",
                    "value": USER_NAME
                    },
                    {
                    "name": "command",
                    "type": "String",
                    "value": PIPELINE_REMOTE_COMMAND
                    },
                    {
                    "name": "modelEvaluate",
                    "type": "String",
                    "value": PIPELINE_MODEL_EVALUATE
                    },
                    {
                    "name": "bqTransformScript",
                    "type": "String",
                    "value": PIPELINE_BIGQUERY_TRANSFORMATION
                    }                    
                ]
                }
            with open("parameters.json", "w") as jsonFile:
                json.dump(parameterDict, jsonFile, indent=4)

            os.popen('sudo gsutil cp parameters.json ' + parameterFilePath).read().strip()
            os.popen('sudo rm parameters.json').read().strip()
            ## Create a new Data Fusion Instance if not already running
            response = requests.get(FUSION_INSTANCE_ENDPOINT, headers=HEADER)
            if response.status_code == 200:
                create_instance_response = response.json()
                INSTANCE_STATE = create_instance_response['state']
                INSTANCE_API_ENDPOINT = create_instance_response['apiEndpoint']
            else:
                INSTANCE_STATE = 'NOT EXISTING'
            if INSTANCE_STATE != 'RUNNING':
                response = requests.post(
                        FUSION_INSTANCE_CREATION_ENDPOINT, data=FUSION_PAYLOAD, headers=HEADER)
                logging.info('Fusion Creation Response:'+ response)
                instance_creation_time = 0
                while True:
                    ## Poll for instance creation state until instance is up and running
                    try:
                        logging.info('Instance Creation Response:' + INSTANCE_STATE)
                        if (INSTANCE_STATE == 'RUNNING' or INSTANCE_STATE == 'FAILED'):
                            INSTANCE_API_ENDPOINT = create_instance_response['apiEndpoint']
                            break
                        else:
                            instance_creation_time += 300
                            if instance_creation_time < 1200:
                                time.sleep(instance_creation_time)
                                response = requests.get(
                                        FUSION_INSTANCE_ENDPOINT, headers=HEADER)
                                create_instance_response = response.json()
                                INSTANCE_STATE = create_instance_response['state']
                            else:
                                break
                    except Exception as e:
                        logging.info('Instance creation error:' + e)
                        break
            if INSTANCE_STATE == 'RUNNING':
                ## Get all Dataproc profiles

                #response = requests.get(INSTANCE_API_ENDPOINT + "/v3/namespaces//" + NAMESPACE + "/profiles?includeSystem=true",
                #                        headers=HEADER)
                #dataproc_profile = response.json()
                #print(dataproc_profile[0]['name'], len(dataproc_profile))

                ## Create/update Existing Dataproc profile
                INSTANCE_API_ENDPOINT = INSTANCE_API_ENDPOINT + "/v3/namespaces/" + NAMESPACE
                PROFILE_API = INSTANCE_API_ENDPOINT + "/profiles/" + DATAPROC_PROFILE_NAME
                #print(PROFILE_API)
                response = requests.put(PROFILE_API,
                                            data=DATAPROC_PROFILE_JSON,
                                            headers=HEADER)
                logging.info('Dataproc profile creation response:'+ response.text)
                ## Update profile preferences for namespace so created dataproc cluster is used by default for every pipeline execution
                PREFERENCE_API = INSTANCE_API_ENDPOINT + "/preferences"
                response = requests.put(PREFERENCE_API,
                                            data=PREFERENCE_JSON,
                                            headers=HEADER)
                ## Deploy Pipeline if not already deployed
                DEPLOY_PIPELINE_API = INSTANCE_API_ENDPOINT + "/apps/" + PIPELINE_NAME
                logging.info('Existing fusion pipeline deployment API:' + DEPLOY_PIPELINE_API)
                response = requests.get(DEPLOY_PIPELINE_API,
                                            headers=HEADER)
                if response.status_code != 200:
                    response = requests.put(DEPLOY_PIPELINE_API,
                                                data=PIPELINE_JSON,
                                                headers=HEADER)
                ## Start the deployed pipeline by passing the parameters generated in the function and stored in Cloud Storage - parameters.json
                PIPELINE_RUNTIME_PARAMETER_DICT = {"parameterPath": PARAMETER_FILE_PATH}
                PIPELINE_RUNTIME_PARAMETERS = json.dumps(PIPELINE_RUNTIME_PARAMETER_DICT)                
                START_PIPELINE_API = DEPLOY_PIPELINE_API + "/workflows/DataPipelineWorkflow/start"
                response = requests.post(START_PIPELINE_API,
                                            data=PIPELINE_RUNTIME_PARAMETERS,
                                            headers=HEADER)
                logging.info('Fusion Pipeline start response:'+ response.status_code)
                return response.status_code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

