import os

EXPECTED_AUTH_TOKEN = os.environ.get("EXPECTED_AUTH_TOKEN", "")


def lambda_handler(event, context):
    token = event.get("authorizationToken")
    method_arn = event.get("methodArn")

    if not token or token != EXPECTED_AUTH_TOKEN:
        return generate_policy("unauthorized", "Deny", method_arn)

    return generate_policy("authorized-user", "Allow", method_arn)


def generate_policy(principal_id: str, effect: str, resource: str) -> dict:
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}
            ],
        },
    }
