# Lead Scoring Methodology

*"There is a tide in the affairs of men, which taken at the flood, leads on to fortune"
(William Shakespeare)*

## 1. Overview

This document outlines the methodology used by the Smart Lead Scoring Engine to prioritize prospective companies for Brim. The goal is to identify companies that closely match our Ideal Customer Profile (ICP) and are demonstrating signals of purchase intent.

Our scoring is divided into two primary categories:
-   **Fit Score:** How well does this company match our ICP? (e.g., size, industry)
-   **Intent Score:** Is this company showing behaviors that suggest they need a solution like Brim *now*? (e.g., hiring, tech stack)

The final `total_score` is a weighted average of these two scores.

## 2. Signal Breakdown

We use a combination of firmographic, technographic, and intent signals to build our scores.

### Fit Score Signals

| Signal | Rationale | Scoring Rules |
| :--- | :--- | :--- |
| **Employee Count** | Brim provides the most value to mid-sized companies (30-300 employees) that are large enough to have workflow pain but small enough to adopt new tools quickly. | - **100 pts:** 30-300 employees<br>- **50 pts:** 15-29 or 301-500 employees<br>- **0 pts:** All others |
| **Industry** | Tech-forward industries (SaaS, Fintech, AI) are more likely to understand and adopt AI-powered workflow automation. | - **100 pts:** SaaS, Fintech, AI, Technology<br>- **60 pts:** E-commerce, Biotech, Education |

### Intent Score Signals

| Signal | Rationale | Scoring Rules |
| :--- | :--- | :--- |
| **Automation Tech** | Companies already using tools like Zapier or HubSpot have a demonstrated need for integration and automation and are easier to sell to. | - **100 pts:** Uses Zapier, Make, HubSpot, etc.<br>- **20 pts:** Uses other tech but not automation-specific tools. |
| **Hiring: Operations** | Companies hiring for "Operations" or "Automation" roles are actively feeling the pain that Brim solves. This is a very strong buying signal. | - **100 pts:** Job posts contain keywords like 'Operations', 'Ops', 'Automation Engineer'. |

## 3. Final Calculation

-   The **Fit Score** is the average of all calculated Fit signals.
-   The **Intent Score** is the average of all calculated Intent signals.
-   The **Total Score** is calculated as: `(Fit Score * 0.6) + (Intent Score * 0.4)`.

This model prioritizes finding the right type of company first (Fit) and then looks for signs that it's the right time to reach out (Intent).