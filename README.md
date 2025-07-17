# Brim - Product & Growth Engineering Challenge

This repository contains the full-stack implementation for the Brim Product & Growth Engineering Challenge. It includes three integrated systems designed to enhance growth operations: a smart lead scoring engine, a personalized email automation pipeline, and an analytics dashboard with a user activation flow.

## Prerequisites
Before you begin, ensure you have the following software installed on your local machine. The project is fully containerized, so you do not need to install Python or Node.js on your host system.

- Git

- Docker Desktop (must be running)

## Setting the project up
Follow these steps to set up and run the project locally.

**1. Clone the Repository**
First, clone the project repository to your local machine.
```
git clone https://github.com/SavioCastellar/brim-growth-challenge.git
```

**2. Navigate to the Project Directory**

```
cd brim-growth-challenge
```

**3. Build and Run the Application**
This project uses Docker Compose to build all the necessary images and run all services with a single command.

```
docker-compose up --build
```

This command will:
- Pull the official python:3.9 and node:18 base images.
- Build the custom images for the backend and frontend services.
- Install all Python and Node.js dependencies inside the containers.
- Start the FastAPI backend server and the Next.js frontend development server.


**4. Access the Application**
Once the containers are running, the application will be available at the following URLs:

- Frontend Application (Dashboard): http://localhost:3000
- Backend API Docs (FastAPI): http://localhost:8000/docs

---
Pages Available:
- http://localhost:3000/dashboard
- http://localhost:3000/activation

## Key Features

#### Smart Lead Scoring Engine
The core of the growth engine is a lead scoring system that ranks prospects based on firmographic, technographic, and intent data. The system categorizes leads into "Fit" and "Intent" scores to help prioritize outreach.

For a detailed breakdown of the signals used and their weighting, please see the [**Lead Scoring Methodology**](./docs/SCORING_METHODOLOGY.md).

#### AI-Powered Email Generation
Upon successful scoring, an asynchronous background task is initiated to generate personalized email copy using the Gemini API. This process is non-blocking and operates as follows:

- **Personalized Prompts**: A detailed prompt, including the specific company's data (name, score, industry), is sent to the Gemini API.

- **A/B Variant Creation**: The system is instructed to generate multiple email variants (e.g., "problem-focused" and "roi-focused") to allow for performance testing of different outreach strategies.

- **Database Queue**: The generated emails are saved to an outbound_emails table, effectively creating a prioritized queue for the sending service.

#### Prioritized Email Worker
A scheduled background worker, powered by APScheduler, runs periodically to send the generated emails. This system is designed for efficiency and resilience:

- **Prioritization**: The worker queries the database for unsent emails, prioritizing those associated with the highest-scoring leads first.

- **Decoupled & Stateful**: The sending process is completely separate from the generation process. The worker updates an is_sent flag for each email to ensure it is only sent once and that only one variant is sent per company.

- **Scalable**: The worker processes emails in small batches, a pattern that can be scaled to handle a large volume of outreach without overwhelming email servers.


## Tests

To run the tests, execute the following command:
```
docker-compose exec backend pytest -s --cov=app
```

## Future Work

#### Improvements for System 1: Smart Lead Scoring Engine
##### Predictive Machine Learning Model:

**What:** Replace the weighted sum logic with a trained machine learning model (e.g., Logistic Regression or Gradient Boosting). Feedback data from the "Feedback Loop" would be used to train this model.

**Why:** To significantly improve scoring accuracy by uncovering non-obvious patterns in the data that correlate with sales success.

##### Real-Time Data Enrichment:

**What:** Integrate the service with third-party data enrichment APIs (such as the ones mentioned in the challenge, like Apollo.io, or others like Clearbit). When a lead enters, the system would automatically fetch missing data such as `funding_stage`, `employee_count`, and `tech_stack`.

**Why:** To improve the quality and completeness of input data, resulting in more accurate scores and a more reliable confidence score.

##### NLP for Deep Intent Analysis:

**What:** Apply more advanced Natural Language Processing (NLP) techniques to the `news_mentions` and `recent_job_posts` fields. This could involve entity extraction, sentiment analysis, or classifying the type of news/job post.

**Why:** To capture much subtler buying signals than simple keyword matching. For example, distinguishing between news about "cost-cutting" and "market expansion."

##### Full Feedback Loop Implementation:

**What:** Build the `/api/report-outcome` endpoint that allows an external system (like a CRM) to report the outcome of a lead (e.g., `demo_booked`, `closed_won`, `not_a_fit`).

**Why:** To close the data loop. This transforms the scoring system from a static tool into one that learns and self-optimizes based on real-world results.

#### Improvements for System 2: Email Automation Pipeline
##### Advanced Retry Logic:

**What:** Enhance the sending worker. If sending an email fails, instead of giving up, use the `send_attempts` and `last_attempt_at` columns to implement retry logic with exponential backoff (e.g., wait 5 min, then 15 min, then 1h, etc.).

**Why:** To increase the resilience and delivery rate of the system by intelligently handling temporary network or API failures.

##### Dynamic Template Fallback:

**What:** If the AI API call fails, instead of using a single fallback template, have multiple templates and choose the most appropriate one based on the lead's data (e.g., one template for the "SaaS" industry, another for "Fintech").

**Why:** To improve the quality of the fallback experience by maintaining some level of personalization even when the main AI system is unavailable.

##### Intelligent Scheduling (Timezone-Aware):

**What:** Add a timezone field to the company profile. The sending worker would use this information to schedule email deliveries at optimal times in the lead’s local timezone (e.g., 10 AM on a Tuesday).

**Why:** To drastically increase open and response rates by delivering the message when it’s most likely to be read.
