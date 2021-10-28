#!/bin/bash
project="gcpproject1"
region="us-east1"
gcloud config set project $project
gkecluster=$(gcloud container clusters list |grep "mlgkecluster")
if [[ ! -z $gkecluster ]];
then
   gcloud container clusters get-credentials mlgkecluster --region $region --project=$project
   modelexport=""
   modelexport=$(gsutil ls gs://modelregistry/ShipDateDetermination | grep saved_model)
   if [[ -z $modelexport ]];
   then
     echo "No New Trained Model"
   else
     gsutil -m cp -r gs://modelregistry/ShipDateDetermination .
     image="gcr.io/$project/shipdateapi"
     gcloud builds submit --tag $image .
     kubectl apply -f model_serve.yaml
     kubectl expose deployment shipdatepredict-dep --name=shipdatepredictsvc --type=LoadBalancer --port 80 --target-port 8080
   fi
fi
##Cloud Run Deployment
# gcloud run deploy shipdateetaapi --image gcr.io/ma-rd-devils-sren/shipdateapi --allow-unauthenticated --platform managed --region us-east1 --memory 2G