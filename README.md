Management Microservice (AWS Serverless, CDK)

A production-style serverless task management microservice built on AWS using API Gateway, Lambda, DynamoDB, and AWS CDK (Python).

This project demonstrates end-to-end backend design, secure API access, Infrastructure as Code, and a clean migration from AWS Console prototyping to a fully reproducible CDK deployment.

🧠 Project Overview

The service exposes a REST API for managing tasks with full CRUD functionality:

Create tasks

List tasks

Retrieve a task by ID

Update task status/details

Delete tasks

Security is enforced via a custom Lambda Token Authorizer.
All infrastructure is defined using AWS CDK (Python).

🏗 Architecture

AWS Services Used

API Gateway (REST API)

AWS Lambda

Task service Lambda

Custom token authorizer Lambda

Amazon DynamoDB

AWS CDK (Python)

CloudWatch Logs

High-level flow:

Client sends HTTP request

API Gateway invokes Lambda Authorizer

Authorizer validates token

API Gateway routes request to service Lambda

Lambda performs DynamoDB operation

Response returned to client

🔐 Authentication Model

This project uses a custom token-based Lambda Authorizer.

Token is sent via the Authorization header

Token value is validated against an environment variable

Requests without a valid token are denied

⚠️ This is intentional to demonstrate how API Gateway authorizers work internally.
In production, this could be replaced with JWT / Cognito / OAuth.

🧱 Infrastructure as Code (CDK)

All infrastructure is defined using AWS CDK (Python):

API Gateway routes and methods

Lambda functions and permissions

DynamoDB table

Environment variables

IAM roles and policies

This ensures:

Repeatable deployments

Easy teardown (cdk destroy)

No manual console configuration required

🚀 Deployment

Prerequisites

AWS CLI configured

AWS CDK installed

Python 3.10+

1️⃣ Install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

2️⃣ Bootstrap CDK (one-time per account/region)
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>

3️⃣ Deploy
cdk deploy


After deployment, CDK outputs the API endpoint URL.

🧪 API Usage Examples
Environment variables (example)
$BASE_URL = "https://<api-id>.execute-api.<region>.amazonaws.com/dev"
$AUTH = "my-super-secret-token"

➕ Create Task
$body = @{
  title = "First task"
  description = "Created via API"
  status = "PENDING"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method POST `
  -Uri "$BASE_URL/tasks" `
  -Headers @{ Authorization = $AUTH } `
  -ContentType "application/json" `
  -Body $body

📋 List Tasks
Invoke-RestMethod `
  -Method GET `
  -Uri "$BASE_URL/tasks" `
  -Headers @{ Authorization = $AUTH }

🔍 Get Task by ID
Invoke-RestMethod `
  -Method GET `
  -Uri "$BASE_URL/tasks/{taskId}" `
  -Headers @{ Authorization = $AUTH }

✏️ Update Task
$update = @{
  status = "IN_PROGRESS"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method PUT `
  -Uri "$BASE_URL/tasks/{taskId}" `
  -Headers @{ Authorization = $AUTH } `
  -ContentType "application/json" `
  -Body $update

🗑 Delete Task
Invoke-RestMethod `
  -Method DELETE `
  -Uri "$BASE_URL/tasks/{taskId}" `
  -Headers @{ Authorization = $AUTH }

🧹 Cleanup (Cost Control)

To avoid AWS charges:

cdk destroy


This removes all deployed resources.

🧭 Design Decisions

Started with AWS Console prototyping to validate architecture quickly

Migrated to CDK for repeatability and best practices

Used custom authorizer to demonstrate deep API Gateway understanding

Chose DynamoDB for low-latency, serverless persistence

Explicit CORS handling for real-world API usage

🚧 Future Improvements

JWT-based authentication (Cognito / OAuth)

OpenAPI specification

Pagination & filtering

CI/CD pipeline (GitHub Actions)

Structured logging & tracing

Unit & integration tests

📌 Why This Project Matters

This repository demonstrates:

Serverless backend architecture

Secure API design

Infrastructure as Code

AWS best practices

Cost awareness

Migration from manual setup to automated deployment

This is not a tutorial clone — it reflects real engineering decisions and trade-offs.

👤 Author

Daryoush
Cloud / Backend Engineering Portfolio Project
