curl --request POST 'http: //localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "How did monthly revenue vary by customer region across 2025?",
    "user_context": {
        "user_id": "poc-user"
    },
    "include_trace": false
}'

curl --request POST 'http: //localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "Which customer segment generated the most revenue in Q1 2025?",
    "user_context": {
        "user_id": "poc-user"
    },
    "include_trace": false
}'

curl --request POST 'http: //localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "What were the three highest-revenue months in 2025?",
    "user_context": {
        "user_id": "poc-user"
    },
    "include_trace": false
}'

curl --request POST 'http: //localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "How did monthly revenue in the West region trend during the second half of 2025?",
    "user_context": {
        "user_id": "poc-user"
    },
    "include_trace": false
}'

curl --request POST 'http: //localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "Can you compare 2025 revenue between the East and Central regions?",
    "user_context": {
        "user_id": "poc-user"
    },
    "include_trace": false
}'

curl --request POST 'http: //localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "What was our customer churn rate by region in 2025?",
    "user_context": {
        "user_id": "poc-user"
    },
    "include_trace": false
}'

curl --request POST 'http: //localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "Why did revenue increase in March 2025?",
    "user_context": {
        "user_id": "poc-user"
    },
    "include_trace": false
}'