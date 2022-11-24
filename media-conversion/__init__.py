import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.media import AzureMediaServices
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.mgmt.media.models import (
    Asset,
    Transform,
    TransformOutput,
    BuiltInStandardEncoderPreset,
    Job,
    JobInputAsset,
    JobOutputAsset)
import os
import uuid
import sys
import random

subscription_id = 'cea8c3bb-1cec-4cdf-8f2d-c579ad6a42f9'
resource_group_name = 'com682-assignment2'
account_name = 'rossgartlandmediaservice'
blobCnnString = 'DefaultEndpointsProtocol=https;AccountName=rossgartland;AccountKey=teSnaZ/VrtRUm+ENzTDsOoTrH+XbXy8DYkm3Iyoq4DV8tNlZqnpGxhvJY0EZD2SQCfoFKK8Jnboa+AStRU8dlA==;EndpointSuffix=core.windows.net'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    default_credential = DefaultAzureCredential()

    videoFile = req.files["video"]
    filestream = videoFile.stream
    filestream.seek(0)

    videoId = uuid.uuid4().hex

    uniqueness = random.randint(0, 9999)

    # Create input asset attributes
    in_asset_name = 'inputassetName' + str(uniqueness)
    in_alternate_id = 'inputALTid' + str(uniqueness)
    in_description = 'inputdescription' + str(uniqueness)

    input_asset = Asset(alternate_id=in_alternate_id,
                        description=in_description)

    # Create output asset attributes
    out_asset_name = 'outputassetName' + str(uniqueness)
    out_alternate_id = 'outputALTid' + str(uniqueness)
    out_description = 'outputdescription' + str(uniqueness)
    output_asset = Asset(alternate_id=out_alternate_id,
                         description=out_description)

    output_asset = Asset(alternate_id=out_alternate_id,
                         description=out_description)

    # Create AMS client
    client = AzureMediaServices(default_credential, subscription_id)

    # Create input asset
    inputAsset = client.assets.create_or_update(
        resource_group_name, account_name, in_asset_name, input_asset)

    in_container = 'asset-' + inputAsset.asset_id

    # Create output asset
    outputAsset = client.assets.create_or_update(
        resource_group_name, account_name, out_asset_name, output_asset)

    # Create blob storage client
    blob_service_client = BlobServiceClient.from_connection_string(
        blobCnnString)

    blob_client = blob_service_client.get_blob_client(in_container, videoFile)

    blob_client.upload_blob(filestream.read(), blob_type="BlockBlob")

    # Create transform
    transform_name = 'MyTrans' + str(uniqueness)
    transform_output = TransformOutput(
        preset=BuiltInStandardEncoderPreset(preset_name="AdaptiveStreaming"))

    transform = Transform()
    transform.outputs = [transform_output]

    transform = client.transforms.create_or_update(
        resource_group_name=resource_group_name,
        account_name=account_name,
        transform_name=transform_name,
        parameters=transform)

    # Create job
    job_name = 'MyJob' + str(uniqueness)
    files = (videoFile)
    input = JobInputAsset(asset_name=in_asset_name)
    outputs = JobOutputAsset(asset_name=out_asset_name)
    theJob = Job(input=input, outputs=[outputs])
    job: Job = client.jobs.create(
        resource_group_name, account_name, transform_name, job_name, parameters=theJob)

    job_state = client.jobs.get(
        resource_group_name, account_name, transform_name, job_name)

    return func.HttpResponse("Video encoded", mimetype="multipart/form-data", status_code=200)
