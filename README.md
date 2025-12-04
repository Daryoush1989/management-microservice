🧩 Management Microservice (Serverless CRUD API on AWS)

A fully serverless task-management backend using:

API Gateway (REST API)

AWS Lambda (Python)

DynamoDB (GSI included)

Custom Lambda TOKEN Authorizer

IAM least-privilege access

This project demonstrates real-world serverless backend design, authentication, event-driven compute, and DynamoDB modeling.

🚀 Features
✅ Full CRUD API
Method	Path	Description
POST	/tasks	Create a task
GET	/tasks	Get all tasks
GET	/tasks?status=PENDING	Filter tasks using GSI
GET	/tasks/{taskId}	Get specific task
PUT	/tasks/{taskId}	Update task
DELETE	/tasks/{taskId}	Delete task
🔐 Custom Lambda TOKEN Authorizer

Requires header:

Authorization: <api-key>


Validates against Lambda environment variable:
EXPECTED_API_KEY

Returns wildcard IAM Allow policy:
arn:aws:execute-api:<region>:<acct>:<apiId>/<stage>/*/*

Ensures secure access to all routes.

🗃 DynamoDB Data Model
Main Table: ManagementTasks
Field	Type	Description
taskId	String	Primary partition key
title	String	Required
description	String	Optional
status	String	PENDING, IN_PROGRESS, DONE
createdAt	String	ISO-8601 timestamp
updatedAt	String	ISO-8601 timestamp
GSI: StatusIndex
Attribute	Role
status	Partition key
createdAt	Sort key

Used for:
GET /tasks?status=PENDING

🧱 Architecture
(Client)
   |
   | Authorization Header
   v
API Gateway (REST)
   |
   |---> Custom Lambda Authorizer
   |
   |---> CRUD Lambda (Proxy Integration)
                 |
                 v
             DynamoDB Table

🧪 Testing the API
Required Header
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

🔍 Filter by Status

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
Expected: 204 No Content

🧬 Lambda Functions
1️⃣ management-service-handler (CRUD Lambda)

Handles all REST operations

Parses API Gateway proxy events

Generates timestamps

Updates only provided fields

Applies CORS

Supports GSI query sorting

Required Environment Variables:

TABLE_NAME = ManagementTasks
STATUS_INDEX_NAME = StatusIndex

2️⃣ management-api-authorizer (Token Authorizer)

Validates authorizationToken

Compares with:

EXPECTED_API_KEY = <your-secret-key>


Returns wildcard IAM policy to allow all CRUD routes

🔧 Deployment Steps
1. Create DynamoDB Table

Table name: ManagementTasks

PK: taskId

GSI:

PK: status

SK: createdAt

Name: StatusIndex

2. IAM Role for CRUD Lambda

Attach:

AWSLambdaBasicExecutionRole

AmazonDynamoDBFullAccess (simplify; apply least privilege later)

3. Deploy CRUD Lambda

Runtime: Python 3.12

Environment Variables:

TABLE_NAME = ManagementTasks
STATUS_INDEX_NAME = StatusIndex

4. Deploy Authorizer Lambda

Runtime: Python 3.12

Environment Variable:

EXPECTED_API_KEY = my-super-secret-api-key-123

5. Configure API Gateway

Resources:

/tasks

/tasks/{taskId}

Integration:

CRUD Lambda

Authorization:

Custom Authorizer Lambda

Apply to ALL methods

6. Deploy API to Stage dev

Base URL format:

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

Store secrets in:

Lambda environment variables

IAM roles

AWS Secrets Manager (production)

CORS handled inside Lambda responses
