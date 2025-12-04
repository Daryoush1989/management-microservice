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
```text
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
```

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

### 🧬 Lambda Functions

#### `management-service-handler` (CRUD Lambda)

- **Create Task**
- **List Tasks** (with optional filters)
- **Filter Tasks using GSI**
- **Get Task**
- **Update Task**
- **Delete Task**
- **DynamoDB Access**
- **CORS Response Handling**
- **Timestamp Generation**

### ✔ Required Environment Variables

```ini
TABLE_NAME=ManagementTasks
STATUS_INDEX_NAME=StatusIndex
```

management-api-authorizer (Custom Token Authorizer)

### ✔ Reads
```ini
authorizationToken
```

### ✔ Validates Against
```ini
EXPECTED_API_KEY
```

✔ Behavior

Returns IAM Allow or Deny

Wildcard ARN ensures the authorizer works for all endpoints in /dev/*

## 🛠️ Deployment Steps (Final Working Version)

### 1️⃣ Create DynamoDB Table

**Name:** `ManagementTasks`  
**PK:** `taskId`

Add GSI:

```makefile
Name: StatusIndex
PK: status
SK: createdAt
```

### 2️⃣ Create IAM Role for CRUD Lambda

Attach the following AWS-managed policies:

- `AWSLambdaBasicExecutionRole`
- `AmazonDynamoDBFullAccess` *(simple for demo; restrict in production)*


### 3️⃣ Create CRUD Lambda

- **Runtime:** Python 3.12  
- **Handler:** `management_service_handler.lambda_handler`

#### Environment Variables

```ini
TABLE_NAME=ManagementTasks
STATUS_INDEX_NAME=StatusIndex
```

Deploy the Lambda

#### 4️⃣ Create Authorizer Lambda

- **Runtime:** Python 3.12

#### Environment variable:
```ini
EXPECTED_API_KEY=my-super-secret-api-key-123
```

Deploy the authorizer Lambda

#### 5️⃣ Create API Gateway REST API
#### Resources
```ini
/tasks
/tasks/{taskId}
```

Attach:

Integration → **CRUD Lambda**

Authorizer → **ManagementApiAuthorizer**

Apply authorization to all methods.

#### 6️⃣ Deploy to Stage dev

Your base URL will look like:
```ini
https://<rest-api-id>.execute-api.<region>.amazonaws.com/dev
```
# 

## 📁 Project Structure

```text
management-microservice/
│
├── lambda/
│   ├── management_service_handler.py
│   ├── management_api_authorizer.py
│
├── README.md
└── .gitignore
```


🔒 Security Notes

- **Never commit actual API keys to GitHub**
- **Use environment variables + IAM roles**
- **For production, use AWS Secrets Manager**
- **CORS is handled within Lambda responses**
