import subprocess
import json
import os

def handler(event, context):
    try:
        # Get the path to the kubectl binary
        # When bundled in the zip, it will be in the same directory as the handler
        kubectl_path = os.path.join(os.getcwd(), 'kubectl')
        
        # Ensure the binary is executable
        if os.path.exists(kubectl_path):
            os.chmod(kubectl_path, 0o755)

        # Execute kubectl version command
        result = subprocess.run(
            [kubectl_path, "version", "--client", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": result.stdout
        }
    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Failed to execute kubectl",
                "stderr": e.stderr
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
