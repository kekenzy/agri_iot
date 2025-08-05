import boto3
import os
import mimetypes
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

def list_s3_files():
    try:
        # AWS認証情報の確認
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_S3_REGION_NAME')
        aws_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        
        if not all([aws_access_key, aws_secret_key, aws_region, aws_bucket]):
            raise ValueError("AWS認証情報が設定されていません。環境変数を確認してください。")
        
        s3 = boto3.client('s3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        
        response = s3.list_objects_v2(Bucket=aws_bucket)
        files = []

        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.endswith('/'):
                continue  # ディレクトリっぽいプレースホルダは除外
            
            try:
                content_type, _ = mimetypes.guess_type(key)
                presigned_url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': aws_bucket,
                        'Key': key,
                        'ResponseContentType': content_type or 'application/octet-stream'
                    },
                    ExpiresIn=3600  # 有効期限（秒）。ここでは1時間。
                )
                files.append({
                    'key': key,
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'url': presigned_url
                })
            except Exception as e:
                print(f"ファイル {key} の処理中にエラーが発生しました: {str(e)}")
                continue

        return files
        
    except NoCredentialsError:
        raise Exception("AWS認証情報が見つかりません。AWS_ACCESS_KEY_IDとAWS_SECRET_ACCESS_KEYを設定してください。")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            raise Exception(f"S3バケット '{aws_bucket}' が見つかりません。")
        elif error_code == 'AccessDenied':
            raise Exception("S3バケットへのアクセスが拒否されました。権限を確認してください。")
        else:
            raise Exception(f"AWS S3エラー: {error_code}")
    except EndpointConnectionError:
        raise Exception("AWS S3への接続に失敗しました。ネットワーク接続とリージョン設定を確認してください。")
    except Exception as e:
        raise Exception(f"S3ファイルリストの取得中にエラーが発生しました: {str(e)}")

def upload_file_to_s3(file):
    try:
        print(f"S3アップロード開始: {file.name}")
        
        # AWS認証情報の確認
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_S3_REGION_NAME')
        aws_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        
        print(f"AWS設定確認: リージョン={aws_region}, バケット={aws_bucket}")
        
        if not all([aws_access_key, aws_secret_key, aws_region, aws_bucket]):
            raise ValueError("AWS認証情報が設定されていません。環境変数を確認してください。")
        
        s3 = boto3.client('s3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        
        # ファイル名を安全にする（スペースや特殊文字を処理）
        safe_filename = file.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        print(f"安全なファイル名: {safe_filename}")
        
        s3.upload_fileobj(file, aws_bucket, safe_filename)
        print(f"S3アップロード完了: {safe_filename}")
        return True
        
    except NoCredentialsError:
        raise Exception("AWS認証情報が見つかりません。AWS_ACCESS_KEY_IDとAWS_SECRET_ACCESS_KEYを設定してください。")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            raise Exception(f"S3バケット '{aws_bucket}' が見つかりません。")
        elif error_code == 'AccessDenied':
            raise Exception("S3バケットへのアクセスが拒否されました。権限を確認してください。")
        else:
            raise Exception(f"AWS S3アップロードエラー: {error_code}")
    except Exception as e:
        raise Exception(f"ファイルアップロード中にエラーが発生しました: {str(e)}")

def delete_file_from_s3(key):
    s3 = boto3.client('s3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_S3_REGION_NAME'),
    )
    s3.delete_object(Bucket=os.environ.get('AWS_STORAGE_BUCKET_NAME'), Key=key)