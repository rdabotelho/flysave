import boto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

def send_sms(phone_number: str, message: str):
    """
    Envia um SMS usando AWS SNS.
    """
    client = boto3.client(
        "sns",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    try:
        response = client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
    except Exception as e:
        print(f"❌ Erro ao enviar SMS: {e}")

