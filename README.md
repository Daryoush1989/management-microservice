🌟 Management Microservice (Serverless CRUD API on AWS)

A fully serverless task-management microservice built using:

AWS API Gateway (REST API)

AWS Lambda (Python)

DynamoDB (NoSQL + GSI)

Custom Lambda TOKEN Authorizer

IAM roles for secure, least-privilege access

This project demonstrates real-world serverless backend design, authentication, event-driven compute, and DynamoDB modeling patterns.

🚀 Features
✔ Full CRUD API
Method	Path	Description
POST	/tasks	Create a task
GET	/tasks	Get all tasks
GET	/tasks?status=PENDING	Filter tasks using the GSI
GET	/tasks/{taskId}	Get a single task
PUT	/tasks/{taskId}	Update task
DELETE	/tasks/{taskId}	Delete task
🔐 Secure API with Custom Lambda Authorizer

Every request must send:

Authorization: my-super-secret-api-key-123


The authorizer validates this value against the Lambda environment variable:

EXPECTED_API_KEY


If valid → returns an IAM Allow policy with wildcard ARN:

arn:aws:execute-api:<region>:<account-id>:<rest-api-id>/<stage>/*/*


This ensures all routes in the stage are authorized.

🗃 DynamoDB Data Model
Main Table: ManagementTasks
Field	Type	Description
taskId	String	Primary key
title	String	Required
description	String	Optional
status	String	PENDING, IN_PROGRESS, DONE
createdAt	String	ISO-8601 timestamp
updatedAt	String	ISO-8601 timestamp
Global Secondary Index (GSI): StatusIndex
Attribute	Role
status	Partition key
createdAt	Sort key

Used for filtering tasks:

GET /tasks?status=PENDING

🧱 Architecture Diagram
(Client)
   |
   | Authorization Header
   v
API Gateway (REST)
   |
   | ---> Custom Lambda Authorizer (Token validation)
   |
   | ---> Lambda Proxy Integration → CRUD Lambda
   |
   v
DynamoDB (ManagementTasks)

🧪 Testing the API
Every request requires:
Authorization: my-super-secret-api-key-123

➕ Create a Task

POST /tasks

{
  "title": "First management task",
  "description": "Set up management microservice",
  "status": "PENDING"
}

📋 Get All Tasks
GET /tasks

🔍 Filter by Status (GSI)
GET /tasks?status=PENDING

🔎 Get One Task
GET /tasks/{taskId}

✏ Update a Task

PUT /tasks/{taskId}

{
  "status": "IN_PROGRESS",
  "title": "Updated task title"
}

❌ Delete a Task
DELETE /tasks/{taskId}


Expected:

204 No Content

🧬 Lambda Functions
#### management-service-handler (CRUD Lambda)

Handles:

Create task

List tasks (optionally filtered)

GSI filtering by status

Get one task

Update partial fields

Delete task

API Gateway Proxy integration

CORS responses

Timestamp generation

Environment variables required:

TABLE_NAME = ManagementTasks
STATUS_INDEX_NAME = StatusIndex

#### management-api-authorizer (Token Authorizer)

Reads:

authorizationToken


Validates using:

EXPECTED_API_KEY


Returns IAM policy with wildcard resource:

arn:aws:execute-api:<region>:<account>/<apiId>/<stage>/*/*

🔧 Deployment Steps (with fixes applied)
1️⃣ Create DynamoDB Table

Table: ManagementTasks

Partition key: taskId

Add GSI:

PK: status

SK: createdAt

Name: StatusIndex

2️⃣ Create IAM Role for CRUD Lambda

Attach:

AWSLambdaBasicExecutionRole

AmazonDynamoDBFullAccess (simplified for demo)

3️⃣ Create CRUD Lambda

Runtime: Python 3.12

Handler: management_service_handler.lambda_handler

Env vars:

TABLE_NAME=ManagementTasks
STATUS_INDEX_NAME=StatusIndex


Deploy

4️⃣ Create Authorizer Lambda

Runtime: Python 3.12

Env vars:

EXPECTED_API_KEY=my-super-secret-api-key-123


Deploy

5️⃣ Create API Gateway REST API

Resources:

/tasks
/tasks/{taskId}


Integrations:

All endpoints → CRUD Lambda

All endpoints → require ManagementApiAuthorizer

6️⃣ Deploy to Stage dev

Your base URL becomes:

https://<rest-api-id>.execute-api.<region>.amazonaws.com/dev

📁 Project Structure
management-microservice/
│
├── lambda/
│   ├── management_service_handler.py
│   ├── management_api_authorizer.py
│
├── README.md
└── .gitignore

🔒 Security Notes

Never commit real API keys to GitHub

Use environment variables + IAM roles

Use Secrets Manager for production

CORS fully handled inside Lambda responses
