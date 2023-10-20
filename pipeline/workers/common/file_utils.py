def check_bucket_exists(s3_client, bucket_name):
    bucket_list = s3_client.list_buckets()

    for bucket in bucket_list["Buckets"]:
        if bucket_name == bucket["Name"]:
            return True

    return False
