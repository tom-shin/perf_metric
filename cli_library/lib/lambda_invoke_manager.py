import boto3
import json

CHAT_FUNCTION_NAME = "dev-lambda-chat"
CHUNK_FUNCTION_NAME = "dev-lambda-chunk"
EMBED_FUNCTION_NAME = "dev-lambda-embed"
DEL_FUNCTION_NAME = "dev-lambda-del"


class LambdaInvokeManager:
    def __init__(self):
        self.client = boto3.client('lambda')
    
    
    def invoke_chat(self, query):
        event = {
            "Query": query,
            "History": [],
            "debug": True
        }
        payload = json.dumps(event)

        response = self.client.invoke(
            FunctionName = CHAT_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=payload
        )
        
        body = json.loads(response['Payload'].read())
        return body.get('list', ['']), body.get('response', '')
    

    def invoke_chunk(self, bucket, key):
        event = {
            "bucket": bucket,
            "key": key
        }
        payload = json.dumps(event)

        response = self.client.invoke(
            FunctionName = CHUNK_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=payload
        )

        return json.loads(response['Payload'].read())
    

    def invoke_embed(self, chunk_list):
        event = chunk_list
        payload = json.dumps(event)

        response = self.client.invoke(
            FunctionName = EMBED_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=payload
        )

        return json.loads(response['Payload'].read())["Status"]
    

    def invoke_del(self, filter):
        event = {
            "filter": filter
        }

        payload = json.dumps(event)

        response = self.client.invoke(
            FunctionName = DEL_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=payload
        )

        return json.loads(response['Payload'].read())['statusCode']