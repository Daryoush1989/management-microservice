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

Requires header:

Authorization: <api-key>


Validates against Lambda environment variable: EXPECTED_API_KEY

Returns IAM “Allow” policy with correct wildcard ARN, enabling all routes in the dev stage

✔ DynamoDB Data Store

Primary table for tasks

Includes Global Secondary Index to filter by status in real time

🗃 Data Model (DynamoDB)
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
   |---> Custom Lambda Authorizer (Token validation)
   |
   |---> Lambda Proxy Integration → CRUD Lambda
                                       |
                                       v
                                  DynamoDB Table

🧪 Testing

Every request requires:

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

✏ Update

PUT /tasks/{taskId}

{
  "status": "IN_PROGRESS",
  "title": "Updated task title"
}

❌ Delete

DELETE /tasks/{taskId}
Expected → 204 No Content

🧬 Lambda Functions
management-service-handler (Main CRUD Lambda)

Handles all CRUD logic

Parses API Gateway proxy event inputs

Generates timestamps

Sorts GSI queries by creation time

Dynamically updates only provided fields

Outputs full CORS-enabled responses

Environment variables required:

TABLE_NAME = ManagementTasks
STATUS_INDEX_NAME = StatusIndex

management-api-authorizer (Custom Token Authorizer)

Reads:

authorizationToken


Validates with:

EXPECTED_API_KEY = <your-secret-key>


On success, returns IAM policy with wildcard:

arn:aws:execute-api:<region>:<acct>:<apiId>/<stage>/*/*


This fix ensures API Gateway authorizes all routes, not just a single operation.

🔧 Deployment Steps (with fixes applied)
1. Create DynamoDB table

Name: ManagementTasks

PK: taskId

Add GSI:

PK: status

SK: createdAt

Name: StatusIndex

2. Create IAM Role for CRUD Lambda

Attach policies:

AWSLambdaBasicExecutionRole

AmazonDynamoDBFullAccess (simple; replace with least-privilege in real environments)

3. Create CRUD Lambda (management-service-handler)

Runtime: Python 3.12

Add environment vars:

TABLE_NAME = ManagementTasks
STATUS_INDEX_NAME = StatusIndex


Paste CRUD logic

Deploy.

4. Create Authorizer Lambda (management-api-authorizer)

Runtime: Python 3.12

Add environment var:

EXPECTED_API_KEY = my-super-secret-api-key-123


Paste fixed authorizer code (wildcard ARN)

Deploy.

5. Create API Gateway REST API

Resources:

/tasks
/tasks/{taskId}


Assign:

Integration → CRUD Lambda

Authorizer → Custom authorizer lambda

Set Authorization:

Authorization = ManagementApiAuthorizer


Apply to:

ALL methods (GET, POST, PUT, DELETE)

OPTIONS optional

6. Deploy API to Stage dev

Your base URL will look like:

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

Use:

Lambda environment variables

IAM roles

AWS Secrets Manager (production)

CORS is handled inside the Lambda responses
