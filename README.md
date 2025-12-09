🧩 Management Microservice — Serverless API
📌 Overview

A fully serverless backend built with AWS Lambda, API Gateway, and DynamoDB, deployed using the AWS CDK (Python).
The microservice exposes CRUD endpoints for managing items, with a custom Lambda authorizer.

🚀 Features & Endpoints
Method	Endpoint	Description
POST	/tasks	Create a new task
GET	/tasks	List all tasks
GET	/tasks/{id}	Get a single task
PUT	/tasks/{id}	Update a task
DELETE	/tasks/{id}	Delete a task

Authorization: Custom Lambda Authorizer (token-based).
DynamoDB Table: TasksTable

🏗 Architecture

API Gateway REST API

Lambda Functions

CRUD handler

Custom authorizer

DynamoDB table (PK: taskId)

IAM permissions (least privilege)

CDK (Python) deployment infrastructure

🔧 Environment Variables
TABLE_NAME=TasksTable
LOG_LEVEL=INFO

📦 Deployment (Console / CDK)
cdk synth
cdk deploy

🧪 Testing (Examples)
# Create task
curl -X POST https://your-api/tasks \
  -H "Authorization: Bearer sampletoken" \
  -d '{"title": "Test task", "description": "Example"}'