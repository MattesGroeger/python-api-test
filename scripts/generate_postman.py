import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.main import app

# Generate OpenAPI schema
openapi_schema = app.openapi()

# Create Postman collection
postman_collection = {
    "info": {
        "name": "E-Commerce API",
        "description": "Collection for testing the E-Commerce API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [],
    "variable": [
        {
            "key": "BASE_URL",
            "value": "http://localhost:8000"
        },
        {
            "key": "TEST_USERNAME",
            "value": "testuser"
        },
        {
            "key": "TEST_PASSWORD",
            "value": "testpass"
        },
        {
            "key": "TEST_EMAIL",
            "value": "test@example.com"
        },
        {
            "key": "ACCESS_TOKEN",
            "value": ""
        },
        {
            "key": "ORDER_ID",
            "value": ""
        }
    ]
}

# Helper function to convert OpenAPI path to Postman format
def convert_path_to_postman(path):
    return path.replace("{", "{{").replace("}", "}}")

# Process each path in the OpenAPI spec
for path, methods in openapi_schema["paths"].items():
    for method, details in methods.items():
        # Skip options method
        if method.lower() == "options":
            continue
            
        # Create request item
        request = {
            "name": details.get("summary", f"{method.upper()} {path}"),
            "request": {
                "method": method.upper(),
                "header": [],
                "url": {
                    "raw": f"{{{{BASE_URL}}}}{path}",
                    "host": ["{{BASE_URL}}"],
                    "path": path.strip("/").split("/")
                }
            }
        }
        
        # Add Content-Type header for POST/PUT requests
        if method.lower() in ["post", "put"]:
            request["request"]["header"].append({
                "key": "Content-Type",
                "value": "application/json"
            })
            
        # Add Authorization header for protected endpoints
        if "security" in details:
            request["request"]["header"].append({
                "key": "Authorization",
                "value": "Bearer {{ACCESS_TOKEN}}"
            })
            
        # Add request body if needed
        if "requestBody" in details:
            content = details["requestBody"]["content"]
            if "application/json" in content:
                schema = content["application/json"]["schema"]
                example = {}
                for prop_name, prop in schema.get("properties", {}).items():
                    if prop.get("type") == "string":
                        example[prop_name] = "example_value"
                    elif prop.get("type") == "integer":
                        example[prop_name] = 1
                    elif prop.get("type") == "boolean":
                        example[prop_name] = True
                request["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(example, indent=2)
                }
                
        # Add test script for login endpoint to set token
        if path == "/api/v1/auth/token" and method.lower() == "post":
            request["request"]["event"] = [{
                "listen": "test",
                "script": {
                    "exec": [
                        "var jsonData = pm.response.json();",
                        "pm.environment.set(\"ACCESS_TOKEN\", jsonData.access_token);",
                        "console.log(\"Token set:\", pm.environment.get(\"ACCESS_TOKEN\"));"
                    ],
                    "type": "text/javascript"
                }
            }]
            
        postman_collection["item"].append(request)

# Save to file
output_path = project_root / "postman_collection.json"
with open(output_path, "w") as f:
    json.dump(postman_collection, f, indent=2)

print(f"Postman collection generated at {output_path}") 