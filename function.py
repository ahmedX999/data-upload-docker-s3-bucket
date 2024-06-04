def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from S3 Bucket Lambda!'
    }
