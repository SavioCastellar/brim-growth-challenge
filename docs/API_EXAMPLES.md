# API Request Examples

This document provides sample `cURL` commands to test the key endpoints of the Brim Growth API. This allows for easy validation of the core features without using the UI.

---

### 1. Score a Single Company

This endpoint scores a single company based on the provided data and asynchronously triggers the email generation process.

**Endpoint:** `POST /api/leads/score-company`

**cURL Command:**
```shell
curl -X 'POST' \
  'http://localhost:8000/api/leads/score-company' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_name": "QuantumLeap AI",
    "employee_count": 150,
    "industry": "AI",
    "tech_stack": ["Zapier", "AWS"],
    "recent_job_posts": ["Head of Operations"]
  }'
```

Sample JSON Body:
```
{
  "company_name": "QuantumLeap AI",
  "employee_count": 150,
  "industry": "AI",
  "tech_stack": ["Zapier", "AWS"],
  "recent_job_posts": ["Head of Operations"]
}
```


### 2. Score a Batch of Companies via JSON Upload

This endpoint accepts a JSON file containing a list of company objects and starts a background job to score all of them concurrently.

**Endpoint:** `POST /api/leads/batch-score`

Note: Create a file named sample-batch.json with the content below before running this command.

```
curl -X 'POST' \
  'http://localhost:8000/api/leads/batch-score' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@./sample-batch.json'
```

Content for sample-batch.json:
```
[
  {
    "company_name": "Innovatech Solutions",
    "employee_count": 120,
    "industry": "SaaS"
  },
  {
    "company_name": "DataDriven Corp",
    "employee_count": 250,
    "industry": "Fintech",
    "tech_stack": ["Zapier"]
  }
]
```

### 3. Log a Frontend Activation Event
This endpoint is used by the frontend to log user interactions during the activation flow. It's essential for building the activation funnel analytics.

**Endpoint:** `POST /api/activation/log-event`

cURL Command:
```
curl -X 'POST' \
  'http://localhost:8000/api/activation/log-event' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user_xyz_789",
    "step_name": "result_viewed",
    "metadata": {
      "insights_count": 3
    }
  }'
```

Sample JSON Body:
```
{
  "user_id": "user_xyz_789",
  "step_name": "result_viewed",
  "metadata": {
    "insights_count": 3
  }
}
```