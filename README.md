🧩 Management Microservice (Serverless CRUD API on AWS)

A fully serverless task management microservice built using:

AWS API Gateway (REST API)

AWS Lambda (Python)

DynamoDB (NoSQL, GSI included)

Custom Lambda TOKEN Authorizer

IAM for secure, least-privilege access

This project demonstrates real-world serverless backend design, authentication, event-driven compute, and DynamoDB modeling patterns.

🚀 Features
✔ Full CRUD API
Method	Path	Description
POST	/tasks	Create a task
GET	/tasks	Get all tasks
GET	/tasks?status=PENDING	Filter tasks using GSI
GET	/tasks/{taskId}	Get specific task
PUT	/tasks/{taskId}	Update task
DELETE	/tasks/{taskId}	Delete task
✔ Secure API with Custom Lambda Authorizer

Every request must include:

Authorization: <api-key>


Validates against Lambda environment variable:

EXPECTED_API_KEY


Returns IAM Allow policy with wildcard ARN, enabling all routes in the dev stage:

arn:aws:execute-api:<region>:<accountId>:<apiId>/<stage>/*/*

🗃 DynamoDB Data Store

Primary table for tasks.
Includes a Global Secondary Index to filter by status in real time.

📊 Data Model (DynamoDB)
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
   | Authorization header
   v
API Gateway (REST)
   |
   |--> Custom Lambda Authorizer
   |
   |--> Lambda Proxy Integration
            |
            v
     management-service-handler (CRUD Lambda)
            |
            v
       DynamoDB Table

🧪 Testing
Required header for every request:
Authorization: my-super-secret-api-key-123

➕ Create a task

POST /tasks

{
  "title": "First management task",
  "description": "Set up management microservice",
  "status": "PENDING"
}

📋 Get all tasks

GET /tasks

🔍 Filter by status (GSI)

GET /tasks?status=PENDING

🔎 Get one task

GET /tasks/{taskId}

✏ Update a task

PUT /tasks/{taskId}

{
  "status": "IN_PROGRESS",
  "title": "Updated task title"
}

❌ Delete a task

DELETE /tasks/{taskId}

Expected:

204 No Content

🧬 Lambda Functions
management-service-handler (CRUD Lambda)

Handles all CRUD logic

Parses API Gateway proxy events

Generates timestamps

Queries DynamoDB + GSI

Dynamically updates only provided fields

Returns CORS-enabled responses

Environment variables:
TABLE_NAME = ManagementTasks
STATUS_INDEX_NAME = StatusIndex

management-api-authorizer (Custom Token Authorizer)

Reads:

authorizationToken


Validates with:

EXPECTED_API_KEY


Returns IAM Allow policy using wildcard ARN:

arn:aws:execute-api:<region>:<acct>:<apiId>/<stage>/*/*

🔧 Deployment Steps (Final Working Version)
1. Create DynamoDB Table

Table: ManagementTasks

PK: taskId

Create GSI:

Name: StatusIndex

PK: status

SK: createdAt

2. Create IAM Role for CRUD Lambda

Attach:

AWSLambdaBasicExecutionRole

AmazonDynamoDBFullAccess (simple version for demo)

3. Deploy CRUD Lambda (management-service-handler)

Runtime: Python 3.12

Add environment variables

Paste CRUD code

Deploy

4. Deploy Authorizer Lambda (management-api-authorizer)

Runtime: Python 3.12

Add environment variable:

EXPECTED_API_KEY = my-super-secret-api-key-123


Paste authorizer code

Deploy

5. Create API Gateway REST API

Resources:

/tasks
/tasks/{taskId}


For each method:

Integration → CRUD Lambda

Authorizer → management-api-authorizer

Enable for all methods

6. Deploy API to Stage dev

Base URL example:

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

Use Lambda environment variables, IAM roles, and Secrets Manager (production)

CORS returned from Lambda for simplicity
