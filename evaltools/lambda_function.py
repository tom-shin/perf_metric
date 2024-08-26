from evaltools import utils


TESTSET_ACTION = "create_testset"
EVALSET_ACTION = "create_evalset"
EVALUATE_ACTION = "evaluate"

ALLOWED_ACTIONS = [TESTSET_ACTION, EVALSET_ACTION, EVALUATE_ACTION]

def handler(event, context):
    action = event.get("action")
    if not action in ALLOWED_ACTIONS:
        return {
            "statusCode": 400,
            "body": f"This Lambda function only allows: {ALLOWED_ACTIONS}"
        }

    body = event.get("body")
    if not body:
        return {
            "statusCode": 400,
            "body": f"\"body\" is necessary"
        }
    
    payload = {
        "statusCode": 200
    }



    if action == TESTSET_ACTION:
        n = event.get("n", 10)
        payload["body"] = utils.generate_testset(body, n)
        return payload
    
    if action == EVALSET_ACTION:
        payload["body"] = utils.generate_evalset(body)
        return payload
    
    if action == EVALUATE_ACTION:
        payload["body"] = utils.evaluate(body)
        return payload

