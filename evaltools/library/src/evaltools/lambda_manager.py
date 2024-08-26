import boto3
import os
import json

CHAT_FUNCTION_NAME = os.getenv("CHAT_FUNCTION_NAME")
CHUNK_FUNCTION_NAME = os.getenv("CHUNK_FUNCTION_NAME")
EMBED_FUNCTION_NAME = os.getenv("EMBED_FUNCTION_NAME")
DEL_FUNCTION_NAME = os.getenv("DEL_FUNCTION_NAME")


class LambdaManager:
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
        
        body = json.loads(response['Payload'].read())["body"]
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

        return json.loads(response['Payload'].read())["body"]
    

    def invoke_embed(self, chunk_list):
        event = chunk_list
        payload = json.dumps(event)

        response = self.client.invoke(
            FunctionName = EMBED_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=payload
        )

        return json.loads(response['Payload'].read())["statusCode"] == 200
    

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

        return json.loads(response['Payload'].read())['statusCode'] == 200