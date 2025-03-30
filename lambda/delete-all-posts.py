import json
import os
import boto3
import requests

def lambda_handler(event, context):
    # Get credentials from Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId='GhostAdminAPIKey')
    secret_dict = json.loads(secret['SecretString'])

    api_key = secret_dict['key']
    admin_url = secret_dict['admin_url']

    # Remove trailing slash just in case
    admin_url = admin_url.rstrip('/')

    headers = {
        'Authorization': f'Ghost {api_key}',
        'Content-Type': 'application/json'
    }

    # Get all posts
    try:
        response = requests.get(f"{admin_url}/ghost/api/v3/admin/posts/?limit=all", headers=headers)
        response.raise_for_status()
        posts = response.json().get('posts', [])
    except Exception as e:
        return {
            "error": f"Failed to fetch posts: {str(e)}"
        }

    # Delete all posts
    deleted = 0
    for post in posts:
        try:
            del_response = requests.delete(f"{admin_url}/ghost/api/v3/admin/posts/{post['id']}/", headers=headers)
            del_response.raise_for_status()
            deleted += 1
        except Exception as e:
            continue

    return {
        'statusCode': 200,
        'body': f"Deleted {deleted} posts"
    }
