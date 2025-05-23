from google.cloud import storage
import io

def download_blob_to_memory(bucket_name: str, source_blob_name: str) -> bytes:
    """Downloads a blob from the bucket into memory."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        file_content = io.BytesIO()
        blob.download_to_file(file_content)
        file_content.seek(0) # Rewind to the beginning
        return file_content.read()
    except Exception as e:
        print(f"Error downloading {source_blob_name} from {bucket_name}: {e}")
        raise

def upload_blob_from_memory(bucket_name: str, destination_blob_name: str, data: bytes, content_type: str = 'application/octet-stream'):
    """Uploads data from memory to a blob."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data, content_type=content_type)
        print(f"File uploaded to gs://{bucket_name}/{destination_blob_name}")
    except Exception as e:
        print(f"Error uploading to gs://{bucket_name}/{destination_blob_name}: {e}")
        raise

# Example of how you might call a Vertex AI Endpoint (conceptual)
# from google.cloud import aiplatform
# def predict_with_vertex_ai(project_id: str, endpoint_id: str, instances: list) -> dict:
#     """Makes a prediction request to a Vertex AI Endpoint."""
#     try:
#         aiplatform.init(project=project_id)
#         endpoint = aiplatform.Endpoint(endpoint_id)
#         response = endpoint.predict(instances=instances)
#         return response.predictions
#     except Exception as e:
#         print(f"Error predicting with Vertex AI Endpoint {endpoint_id}: {e}")
#         raise