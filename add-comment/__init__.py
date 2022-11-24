import logging

import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
from azure.storage.queue import QueueClient
import uuid
import json
import datetime

blobCnnString = 'DefaultEndpointsProtocol=https;AccountName=rossgartland;AccountKey=teSnaZ/VrtRUm+ENzTDsOoTrH+XbXy8DYkm3Iyoq4DV8tNlZqnpGxhvJY0EZD2SQCfoFKK8Jnboa+AStRU8dlA==;EndpointSuffix=core.windows.net'
cosmosEndpoint = 'https://rossgartlandcosmos.documents.azure.com:443/'
cosmosKey = 'dFfKP7CY0mO9DEONIEV3wuWOYYULjpQC75crxAtcgOQQ0kLMyBDV3bA4jk0TmOGAtrz5dHwqXwYAACDb7EAxSQ=='
cosmos = CosmosClient(cosmosEndpoint, cosmosKey)
partition_key = PartitionKey(path='/id')

storageCNNString = 'DefaultEndpointsProtocol=https;AccountName=rossgartland;AccountKey=teSnaZ/VrtRUm+ENzTDsOoTrH+XbXy8DYkm3Iyoq4DV8tNlZqnpGxhvJY0EZD2SQCfoFKK8Jnboa+AStRU8dlA==;EndpointSuffix=core.windows.net'

db = cosmos.create_database_if_not_exists(id='a2-video-streaming')

cosmosContainer = db.create_container_if_not_exists(
    id='comments',
    partition_key=partition_key,
    offer_throughput=400
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Initialize the queue.
    queueName = 'queue-comment-' + str(uuid.uuid4())
    queue = QueueClient.from_connection_string(storageCNNString, queueName)
    queue.create_queue()

    # Request values for comment.
    videoID = req.route_params.get("videoID")
    commentID = uuid.uuid4().hex
    userID = req.form["userID"]
    username = req.form["username"]
    commentData = req.form["commentData"]
    sentDate = datetime.datetime.utcnow().isoformat()

    # Create comment object.
    comment = {
        'id': commentID,
        'videoID': videoID,
        'userID': userID,
        'username': username,
        'commentData': commentData,
        'sentDate': sentDate
    }

    queue.send_message("Comment added successfully.")

    # Insert into comment container.
    cosmosContainer.create_item(comment)

    message = queue.receive_message()

    return func.HttpResponse(message.content, mimetype="multipart/form-data", status_code=201)
