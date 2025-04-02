import json
import os
import boto3
import urllib.request
import urllib.error
import time
import jwt  # pip install pyjwt
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

def create_jwt(api_key):
    key_id, secret = api_key.split(':')
    iat = int(time.time())
    exp = iat + 5 * 60  # 5 minuutin elinkaari
    payload = {
        'iat': iat,
        'exp': exp,
        'aud': '/v3/admin/'
    }

    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers={'kid': key_id})
    return token if isinstance(token, str) else token.decode('utf-8')

def lambda_handler(event, context):
    try:
        # Hae Secret Managerista admin_url ja api_key
        secrets_client = boto3.client('secretsmanager')
        secret = secrets_client.get_secret_value(SecretId='GhostAdminAPIKey')
        secret_data = json.loads(secret['SecretString'])
        api_key = secret_data['key']
        admin_url = secret_data['admin_url']

        token = create_jwt(api_key)

        headers = {
            'Authorization': f"Ghost {token}",
            'Content-Type': 'application/json'
        }

        # Hae postaukset
        posts = []
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Attempt {attempt} to fetch posts...")
                time.sleep(RETRY_DELAY_SECONDS)
                request = urllib.request.Request(
                    f"{admin_url}/ghost/api/v3/admin/posts/?limit=all",
                    headers=headers
                )
                with urllib.request.urlopen(request) as response:
                    data = json.loads(response.read())
                    posts = data.get('posts', [])
                    break
            except Exception as e:
                logger.error(f"Failed to fetch posts (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    raise Exception("Max retries exceeded while fetching posts")

        deleted_count = 0

        # Poista postaukset
        for post in posts:
            post_id = post['id']
            delete_url = f"{admin_url}/ghost/api/v3/admin/posts/{post_id}/"
            delete_request = urllib.request.Request(
                delete_url,
                method='DELETE',
                headers=headers
            )
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    logger.info(f"Deleting post {post_id} (attempt {attempt})...")
                    time.sleep(RETRY_DELAY_SECONDS)
                    urllib.request.urlopen(delete_request)
                    deleted_count += 1
                    break
                except urllib.error.HTTPError as e:
                    logger.error(f"HTTPError deleting post {post_id}: {e}")
                except urllib.error.URLError as e:
                    logger.error(f"URLError deleting post {post_id}: {e}")

        return {
            'adminurl': admin_url,
            'statusCode': 200,
            'body': f"Deleted {deleted_count} posts"
        }

    except Exception as e:
        logger.exception("Unhandled exception")
        return {
            'adminurl': secret_data.get('admin_url', 'unknown'),
            'statusCode': 500,
            'error': f"Failed to delete posts: {str(e)}"
        }
