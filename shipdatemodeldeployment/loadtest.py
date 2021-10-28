from locust import task, between
from locust.contrib.fasthttp import FastHttpUser
import json

class shipdateapi(FastHttpUser):
    wait_time = between(1,2)

    @task
    def getprediction(self):
        payload = {"instances":[ {
            "ORG_ID": "TestOrg",
            "ORDER_TYPE_ID": "WEB-US",
            "ORDER_LINE_QUANTITY": "1.0",
            "IS_GIFT": "0",
            "DELIVERY_METHOD_ID": "ShipToAddress",
            "ORDER_CREATE_TO_ALLOCATION_IN_HOURS": "1.0",
            "SERVICE_LEVEL": "PROSHIP,GROUND",
            "SOURCE_LOCATION": "1234-DC",
            "SOURCE_STATE": "TX",
            "SOURCE_COUNTRY": "US",
            "SOURCE_LATITUDE": "32.97335",
            "SOURCE_LONGITUDE": "-97.329507",
            "ORDER_CREATE_TO_RELEASE_IN_HOURS": "1.0",
            "CREATION_DAY_OF_WEEK": "7",
            "CREATION_YEAR_WEEK": "2021-22",
            "CREATION_MONTH": "6",
            "CREATION_HOUR": "19",
            "CURRENT_BACKLOG": "5.0",
            "TOTAL_CAPACITY_UTILIZED": "196.0",
            "SEVEN_DAY_AVERAGE_CAPACITY": "155.0",
            "SEVEN_DAY_MAX_CAPACITY": "409.0",
            "SEVEN_DAY_AVERAGE_BACKLOG": "78.0",
            "SEVEN_DAY_MAX_BACKLOG": "211.0"
        } ] }
        header = {'Content-Type':'application/json','Accept':'application/json'}
        self.client.post("/predict",data=json.dumps(payload),headers=header,catch_response=False)
  

