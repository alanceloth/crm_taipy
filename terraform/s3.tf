# s3.tf

resource "aws_s3_bucket" "crm_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Name = "CRM Taipy Bucket"
    managed_by = "terraform"
  }
}

resource "aws_s3_bucket_policy" "crm_bucket_policy" {
  bucket = aws_s3_bucket.crm_bucket.id

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::${aws_s3_bucket.crm_bucket.bucket}",
        "arn:aws:s3:::${aws_s3_bucket.crm_bucket.bucket}/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": [var.allowed_ip]
        }
      }
    }]
  })
}

resource "aws_s3_bucket_ownership_controls" "crm_bucket-acl-ownership" {
  bucket = aws_s3_bucket.crm_bucket.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
