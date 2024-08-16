import boto3
import json
# from tqdm import tqdm
# from lib.data_loader import DataLoader

CHAT_FUNCTION_NAME = "dev-lambda-chat"
CHUNK_FUNCTION_NAME = "dev-lambda-chunk"
EMBED_FUNCTION_NAME = "dev-lambda-embed"
DEL_FUNCTION_NAME = "dev-lambda-del"


class LambdaInvokeManager:
    def __init__(self):
        self.client = boto3.client('lambda')
    
    # def generate_evalset(self, testset_dir, evalset_dir = "./test/evalset.json"):
    #     testset = DataLoader.load_json(testset_dir)
    #     evalset = []
    #     for test in tqdm(testset, desc="Generating Evalset"):
    #         context, response = self.invoke_chat(test["question"])
    #         test.update({"contexts":context, "answer":response})
            
    #         evalset.append(test)
            
    #     DataLoader.dump_json(evalset, evalset_dir)
    #     return evalset_dir


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