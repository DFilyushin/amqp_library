from prometheus_client import Counter, Histogram

DURATION_WORK = Histogram('listener_work_duration_seconds', 'Processing speed of one request')
COUNT_SUCCESS_MESSAGES = Counter('listener_success_processed_message', 'Count of success processed message')
COUNT_ERROR_MESSAGES = Counter('listener_error_processed_message', 'Count of error processed message')
