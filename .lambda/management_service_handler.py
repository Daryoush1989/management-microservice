import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ["TABLE_NAME"]
STATUS_INDEX_NAME = os.environ.get("STATUS_INDEX_NAME", "StatusIndex")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resp(status: int, body) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    method = event.get("httpMethod")
    path_params = event.get("pathParameters") or {}
    qs = event.get("queryStringParameters") or {}

    if method == "OPTIONS":
        return _resp(200, {"message": "OK"})

    body = event.get("body")
    if body and isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return _resp(400, {"message": "Invalid JSON"})

    # /tasks
    if not path_params.get("taskId"):
        if method == "POST":
            return create_task(body)
        if method == "GET":
            return list_tasks(qs)
        return _resp(405, {"message": "Method not allowed"})

    # /tasks/{taskId}
    task_id = path_params["taskId"]
    if method == "GET":
        return get_task(task_id)
    if method == "PUT":
        return update_task(task_id, body)
    if method == "DELETE":
        return delete_task(task_id)

    return _resp(405, {"message": "Method not allowed"})


def create_task(body: dict):
    if not body or not body.get("title"):
        return _resp(400, {"message": "Field 'title' is required"})

    status = body.get("status", "PENDING")
    if status not in ("PENDING", "IN_PROGRESS", "DONE"):
        return _resp(400, {"message": "Invalid status"})

    task_id = str(uuid.uuid4())
    now = _now_iso()

    item = {
        "taskId": task_id,
        "title": body["title"],
        "description": body.get("description", ""),
        "status": status,
        "createdAt": now,
        "updatedAt": now,
    }
    table.put_item(Item=item)
    return _resp(201, item)


def list_tasks(qs: dict):
    status = qs.get("status")
    if status:
        if status not in ("PENDING", "IN_PROGRESS", "DONE"):
            return _resp(400, {"message": "Invalid status filter"})
        resp = table.query(
            IndexName=STATUS_INDEX_NAME,
            KeyConditionExpression=Key("status").eq(status),
            ScanIndexForward=True,
        )
        return _resp(200, resp.get("Items", []))

    resp = table.scan()
    return _resp(200, resp.get("Items", []))


def get_task(task_id: str):
    resp = table.get_item(Key={"taskId": task_id})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"message": "Task not found"})
    return _resp(200, item)


def update_task(task_id: str, body: dict):
    if not body:
        return _resp(400, {"message": "Request body required"})

    allowed = {"title", "description", "status"}
    updates = []
    names = {}
    values = {}

    for k, v in body.items():
        if k not in allowed:
            continue
        if k == "status" and v not in ("PENDING", "IN_PROGRESS", "DONE"):
            return _resp(400, {"message": "Invalid status"})
        names[f"#{k}"] = k
        values[f":{k}"] = v
        updates.append(f"#{k} = :{k}")

    if not updates:
        return _resp(400, {"message": "No valid fields to update"})

    names["#updatedAt"] = "updatedAt"
    values[":updatedAt"] = _now_iso()
    updates.append("#updatedAt = :updatedAt")

    try:
        resp = table.update_item(
            Key={"taskId": task_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ConditionExpression="attribute_exists(taskId)",
            ReturnValues="ALL_NEW",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return _resp(404, {"message": "Task not found"})

    return _resp(200, resp["Attributes"])


def delete_task(task_id: str):
    try:
        table.delete_item(
            Key={"taskId": task_id},
            ConditionExpression="attribute_exists(taskId)",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return _resp(404, {"message": "Task not found"})

    return _resp(204, {})
