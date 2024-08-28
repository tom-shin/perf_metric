import boto3
import os
import json

CHAT_FUNCTION_NAME = os.getenv("CHAT_FUNCTION_NAME")


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