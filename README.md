# 🧩 Management Microservice (Serverless CRUD API on AWS)

A fully serverless task-management microservice built using:

- **AWS API Gateway (REST API)**
- **AWS Lambda (Python)**
- **DynamoDB (NoSQL with GSI support)**
- **Custom Lambda TOKEN Authorizer**
- **IAM** for secure, least-privilege access

This project demonstrates real-world serverless backend design, authentication, event-driven compute, and DynamoDB modeling patterns.

---

## 🚀 Features

### ✔ Full CRUD API

| Method | Path                 | Description                     |
|--------|----------------------|---------------------------------|
| POST   | /tasks               | Create a task                   |
| GET    | /tasks               | Get all tasks                   |
| GET    | /tasks?status=PENDING | Filter using GSI by status      |
| GET    | /tasks/{taskId}      | Get one task                    |
| PUT    | /tasks/{taskId}      | Update task                     |
| DELETE | /tasks/{taskId}      | Delete task                     |

---

## 🔐 Secure API with Custom Lambda Authorizer

Every request must include:

Authorization: <api-key>

markdown
Copy code

The authorizer:

- Reads: `authorizationToken`
- Validates against Lambda environment variable:

EXPECTED_API_KEY = <your-secret-key>

markdown
Copy code

- Returns IAM `"Allow"` with **wildcard ARN**:

arn:aws:execute-api:<region>:<accountId>:<restApiId>/<stage>//

yaml
Copy code

This fix ensures **ALL routes** under the development stage are authorized.

---

## 🗃 DynamoDB Data Store

- **Primary table** for tasks
- Includes **Global Secondary Index (GSI)** to filter by status in real time

---

## 📊 Data Model (DynamoDB)

### **Main Table: `ManagementTasks`**

| Field       | Type   | Description                 |
|-------------|--------|-----------------------------|
| taskId      | String | Primary partition key       |
| title       | String | Required                    |
| description | String | Optional                    |
| status      | String | PENDING, IN_PROGRESS, DONE  |
| createdAt   | String | ISO-8601 timestamp          |
| updatedAt   | String | ISO-8601 timestamp          |

### **Global Secondary Index: `StatusIndex`**

| Attribute | Role            |
|-----------|-----------------|
| status    | Partition key   |
| createdAt | Sort key        |

Used for:

GET /tasks?status=PENDING

yaml
Copy code

---

## 🧱 Architecture

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

yaml
Copy code

---

## 🧪 Testing

### Every request requires:

Authorization: my-super-secret-api-key-123

yaml
Copy code

---

### ➕ Create a task

**POST /tasks**

```json
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

json
Copy code
{
  "status": "IN_PROGRESS",
  "title": "Updated task title"
}
❌ Delete a task
DELETE /tasks/{taskId}

Expected:

css
Copy code
204 No Content
🧬 Lambda Functions
1️⃣ management-service-handler (Main CRUD Lambda)
This function:

Handles all CRUD logic

Parses API Gateway proxy events

Generates timestamps

Uses GSI queries sorted by creation time

Dynamically updates only fields supplied by the user

Returns CORS-enabled HTTP payloads

Environment variables:
ini
Copy code
TABLE_NAME=ManagementTasks
STATUS_INDEX_NAME=StatusIndex
2️⃣ management-api-authorizer (Custom Token Authorizer)
Reads:

nginx
Copy code
authorizationToken
Validates with environment variable:

ini
Copy code
EXPECTED_API_KEY=<your-secret-key>
Returns IAM policy with wildcard resource:

ruby
Copy code
arn:aws:execute-api:<region>:<acct>:<apiId>/<stage>/*/*
This ensures API Gateway authorizes all routes (fix applied during debugging).

🔧 Deployment Steps (Final Version With Fixes)
1. Create DynamoDB Table
Name: ManagementTasks

Partition key: taskId (String)

Add a GSI:

yaml
Copy code
PK: status
SK: createdAt
Index name: StatusIndex
2. Create IAM Role for CRUD Lambda
Attach policies:

AWSLambdaBasicExecutionRole

AmazonDynamoDBFullAccess (note: use least-privilege in production)

3. Create CRUD Lambda
Runtime: Python 3.12

Set environment variables:

ini
Copy code
TABLE_NAME=ManagementTasks
STATUS_INDEX_NAME=StatusIndex
Paste CRUD code

Deploy

4. Create Authorizer Lambda
Runtime: Python 3.12

Add environment variable:

ini
Copy code
EXPECTED_API_KEY=my-super-secret-api-key-123
Paste fixed authorizer code (wildcard ARN)

Deploy

5. Create API Gateway REST API
Create two resources:

bash
Copy code
/tasks
/tasks/{taskId}
Assign:

Step	Setting
Integration	CRUD Lambda
Authorizer	management-api-authorizer
Authorization	REQUIRED on all methods

Methods requiring authorizer:

POST /tasks

GET /tasks

GET /tasks/{taskId}

PUT /tasks/{taskId}

DELETE /tasks/{taskId}

6. Deploy API to Stage dev
Your base URL will look like:

php-template
Copy code
https://<rest-api-id>.execute-api.<region>.amazonaws.com/dev
📁 Project Structure
python
Copy code
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

Store sensitive values using:

Lambda environment variables

IAM roles (for AWS resources)

AWS Secrets Manager (prod)

CORS is handled inside Lambda responses
