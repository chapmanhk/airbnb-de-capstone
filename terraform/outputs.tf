output "raw_data_bucket" {
  value = aws_s3_bucket.raw_data.bucket
  description = "The name of the raw data bucket"
}

output "cleaned_data_bucket" {
  value = aws_s3_bucket.cleaned_data.bucket
  description = "The name of the cleaned data bucket"
}

output "models_bucket" {
  value = aws_s3_bucket.models.bucket
  description = "The name of the cleaned data bucket"
}

output "predictions_bucket" {
  value = aws_s3_bucket.predictions.bucket
  description = "The name of the predictions output bucket"
}
