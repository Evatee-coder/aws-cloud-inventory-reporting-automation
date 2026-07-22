# This code here is the lambda version of reportGeneration.py to generate a reports.txt file via Lambda function
# containing combined data from EC2, Lambda, and S3 in JSON format.


import boto3
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase # For attaching files
from email import encoders  # For encoding the attachments

ec2 = boto3.client("ec2")
lambda_client = boto3.client("lambda")
s3 = boto3.client("s3")
ses = boto3.client("ses")
aws_region = "us-east-1"

# Function to retrieve EC2 instance data and return as a list of tuples
def ec2_data():
    return [(instance["Instances"][0].get("InstanceId"),
             instance["Instances"][0].get("InstanceType"),
             instance["Instances"][0].get("State").get("Name"))
            for instance in ec2.describe_instances().get("Reservations")
            ]

def lambda_data():
    return [
        (function["FunctionName"],
         function["Runtime"],
         function["LastModified"])
        for function in lambda_client.list_functions().get("Functions")
    ]

def s3_data():
    return [
        (bucket["Name"],
         bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S"))
        for bucket in s3.list_buckets().get("Buckets")
    ]

# To combine all three functions and print their outputs in dictionary format
def generate_data():
    return {
        "EC2_Instances": ec2_data(),
        "Lambda_Functions": lambda_data(),
        "S3_Buckets": s3_data()
    } 

def write_report_file(data, filename):
    # Write to /tmp directory (Lambda's writable directory)
    filepath = f"/tmp/{filename}"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4, default=str)
    return filepath  # Return the full path

def build_email_message(from_email, to_email, subject, body, attachment_filepath):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_email)
    msg['Subject'] = subject
    msg.attach(body)
    
    # Read from /tmp directory
    with open(attachment_filepath, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    # Encode file in ASCII characters
    encoders.encode_base64(part)
    
    # Add header - use only the filename without path
    filename = attachment_filepath.split('/')[-1]
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")
    msg.attach(part)
    
    return msg

def send_email(from_email, to_email, message):
    response = ses.send_raw_email(
        Source=from_email,
        Destinations=to_email,
        RawMessage={
            'Data': message.as_string()
        }
    )
    return response.get('MessageId')

# The function will execute the whole logic
def lambda_handler(event, context):
    try:
        attachment_filename = "cloud_report.txt"
        
        # Generate data
        data = generate_data()
        
        # Write report to /tmp and get the filepath
        filepath = write_report_file(data, attachment_filename)
        
        # Email configuration
        business_team = "xxxxxxx@gmail.com"
        from_email = "yyyyyyyyy@gmail.com"
        to_email = ["zzzzzzzz@usach.cl"]
        subject = "Better: Daily Cloud Report"
        body = f"""
Hi all,

Please find today cloud report attached.

Reach out to Cloud Automation Team for any queries on below email addresses.
{business_team}

Regards,
Cloud Automation Team
"""
        
        text_body = MIMEText(body, "plain")
        
        # Build and send email using the filepath from /tmp
        email_message = build_email_message(from_email, to_email, subject, text_body, filepath)
        message_id = send_email(from_email, to_email, email_message)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Email sent successfully! Message ID: {message_id}')
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
