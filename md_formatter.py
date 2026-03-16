from main import CompanyJobListing


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
        markdown_lines.append(f"## 🏢 {company.company_name}")

        if not company.open_jobs:
            markdown_lines.append("*No open positions found at this time.*\n")
            continue

        for job in company.open_jobs:
            # Using bold for titles and a blockquote-style feel for details
            markdown_lines.append(f"### **{job.title}**")
            markdown_lines.append(f"- **Location:** {job.location}")
            markdown_lines.append(f"- **Salary Range:** {job.salary_range}")
            markdown_lines.append("")  # Spacer between jobs

        markdown_lines.append("---")  # Separator between companies

    return "\n".join(markdown_lines)