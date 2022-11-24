import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.queue import QueueClient
import uuid
import json


blobCnnString = 'DefaultEndpointsProtocol=https;AccountName=rossgartland;AccountKey=teSnaZ/VrtRUm+ENzTDsOoTrH+XbXy8DYkm3Iyoq4DV8tNlZqnpGxhvJY0EZD2SQCfoFKK8Jnboa+AStRU8dlA==;EndpointSuffix=core.windows.net'
cosmosEndpoint = 'https://rossgartlandcosmos.documents.azure.com:443/'
cosmosKey = 'dFfKP7CY0mO9DEONIEV3wuWOYYULjpQC75crxAtcgOQQ0kLMyBDV3bA4jk0TmOGAtrz5dHwqXwYAACDb7EAxSQ=='
cosmos = CosmosClient(cosmosEndpoint, cosmosKey)
partition_key = PartitionKey(path='/id')
storageCNNString = 'DefaultEndpointsProtocol=https;AccountName=rossgartland;AccountKey=teSnaZ/VrtRUm+ENzTDsOoTrH+XbXy8DYkm3Iyoq4DV8tNlZqnpGxhvJY0EZD2SQCfoFKK8Jnboa+AStRU8dlA==;EndpointSuffix=core.windows.net'

db = cosmos.create_database_if_not_exists(id='a2-video-streaming')

cosmosContainer = db.create_container_if_not_exists(
    id='videos',
    partition_key=partition_key,
    offer_throughput=400
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Initialize the queue
    queueName = 'queue-upload-videos-' + str(uuid.uuid4())
    queue = QueueClient.from_connection_string(storageCNNString, queueName)
    queue.create_queue()

    videoId = uuid.uuid4().hex

    blob = BlobClient.from_connection_string(
        conn_str=blobCnnString, container_name="videos", blob_name=videoId)

    video = req.files["video"]
    filestream = video.stream
    filestream.seek(0)

    blob.upload_blob(filestream.read(), blob_type="BlockBlob")
    blobUrl = blob.url

    if blob.url is None:
        return func.HttpResponse("unable to create video try again", status_code=409)

    videoData = {
        'filePath': blobUrl,
        'id': videoId,
        'videoTitle': req.form["videoTitle"],
        'description': req.form["description"],
        'publisher': req.form["publisher"],
        'producer': req.form["producer"],
        'genre': req.form["genre"],
        'age': req.form["age"],
        'comments': []
    }

    queue.send_message("Video has been uploaded successfully.")

    cosmosContainer.create_item(videoData)

    message = queue.receive_message()

    return func.HttpResponse(json.dumps(message.content), mimetype="multipart/form-data", status_code=201)
