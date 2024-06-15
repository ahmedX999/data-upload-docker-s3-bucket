def lambda_handler(event, context):
    encrypted_access_key = os.environ['ENCRYPTED_ACCESS_KEY']
    encrypted_secret_key = os.environ['ENCRYPTED_SECRET_KEY']
    print("encrypted_access_key")
    print(encrypted_access_key)
    print("encrypted_secret_key")
    print(encrypted_secret_key)
    return {
        'statusCode': 200,
        'body': 'Hello from The S3 Bucket Lambda function! 2024 '
    }
