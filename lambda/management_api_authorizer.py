import os

EXPECTED_API_KEY = os.environ.get("EXPECTED_API_KEY", "")


def lambda_handler(event, context):
    """
    Lambda TOKEN authorizer for API Gateway REST API.

    Expects the token in event["authorizationToken"].
    API Gateway will map the header (e.g. Authorization) to this field.
    """
    token = event.get("authorizationToken")
    method_arn = event.get("methodArn")

    if not token or token != EXPECTED_API_KEY:
        # In a TOKEN authorizer, returning a Deny policy will block the request
        return generate_policy("unauthorized", "Deny", method_arn)

    # In real life, principalId might be a real user id
    return generate_policy("authorized-user", "Allow", method_arn)


def generate_policy(principal_id: str, effect: str, resource: str) -> dict:
    """Generate an IAM policy response expected by API Gateway."""
    auth_response = {"principalId": principal_id}

    if effect and resource:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                }
            ],
        }
        auth_response["policyDocument"] = policy_document

    return auth_response
