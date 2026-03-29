provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    lambda = "http://localhost:4566"
    iam    = "http://localhost:4566"
    sts    = "http://localhost:4566"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "kubectl_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Lambda Function
resource "aws_lambda_function" "kubectl_version" {
  filename         = "lambda_function_payload.zip"
  function_name    = "kubectl-version-lambda"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 15

  source_code_hash = filebase64sha256("lambda_function_payload.zip")
}

# Lambda URL for easy access
resource "aws_lambda_function_url" "kubectl_url" {
  function_name      = aws_lambda_function.kubectl_version.function_name
  authorization_type = "NONE"
}

output "function_url" {
  value = aws_lambda_function_url.kubectl_url.function_url
}
