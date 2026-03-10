"""Contact search and enrichment commands."""

import click

from .codegen import print_python, print_typescript
from .state import pass_state
from .output import print_json, print_kv, print_list_table


@click.group()
def contacts():
    """Contact search and enrichment.

    \b
    Examples:
      loopsh contacts search --dot 2247505
      loopsh contacts search --company "Swift" --levels c_suite,vp
      loopsh contacts enrich CONTACT_ID

    \b
    Agent workflow — find contacts then enrich:
      ID=$(loopsh --json contacts search --dot 2247505 | jq -r '.results[0].id')
      loopsh contacts enrich "$ID"
    """
    pass


@contacts.command()
@click.option("--dot", "dot_number", default=None, help="DOT number.")
@click.option("--company", "company_name", default=None, help="Company name.")
@click.option("--title", "job_title", default=None, help="Job title filter.")
@click.option("--levels", default=None, help="Comma-separated seniority levels (vp,director,manager,c_suite).")
@click.option("--page", default=1, type=int, help="Page number.")
@click.option("--limit", default=25, type=int, help="Results per page.")
@click.option("--no-retry", is_flag=True, help="Don't auto-retry on 202 (async fetch).")
@pass_state
def search(state, dot_number, company_name, job_title, levels, page, limit, no_retry):
    """Search for contacts at a carrier or company.

    \b
    Examples:
      loopsh contacts search --dot 2247505
      loopsh contacts search --company "Swift" --levels c_suite,vp
      loopsh --json contacts search --dot 2247505 | jq '.results[].name'
    """
    if not dot_number and not company_name:
        raise click.UsageError("Provide --dot or --company.")

    level_list = [l.strip() for l in levels.split(",")] if levels else None

    if state.codegen:
        kwargs = {
            "dot_number": dot_number, "company_name": company_name,
            "job_title": job_title, "job_title_levels": level_list,
            "page": page, "limit": limit,
        }
        fn = print_python if state.codegen == "python" else print_typescript
        fn("contacts.search", [], kwargs)
        return

    result = state.client.contacts.search(
        dot_number=dot_number, company_name=company_name,
        job_title=job_title, job_title_levels=level_list,
        page=page, limit=limit, auto_retry=not no_retry,
    )

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No contacts found.")
            return
        print_list_table(rows, ["name", "job_title", "seniority"], title="Contacts")


@contacts.command()
@click.argument("contact_id")
@pass_state
def enrich(state, contact_id):
    """Enrich a contact — get email, phone, work history (1 credit).

    \b
    Examples:
      loopsh contacts enrich CONTACT_ID
      loopsh --json contacts enrich CONTACT_ID
    """
    if state.codegen:
        fn = print_python if state.codegen == "python" else print_typescript
        fn("contacts.enrich", [contact_id])
        return

    result = state.client.contacts.enrich(contact_id)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        print_kv({
            "Name": data.get("name"),
            "Email": data.get("email"),
            "Phone": data.get("phone"),
            "Title": data.get("job_title"),
            "Company": data.get("company_name"),
            "LinkedIn": data.get("linkedin_url"),
        }, title="Enriched Contact")
