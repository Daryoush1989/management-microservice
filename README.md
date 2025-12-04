# 🧩 Management Microservice (Serverless CRUD API on AWS)

A fully serverless task-management microservice built using:

- **AWS API Gateway (REST API)**
- **AWS Lambda (Python 3.12)**
- **DynamoDB (NoSQL + GSI)**
- **Custom Lambda TOKEN Authorizer**
- **IAM (least-privilege roles)**

This project demonstrates real-world serverless backend design, authentication, and DynamoDB modelling.

---

## 🚀 Features

### ✔ Full CRUD API

| Method | Path | Description |
|--------|-------|-------------|
| **POST** | `/tasks` | Create a task |
| **GET** | `/tasks` | Get all tasks |
| **GET** | `/tasks?status=PENDING` | Filter tasks using GSI |
| **GET** | `/tasks/{taskId}` | Get a specific task |
| **PUT** | `/tasks/{taskId}` | Update task |
| **DELETE** | `/tasks/{taskId}` | Delete task |

---

## 🔐 Secure API (Custom Token Authorizer)

Every request must include:

Authorization: <api-key>

The **authorizer Lambda** validates this against:

EXPECTED_API_KEY=<your-secret-key>

A correct key returns an IAM **Allow** policy with wildcard ARN:

arn:aws:execute-api:<region>:<account-id>:<restApiId>/<stage>//


This fix ensures **ALL routes** are authorized (not just one).

---

## 🗃 DynamoDB Data Store

### **Main Table: `ManagementTasks`**

| Field | Type | Description |
|-------|-------|-------------|
| taskId | String | Primary key |
| title | String | Required |
| description | String | Optional |
| status | String | PENDING, IN_PROGRESS, DONE |
| createdAt | String | ISO-8601 timestamp |
| updatedAt | String | ISO-8601 timestamp |

---

### **Global Secondary Index: `StatusIndex`**

| Attribute | Role |
|-----------|-------|
| status | Partition key |
| createdAt | Sort key |

Used for:

GET /tasks?status=PENDING

---

## 🧱 Architecture

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
DynamoDB (ManagementTasks)


---

## 🧪 Testing

### All requests require:

Authorization: my-super-secret-api-key-123


---

### ➕ Create a Task  
**POST /tasks**

```json
{
  "title": "First management task",
  "description": "Set up management microservice",
  "status": "PENDING"
}
```

---

### 📋 Get All Tasks  
**GET /tasks**

---

### 🔍 Filter Tasks (GSI)  
**GET /tasks?status=PENDING**

---

### 🔎 Get a Single Task  
**GET /tasks/{taskId}**

---

### ✏ Update a Task  
**PUT /tasks/{taskId}**

```json
{
  "status": "IN_PROGRESS",
  "title": "Updated task title"
}
```

---

### ❌ Delete a Task  
**DELETE /tasks/{taskId}**

Expected:

```
204 No Content
```

---
🧬 Lambda Functions
### management-service-handler (CRUD Lambda)
Handles:

Create task

List tasks (optionally filtered)

Filter tasks using GSI

Get task

Update task

Delete task

DynamoDB access

CORS response handling

Timestamp generation

Environment variables:

TABLE_NAME=ManagementTasks
STATUS_INDEX_NAME=StatusIndex
management-api-authorizer (Custom Token Authorizer)
Reads:

authorizationToken
Validates against:


EXPECTED_API_KEY
Returns IAM Allow/Deny using wildcard resource.

🔧 Deployment Steps (Final Working Version)
1️⃣ Create DynamoDB table
Name: ManagementTasks

Partition key: taskId

Add GSI:

Name: StatusIndex

PK: status

SK: createdAt

2️⃣ Create IAM Role for CRUD Lambda
Attach:

AWSLambdaBasicExecutionRole

AmazonDynamoDBFullAccess (demo simplification)

3️⃣ Create CRUD Lambda
Runtime: Python 3.12

Handler: management_service_handler.lambda_handler

Environment variables:

TABLE_NAME=ManagementTasks
STATUS_INDEX_NAME=StatusIndex
Deploy.

4️⃣ Create Authorizer Lambda
Runtime: Python 3.12

Env var:


EXPECTED_API_KEY=my-super-secret-api-key-123
Deploy.

5️⃣ Create API Gateway REST API
Resources:


/tasks
/tasks/{taskId}
All methods → integration = CRUD Lambda

Authorization for each method → ManagementApiAuthorizer

6️⃣ Deploy API to Stage dev
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
Do NOT commit real API keys to GitHub

Use IAM roles + environment variables

Use Secrets Manager for production

CORS handled inside Lambda responses

