import os
import json
import boto3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from botocore.exceptions import ClientError
import base64

def decrypt(ciphertext):
    kms = boto3.client('kms')
    try:
        response = kms.decrypt(CiphertextBlob=base64.b64decode(ciphertext))
        return response['Plaintext'].decode('utf-8')
    except ClientError as e:
        print(f"Erreur lors du déchiffrement: {e}")
        return None

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Erreur lors de la récupération du secret: {e}")
        return None

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def create_drive_service(client_id, client_secret, refresh_token):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret
    )
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

def lambda_handler(event, context):
    secret_name = "my-google-drive-secret"  #  le nom de  secret

    secrets = get_secret(secret_name)
    if not secrets:
        return {
            'statusCode': 500,
            'body': json.dumps('Erreur lors de la récupération des secrets.')
        }

    encrypted_client_id = secrets.get('ENCRYPTED_CLIENT_ID')
    encrypted_client_secret = secrets.get('ENCRYPTED_CLIENT_SECRET')
    encrypted_refresh_token = secrets.get('ENCRYPTED_REFRESH_TOKEN')

    if not encrypted_client_id or not encrypted_client_secret or not encrypted_refresh_token:
        return {
            'statusCode': 400,
            'body': json.dumps('Les informations d\'identification chiffrées sont requises.')
        }

    client_id = decrypt(encrypted_client_id)
    client_secret = decrypt(encrypted_client_secret)
    refresh_token = decrypt(encrypted_refresh_token)
    
    if not client_id or not client_secret or not refresh_token:
        return {
            'statusCode': 500,
            'body': json.dumps('Erreur lors du déchiffrement des informations d\'identification.')
        }

    try:
        drive_service = create_drive_service(client_id, client_secret, refresh_token)
        
        # Récupérer la liste des fichiers du Google Drive
        results = drive_service.files().list(pageSize=10).execute()
        items = results.get('files', [])
        
        response = {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
    return response
