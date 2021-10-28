#!/bin/bash
project="gcpproject1"
region="us-east1"
gcloud config set project $project
gkecluster=$(gcloud container clusters list |grep "mlgkecluster")
if [[ ! -z $gkecluster ]];
then
   gcloud container clusters get-credentials mlgkecluster --region $region --project=$project
   modelexport=""
   modelexport=$(gsutil ls gs://aiplatformmodelregistry | grep model-2425)
   if [[ -z $modelexport ]];
   then
     echo "No New Trained Model"
   else
     #gsutil -m cp -r gs://modelregistry/DeliveryDateModel .
     image="gcr.io/$project/shipdatemodelapi"
     gcloud builds submit --tag $image .
     kubectl apply -f model_serve.yaml
     kubectl expose deployment shipdatemodelpredict-dep --name=shipdatepredictmodelsvc --type=LoadBalancer --port 80 --target-port 8080
   fi
fi
##Cloud Run Deployment
# gcloud run deploy deliverydateetaapi --image gcr.io/sodium-inverter-304318/deliverydateapi --allow-unauthenticated --platform managed --region us-east1 --memory 2G