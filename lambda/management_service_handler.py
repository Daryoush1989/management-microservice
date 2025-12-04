import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "ManagementTasks")
status_index_name = os.environ.get("STATUS_INDEX_NAME", "StatusIndex")
table = dynamodb.Table(table_name)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            # Simple CORS for dev – adjust allowed origin in real prod
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body)
    }


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def lambda_handler(event, context):
    """
    Main entrypoint for API Gateway REST API (proxy integration).
    """
    http_method = event.get("httpMethod")
    path = event.get("path") or ""
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    body = event.get("body")

    if body and isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return _response(400, {"message": "Invalid JSON in request body"})

    # Routes based on path + method
    # /tasks
    if path.endswith("/tasks") and "taskId" not in path_params:
        if http_method == "POST":
            return create_task(body)
        elif http_method == "GET":
            return list_tasks(query_params)
        elif http_method == "OPTIONS":
            return _response(200, {"message": "OK"})

    # /tasks/{taskId}
    if "/tasks/" in path and "taskId" in path_params:
        task_id = path_params["taskId"]
        if http_method == "GET":
            return get_task(task_id)
        elif http_method == "PUT":
            return update_task(task_id, body)
        elif http_method == "DELETE":
            return delete_task(task_id)
        elif http_method == "OPTIONS":
            return _response(200, {"message": "OK"})

    return _response(404, {"message": "Not Found"})


def create_task(body):
    if not body:
        return _response(400, {"message": "Request body is required"})

    title = body.get("title")
    description = body.get("description", "")
    status = body.get("status", "PENDING")

    if not title:
        return _response(400, {"message": "Field 'title' is required"})

    if status not in ("PENDING", "IN_PROGRESS", "DONE"):
        return _response(400, {"message": "Invalid status"})

    task_id = str(uuid.uuid4())
    now = _now_iso()

    item = {
        "taskId": task_id,
        "title": title,
        "description": description,
        "status": status,
        "createdAt": now,
        "updatedAt": now
    }

    table.put_item(Item=item)

    return _response(201, item)


def list_tasks(query_params):
    """
    If query param status is provided, use GSI to filter by status.
    Otherwise, Scan the whole table (OK for small/demo).
    """
    status = query_params.get("status") if query_params else None

    if status:
        if status not in ("PENDING", "IN_PROGRESS", "DONE"):
            return _response(400, {"message": "Invalid status filter"})
        resp = table.query(
            IndexName=status_index_name,
            KeyConditionExpression=Key("status").eq(status),
            ScanIndexForward=True  # oldest first
        )
        items = resp.get("Items", [])
    else:
        # demo only – scans do not scale well for large tables
        resp = table.scan()
        items = resp.get("Items", [])

    return _response(200, items)


def get_task(task_id):
    resp = table.get_item(Key={"taskId": task_id})
    item = resp.get("Item")
    if not item:
        return _response(404, {"message": "Task not found"})
    return _response(200, item)


def update_task(task_id, body):
    if not body:
        return _response(400, {"message": "Request body is required"})

    allowed_fields = {"title", "description", "status"}
    update_expr_parts = []
    expr_attr_values = {}
    expr_attr_names = {}

    for field, value in body.items():
        if field not in allowed_fields:
            continue
        if field == "status" and value not in ("PENDING", "IN_PROGRESS", "DONE"):
            return _response(400, {"message": "Invalid status"})
        placeholder_name = f"#{field}"
        placeholder_value = f":{field}"
        update_expr_parts.append(f"{placeholder_name} = {placeholder_value}")
        expr_attr_names[placeholder_name] = field
        expr_attr_values[placeholder_value] = value

    if not update_expr_parts:
        return _response(400, {"message": "No valid fields to update"})

    # always update updatedAt
    update_expr_parts.append("#updatedAt = :updatedAt")
    expr_attr_names["#updatedAt"] = "updatedAt"
    expr_attr_values[":updatedAt"] = _now_iso()

    update_expr = "SET " + ", ".join(update_expr_parts)

    resp = table.update_item(
        Key={"taskId": task_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values,
        ConditionExpression="attribute_exists(taskId)",
        ReturnValues="ALL_NEW"
    )

    return _response(200, resp.get("Attributes", {}))


def delete_task(task_id):
    try:
        table.delete_item(
            Key={"taskId": task_id},
            ConditionExpression="attribute_exists(taskId)"
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return _response(404, {"message": "Task not found"})

    return _response(204, {})

