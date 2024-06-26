import json
import boto3
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
    # Crée un client Secrets Manager
    client = boto3.client('secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Erreur lors de la récupération du secret: {e}")
        return None

    # Décrypte le secret à l'aide de la clé KMS associée.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def lambda_handler(event, context):
    secret_name = "my-secret"  #  le nom de secret

    secrets = get_secret(secret_name)
    if not secrets:
        return {
            'statusCode': 500,
            'body': json.dumps('Erreur lors de la récupération des secrets.')
        }

    encrypted_access_key = secrets.get('ENCRYPTED_ACCESS_KEY')
    encrypted_secret_key = secrets.get('ENCRYPTED_SECRET_KEY')
    encrypted_region = secrets.get('ENCRYPTED_REGION')

    if not encrypted_access_key or not encrypted_secret_key or not encrypted_region:
        return {
            'statusCode': 400,
            'body': json.dumps('Les informations d\'identification chiffrées sont requises.')
        }

    access_key = decrypt(encrypted_access_key)
    secret_key = decrypt(encrypted_secret_key)
    region = decrypt(encrypted_region)
    
    if not access_key or not secret_key or not region:
        return {
            'statusCode': 500,
            'body': json.dumps('Erreur lors du déchiffrement des informations d\'identification.')
        }

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3 = session.client('s3')

        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return {
            'statusCode': 200,
            'body': json.dumps(buckets)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erreur lors de la connexion à S3: {str(e)}")
        }
