import os
import subprocess
from datetime import datetime
from typing import List

import markdown
from google import genai
from pydantic import BaseModel

from mail import push_mail

from dotenv import load_dotenv

# The innermost item
class Job(BaseModel):
    title: str


# The item representing each row (Company)
class Company(BaseModel):
    company_name: str
    open_jobs: List[Job]


# The overall response structure (The 2D-like list)
class CompanyJobListing(BaseModel):
    companies: List[Company]

load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))


def format_jobs_to_markdown(job_listing: CompanyJobListing) -> str:
    """
    Converts a CompanyJobListing Pydantic object into a
    structured Markdown string for email.
    """
    if not job_listing.companies:
        return "### No job listings found for the requested companies."

    markdown_lines = []
    markdown_lines.append(f"# Open Software Engineering Roles\n")
    markdown_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    markdown_lines.append("---")

    for company in job_listing.companies:
        if not company.open_jobs: continue
        markdown_lines.append(f"## 🏢 {company.company_name}")

        for job in company.open_jobs:
            # Using bold for titles and a blockquote-style feel for details
            markdown_lines.append(f"### **{job.title}**")
            markdown_lines.append("")  # Spacer between jobs

        markdown_lines.append("---")  # Separator between companies

    return "\n".join(markdown_lines)


def fetch_job_listings(company_list) -> CompanyJobListing:
    prompt = f"""
    Find open roles at these companies: {company_list}.
    Look in the company careers website as well as linkedin and indeed.
    Return a list for each company containing their open jobs.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': CompanyJobListing,
        }
    )

    # Access the data naturally
    parsed_response = response.parsed  # This is a CompanyJobListing object

    return parsed_response


if __name__ == "__main__":
    git_bash_path = "C:\\Program Files\\Git\\bin\\bash.exe"
    subprocess.run([git_bash_path, "-c", "./get_random"])

    file_path: str = "random_selection.txt"

    with open(file_path, "r", encoding='utf-8') as f:
        # Strip whitespace and ignore empty lines
        companies = [line.strip() for line in f if line.strip()]

    formatted_list = ", ".join(companies)

    job_listings: CompanyJobListing = fetch_job_listings(formatted_list)
    print(job_listings)
    jobs_count = any([len(c.open_jobs) > 0 for c in job_listings.companies])

    if jobs_count:
        push_mail(markdown.markdown(format_jobs_to_markdown(job_listings)))
