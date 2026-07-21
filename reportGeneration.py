# This code here generate a reports.txt file that contains the data of EC2 instances, 
# Lambda functions, and S3 buckets in JSON format. It then sends an email with the reports.txt file attached to a specified recipient using AWS SES.
# I use jasonformatter to format the JSON data in a readable way. 


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

# Function to retrieve Lambda function data and return as a list of tuples
def lambda_data():
    return [
        (function["FunctionName"],
         function["Runtime"],
         function["LastModified"])
        for function in lambda_client.list_functions().get("Functions")
    ]

# def s3_data():
#     return [
#         (bucket["Name"],
#          bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S"))
#         for bucket in s3.list_buckets().get("Buckets")
#     ]


data = {
    "EC2_Instances": ec2_data(),
    "Lambda_Functions": lambda_data()
}

with open("reports.txt", "w") as f:
    f.write(json.dumps(data, indent=4))  # Writing the data to a reports.txt file in JSON format






# # To combine all three functions and print their outputs in dictionary format
# def generate_data():
#     return {
#         "EC2_Instances": ec2_data(),
#         "Lambda_Functions": lambda_data()
#         #,
#         #"S3_Buckets": s3_data()
#     } 

# def write_report_file(data, filename):
#     with open(filename, "w") as f: # Writing the combined data to a reports.txt file in JSON format
#         json.dump(data, f, indent=4)
    

# def build_email_message(from_email, to_email, subject, body, attachment_filename):
#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = ", ".join(to_email)
#     msg['Subject'] = subject
#     msg.attach(body)

#     with open(attachment_filename, "rb") as attachment:  #rb is readbytes 
#         part = MIMEBase("application", "octet-stream")
#         part.set_payload(attachment.read())

#     # Encode file in ASCII characters
#     encoders.encode_base64(part)

#     # Add header
#     part.add_header("Content-Disposition", f"attachment; filename= {attachment_filename}")
#     msg.attach(part) # Attach the file to the message
    
#     return msg


# def send_email(from_email, to_email, message):
#     response = ses.send_raw_email(
#         Source=from_email,
#         Destinations= to_email,
#         RawMessage={
#             'Data': message.as_string()
#         },
        
#     )
#     return response.get('MessageId')




# # The function will execute the whole logic
# def run():
#     attachment_filename = "cloud_report.txt"
#     data = generate_data()
#     write_report_file(data, attachment_filename)
#     business_team = "businesskpmgsol@kpmg.com"
#     from_email = "adetayo.eyelade2@gmail.com"
#     to_email = ["adetayo.eyelade@usach.cl"]
#     subject = "Better: Daily Cloud Report"
#     body =  f"""

#             Hi all,
#             Please find today cloud report attached.
#             Reach out to Cloud Automation Team for any queries on below email addresses. \n
#             {business_team}
#             Regards,
#             Cloud Automation Team

#             """
#     text_body = MIMEText(body, "plain")
#     email_message = build_email_message(from_email, to_email, subject, text_body, attachment_filename)
#     send_email(from_email, to_email, email_message)

# if __name__ == "__main__":
#     run()


#print(lambda_data())



