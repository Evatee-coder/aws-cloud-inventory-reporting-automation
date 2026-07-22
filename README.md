# AWS Cloud Inventory Reporting Automation

Automates recurring AWS infrastructure inventory by collecting metadata from Amazon EC2, AWS Lambda, and Amazon S3, generating a structured JSON report, and delivering it to stakeholders through Amazon SES.

The project mirrors a production cloud operations workflow used for governance, compliance reviews, cost visibility, and infrastructure reporting without requiring engineers to manually inspect multiple AWS services.

---

## Table of Contents

- [Architecture](#architecture)
- [Project Highlights](#project-highlights)
- [Tech Stack](#tech-stack)
- [Engineering Decisions](#engineering-decisions)
- [Repository Structure](#repository-structure)
- [Setup and Usage](#setup-and-usage)
- [IAM Permissions](#iam-permissions)
- [Sample Output](#sample-output)
- [Challenges and Fixes](#challenges-and-fixes)
- [Future Improvements](#future-improvements)
- [Skills Demonstrated](#skills-demonstrated)
- [Author](#author)

---

## Architecture

```text
                Amazon EventBridge
               Scheduled Trigger
                      │
                      ▼
               AWS Lambda Function
              Inventory Collection
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Amazon EC2    AWS Lambda     Amazon S3
DescribeInstances ListFunctions ListBuckets
        └─────────────┼─────────────┘
                      ▼
         Consolidated JSON Report
         /tmp/cloud_report.txt
                      │
                      ▼
               Amazon SES Email
                      │
                      ▼
           Stakeholder Email Inbox
```

The workflow is triggered on a schedule by Amazon EventBridge. The Lambda function queries multiple AWS services through `boto3`, consolidates the collected inventory into a single JSON report, stores the report in Lambda's temporary filesystem, and sends it as an email attachment using Amazon SES.

---

## Project Highlights

- Automated AWS infrastructure inventory across EC2, Lambda, and S3
- Built as both a local CLI application and an AWS Lambda function
- Scheduled execution using Amazon EventBridge
- Email delivery with MIME attachments via Amazon SES
- Structured exception handling for operational visibility
- Designed with least-privilege IAM permissions
- Production-style serverless reporting workflow

---

## Tech Stack

- Python 3
- boto3
- AWS Lambda
- Amazon EventBridge
- Amazon EC2
- Amazon S3
- Amazon SES
- AWS IAM
- JSON
- Python `email.mime`

---

## Engineering Decisions

### Use AWS Lambda instead of an EC2 instance

The reporting job executes only on a schedule, making AWS Lambda a more operationally efficient choice than maintaining a continuously running EC2 instance.

### Use EventBridge for scheduling

Amazon EventBridge provides a fully managed scheduler, eliminating the need for operating-system cron jobs or additional infrastructure.

### Store reports in `/tmp`

AWS Lambda provides writable temporary storage only in `/tmp`. Since the report is generated and emailed within a single execution, temporary storage avoids unnecessary complexity.

### Maintain two execution models

The project includes both a standalone Python script for local testing and a Lambda implementation for production deployment. This improves developer productivity while preserving deployment flexibility.

### Implement structured exception handling

Errors are captured and returned as structured responses, improving CloudWatch observability and making failures easier to diagnose.

---

## Repository Structure

```text
.
├── reportGeneration.py
├── lambda_code.py
├── cloud_report.txt
├── requirements.txt
└── README.md
```

| File | Description |
|------|-------------|
| `reportGeneration.py` | Standalone Python implementation for local execution |
| `lambda_code.py` | AWS Lambda implementation |
| `cloud_report.txt` | Sample generated inventory report |
| `requirements.txt` | Project dependencies |
| `README.md` | Project documentation |

---

## Setup and Usage

### Clone the repository

```bash
git clone https://github.com/Evatee-coder/aws-cloud-inventory-reporting.git

cd aws-cloud-inventory-reporting
```

### Create a virtual environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install boto3
```

### Configure AWS credentials

```bash
aws configure
```

Verify the configured identity

```bash
aws sts get-caller-identity
```

### Configure Amazon SES

Verify the sender identity (or domain) in Amazon SES.

If your SES account is operating in the sandbox, the recipient email address must also be verified.

### Run locally

```bash
python3 reportGeneration.py
```

The generated report will be written to

```text
cloud_report.txt
```

---

## AWS Lambda Deployment

Package the Lambda function

```bash
zip lambda_inventory.zip lambda_code.py
```

Create an AWS Lambda function using

```text
Runtime : Python 3.x

Handler : lambda_code.lambda_handler
```

Attach an EventBridge schedule, for example

```text
rate(1 day)
```

or

```text
cron(0 8 * * ? *)
```

---

## IAM Permissions

The Lambda execution role requires the following minimum permissions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InventoryReadAccess",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "lambda:ListFunctions",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SendInventoryReport",
      "Effect": "Allow",
      "Action": [
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

The AWS managed policy **AWSLambdaBasicExecutionRole** should also be attached to enable CloudWatch logging.

---

## Sample Output

```json
{
  "ec2_instances": [
    {
      "instance_id": "i-0123456789abcdef0",
      "instance_type": "t3.micro",
      "state": "running"
    }
  ],
  "lambda_functions": [
    {
      "function_name": "inventory-report",
      "runtime": "python3.12",
      "last_modified": "2026-07-20T10:30:00+0000"
    }
  ],
  "s3_buckets": [
    {
      "bucket_name": "company-backups",
      "creation_date": "2026-01-15T14:20:00Z"
    }
  ]
}
```

---

## Challenges and Fixes

### Lambda filesystem restrictions

AWS Lambda provides a read-only execution environment except for the `/tmp` directory.

**Resolution**

The Lambda implementation writes reports to `/tmp/cloud_report.txt`, while the standalone application writes to the local project directory.

---

### JSON serialization errors

Amazon S3 returns bucket creation dates as `datetime` objects, which cannot be serialized directly to JSON.

**Resolution**

```python
json.dump(report_data, report_file, indent=4, default=str)
```

---

### Improving operational visibility

Unhandled exceptions resulted in failed Lambda invocations with limited troubleshooting information.

**Resolution**

Implemented structured exception handling that logs failures to CloudWatch and returns consistent success and error responses.

---

## Future Improvements

- Provision the complete solution with Terraform
- Store configuration in AWS Systems Manager Parameter Store or AWS Secrets Manager
- Add pagination support for large AWS environments
- Store historical reports in Amazon S3
- Generate HTML and CSV reports
- Add automated unit testing with `pytest` and `moto`
- Build a GitHub Actions CI/CD pipeline
- Publish CloudWatch metrics and alarms for failed executions

---

## Skills Demonstrated

- AWS SDK development with `boto3`
- Serverless application development
- Event-driven architecture
- AWS Lambda runtime optimization
- IAM least-privilege design
- JSON data modeling
- Python automation
- MIME email generation
- Exception handling and observability
- Cloud operations automation

---

## Author

**Adetayo Eyelade**

- GitHub: https://github.com/Evatee-coder
- LinkedIn: https://www.linkedin.com/in/victor-adetayo-eyelade-a98606128/
