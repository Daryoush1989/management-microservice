import os

EXPECTED_API_KEY = os.environ.get("EXPECTED_API_KEY", "")


def lambda_handler(event, context):
    """
    Lambda authorizer for API Gateway REST API (TOKEN type).
    Expects the token in the 'authorizationToken' field (e.g. header 'x-api-key').
    """
    # For REQUEST/TOKEN type, event structure includes these:
    token = event.get("authorizationToken")
    method_arn = event.get("methodArn")

    if not token or token != EXPECTED_API_KEY:
        return generate_policy("unauthorized", "Deny", method_arn)

    # In real life, 'principalId' might be a user id.
    return generate_policy("authorized-user", "Allow", method_arn)


def generate_policy(principal_id, effect, resource):
    auth_response = {"principalId": principal_id}

    if effect and resource:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource
                }
            ]
        }
        auth_response["policyDocument"] = policy_document

    # You can also add 'context' with extra info for the backend Lambda if needed
    return auth_response

