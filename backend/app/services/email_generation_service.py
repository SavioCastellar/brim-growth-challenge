import logging
import json
import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv

from . import event_service
from app.models.event_model import OutboundEmail
from app.models.schemas import CompanyInput, ScoringOutput

load_dotenv(find_dotenv())

try:
    genai.configure(api_key="AIzaSyDDp6Q6Um8t5lpWTmfIEMrERG1Hsub5yyk")
except KeyError:
    logging.critical("FATAL ERROE: GEMINI_API_KEY environment variable is not defined.")
    raise RuntimeError("The API key from Gemini is not set.") from None


def determine_email_variant(company_data: CompanyInput, score: int) -> str:
    """
    Determines the best email variant based on company data.

    Args:
        company_data: A dictionary containing firmographics and intent signals.

    Returns:
        The name of the variant to use ('problem_focused' or 'roi_focused').
    """
    # Example signals from the challenge document
    tech_stack = company_data.tech_stack
    job_posts = company_data.recent_job_posts
    employee_count = company_data.employee_count
    funding_stage = company_data.funding_stage

    # Rule for 'problem_focused'
    if any(
        role in str(job_posts) for role in ["Operations", "Automation", "Process"]
    ) or any(tech in str(tech_stack) for tech in ["Zapier", "Make"]):
        logging.info(
            f"Choosing 'problem_focused' variant for {company_data.company_name} due to operational signals."
        )
        return "problem_focused"

    # Rule for 'roi_focused'
    if (
        employee_count > 75
        or "Series B" in funding_stage
        or "Series C" in funding_stage
    ):
        logging.info(
            f"Choosing 'roi_focused' variant for {company_data.company_name} due to scale/maturity."
        )
        return "roi_focused"

    if score > 75:
        logging.info(
            f"Defaulting to 'roi_focused' for high-scoring company {company_data.company_name}."
        )
        return "roi_focused"
    else:
        logging.info(
            f"Defaulting to 'problem_focused' for {company_data.company_name}."
        )
        return "problem_focused"


async def generate_and_save_email_content(
    db_provider, company_data: CompanyInput, scoring: ScoringOutput
):
    """
    Generates a single, targeted email variant and saves it to the database.
    """
    company_id = scoring.company_id
    company_name = company_data.company_name

    chosen_variant = determine_email_variant(company_data, scoring.total_score)

    logging.info(
        f"BACKGROUND TASK: Starting Gemini API call for {company_name} with variant: {chosen_variant}"
    )

    variant_prompts = {
        "problem_focused": "emphasizes the pain of managing workflows and how Brim solves it.",
        "roi_focused": "highlights how Brim saves time and money.",
    }

    prompt_text = f"""
    You are a copywriter specialized in sales for a B2B SaaS company called Brim, which offers "AI teammates" to automate workflows.

    Your target audience is companies with 30-300 employees.

    **Target Company Context:**
    - Company Name: {company_name}
    - Fit/Intent Score: {scoring.total_score}/100
    - Other Data: {company_data}

    **Your Task:**
    Generate one concise cold outreach email for this company. The email should be **{chosen_variant}**. This means it {variant_prompts[chosen_variant]}

    **Required Output Format:**
    Respond ONLY with a valid JSON object, with no explanation or additional text. The JSON must have the following structure:
    {{
      "variant_name": "{chosen_variant}",
      "subject": "<Email Subject Here>",
      "body": "<Email Body Here, using \\n for line breaks>"
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
            response = await model.generate_content_async(prompt_text)
            content = response.text
            logging.info(f"RAW RESPONSE FROM GEMINI API: {content}")

            variant = json.loads(content)

            if not all(k in variant for k in ["variant_name", "subject", "body"]):
                logging.warning(
                    f"Incomplete JSON received from API for {company_name}: {variant}"
                )
                return

            new_email = OutboundEmail(
                company_id=company_id,
                score=scoring.total_score,
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
                f"ERROR in async task for {company_name}. Error: {e}",
                exc_info=True,
            )

    logging.info(f"BACKGROUND TASK: Finished for {company_name}.")
