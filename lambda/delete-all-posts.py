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
    admin_url = secret_dict['admin_url'].rstrip('/')

    headers = {
        'Authorization': f'Ghost {api_key}',
        'Content-Type': 'application/json'
    }

    # Try fetching posts
    try:
        url = f"{admin_url}/ghost/api/v3/admin/posts/?limit=all"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        posts = response.json().get('posts', [])
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Failed to fetch posts",
            "url": url,
            "status_code": getattr(response, 'status_code', 'N/A'),
            "response_text": getattr(response, 'text', 'No response'),
            "exception": str(e)
        }

    # Delete posts
    deleted = 0
    for post in posts:
        try:
            del_url = f"{admin_url}/ghost/api/v3/admin/posts/{post['id']}/"
            del_response = requests.delete(del_url, headers=headers)
            del_response.raise_for_status()
            deleted += 1
        except Exception as e:
            print(f"Failed to delete post {post['id']}: {str(e)}")
            continue

    return {
        'statusCode': 200,
        'body': f"Deleted {deleted} posts"
    }
