import logging
import json
import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from app.models.event_model import OutboundEmail
from . import event_service
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

try:
    genai.configure(api_key="AIzaSyDDp6Q6Um8t5lpWTmfIEMrERG1Hsub5yyk")
except KeyError:
    logging.critical(
        "FATAL ERROE: GEMINI_API_KEY environment variable is not defined."
    )
    raise RuntimeError("The API key from Gemini is not set.") from None


def generate_and_save_email_content(
    db_provider, company_id: str, company_name: str, score: int
):
    """
    Generates email content using Gemini API with JSON mode and saves it to the database.
    """
    logging.info(
        f"BACKGROUND TASK: Starting Gemini API call to: {company_name}"
    )

    prompt_text = f"""
    You are a copywriter specialized in sales for a B2B SaaS company called Brim, which offers "AI teammates" to automate workflows.

    Your target audience is companies with 30-300 employees.

    **Target Company Context:**
    - Company Name: {company_name}
    - Fit/Intent Score: {score}/100

    **Your Task:**
    Generate two distinct variants of a concise cold outreach email for this company. The variants should be:
    1. **'problem_focused'** - emphasizes the pain of managing workflows and how Brim solves it.
    2. **'roi_focused'** - highlights how Brim saves time and money.

    **Required Output Format:**
    Respond ONLY with a valid JSON object, with no explanation or additional text. The JSON must have the following structure:
    {{
    "variants": [
        {{
        "variant_name": "problem_focused",
        "subject": "<Email Subject Here>",
        "body": "<Email Body Here, using \\n for line breaks>"
        }},
        {{
        "variant_name": "roi_focused",
        "subject": "<Email Subject Here>",
        "body": "<Email Body Here, using \\n for line breaks>"
        }}
    ]
    }}
    """

    db: Session
    with db_provider() as db:
        try:
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json"
            )
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config=generation_config,
            )

            logging.info(
                f"BACKGROUND TASK:  Model instantiated. Generating content for {company_name}."
            )
            response = model.generate_content(prompt_text)

            content = response.text

            logging.info(f"RAW RESPONSE FROM GEMINI API: {content}")

            email_data = json.loads(content)

            for variant in email_data.get("variants", []):
                if not all(k in variant for k in ["variant_name", "subject", "body"]):
                    logging.warning(
                        f"Incomplete JSON variant received from API for {company_name}: {variant}"
                    )
                    continue

                new_email = OutboundEmail(
                    company_id=company_id,
                    score=score,
                    email_subject=variant.get("subject"),
                    email_body=variant.get("body"),
                    variant_name=variant.get("variant_name"),
                )
                db.add(new_email)
                db.commit()
                db.refresh(new_email)

                event_service.log_email_generated_event(db, new_email)
                logging.info(
                    f"BACKGROUND TASK: Variant '{variant.get('variant_name')}' saved with ID: {new_email.id}"
                )

        except json.JSONDecodeError as je:
            logging.error(
                f"JSON DECODING ERROR for {company_name}. API response was not valid JSON. Error: {je}",
                exc_info=True,
            )
            logging.error(f"Problematic content: {content}")
        except Exception as e:
            logging.error(
                f"ERROR in background task for {company_name}. Error: {e}", exc_info=True
            )

    logging.info(f"BACKGROUND TASK: Finished for {company_name}.")
