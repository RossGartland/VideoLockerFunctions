This service is no longer live.

To replicate this in your own environment please set the following configuration. 
Ideally you would use envronment vairables rather than declare these literally.

Located throughout _init_.py file.
blobCnnString = 'blobCnnString'
cosmosEndpoint = 'cosmosEndpoint'
cosmosKey = 'cosmosKey'
subscription_id = 'subscription_id'
resource_group_name = 'resource_group_name'
storageCNNString = 'storageCNNString'

Located in secrets.py:
config = dict(
    USERNAME='USERNAME',
    PASSWORD='PASSWORD',
    SECRET_KEY='my_secret'
)
