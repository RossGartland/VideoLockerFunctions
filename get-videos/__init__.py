import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
from azure.storage.blob import BlobServiceClient, BlobClient
import uuid
import json

cosmosEndpoint = 'cosmosEndpoint'
cosmosKey = 'cosmosKey'
cosmos = CosmosClient(cosmosEndpoint, cosmosKey)
partition_key = PartitionKey(path='/id')


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Python HTTP trigger function processed a request.')

    db = cosmos.get_database_client('a2-video-streaming')

    container = db.get_container_client('videos')

    video_list = list(container.query_items(
        query="SELECT * FROM videos",
        enable_cross_partition_query=True
    ))

    logging.info(video_list)

    header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET,POST'
    }

    return func.HttpResponse(json.dumps(video_list), headers=header, mimetype="application/json", status_code=200)
