import json
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import config
from products import PRODUCTS, SERVICES, match_products


def _make_client() -> OpenAI:
    return OpenAI(api_key=config.deepseek_api_key, base_url=config.deepseek_base_url)


def _call_deepseek(
    client: OpenAI,
    system: str,
    user_content: Any,
    temperature: float = 0.4,
    json_mode: bool = True,
    fallback_text: Optional[str] = None
) -> str:
    """
    Calls DeepSeek. Tries with image content first (if list), then falls back to text-only.
    Returns raw string response.
    """
    kwargs = dict(
        model=config.deepseek_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content}
        ],
        temperature=temperature,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    except Exception:
        if fallback_text and isinstance(user_content, list):
            kwargs["messages"][1]["content"] = fallback_text
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        raise


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match_bracket = re.search(r"(\{.*\})", text, re.DOTALL)
    if match_bracket:
        return json.loads(match_bracket.group(1))
    raise ValueError("Could not parse JSON response")


# =============================================================================
# AGENT 1 — Business Pain Analyst
# Thinks like the business owner: what is COSTING them money/growth right now?
# =============================================================================
def agent_auditor(site_data: Dict[str, Any], client: OpenAI, dom_flags: List[str]) -> Dict[str, Any]:
    """
    Agent 1: Thinks purely as the BUSINESS OWNER looking at their own website.
    Finds real revenue-impacting problems — not technical HTML issues.
    Focus: lost sales, lost trust, missed conversions, weak positioning.
    """
    system = (
        "You are a sharp, experienced business owner reviewing your own company's website for the first time as a stranger would see it.\n"
        "Your lens is purely: 'Is this website making me money? Is it losing me customers? Does it make visitors TRUST me and take action?'\n\n"
        "RULES — VERY IMPORTANT:\n"
        "1. Think like a CUSTOMER visiting this site — not a developer or designer.\n"
        "2. Identify problems that COST the business money, trust, or customers. Skip technical jargon.\n"
        "3. Problems must be REAL and observable from the data/images. NEVER invent issues.\n"
        "4. If the site is genuinely good and would convert well, say so — has_errors = false.\n"
        "5. Frame every issue as a BUSINESS problem, not a technical one. Example:\n"
        "   BAD: 'H1 tag is missing'\n"
        "   GOOD: 'A visitor landing here has no idea within 3 seconds what this company does or why they should stay'\n"
        "6. Severity: High = actively losing customers RIGHT NOW. Medium = missing revenue opportunity. Low = trust/polish issue.\n"
        "7. Return valid JSON only."
    )

    text_prompt = f"""
You are visiting this website as a potential customer for the first time:

Business: {site_data.get('title')} — {site_data.get('domain')}
What they claim to do (meta): {site_data.get('meta_description')}
Page content (what a visitor actually reads): {site_data.get('text_sample', '')[:2000]}

Signals:
- Do they have a clear next step for visitors? CTAs found: {site_data.get('cta_found')}
- Can someone contact or inquire? Form present: {site_data.get('has_contact_or_lead_form')}
- Is there a live chat / support? {site_data.get('has_chat_widget')}
- Does the site load and look right on mobile? Viewport: {site_data.get('has_viewport')}
- Do they have strong visuals / product imagery? Images: {site_data.get('total_images')}
- Do they have clear navigation so visitors can explore? Nav: {site_data.get('has_navigation')}
- Pre-flagged technical signals (translate these to business impact): {dom_flags}
- Visual screenshots attached: {site_data.get('visual_image_count', 0)}

Ask yourself as a potential customer:
1. Within 5 seconds, do I know what this company does and why I should care?
2. Do I know what to do next — book, call, buy, sign up?
3. Do I trust this company enough to give them my contact or money?
4. Is anything confusing or frustrating me as I look around?
5. Am I going to leave and go to a competitor?

Report only REAL problems that would make a real customer leave or not convert.

Return JSON:
{{
  "has_errors": true or false,
  "customer_first_impression": "1-2 sentences — honest gut reaction a customer would have landing on this site",
  "errors_list": [
    {{
      "title": "Business-language problem title (not technical)",
      "severity": "High" | "Medium" | "Low",
      "impact": "Exact customer/revenue impact — what are they losing because of this?",
      "fix": "What needs to change — framed as a business improvement, not a code fix"
    }}
  ]
}}
"""

    content_items: List[Any] = [{"type": "text", "text": text_prompt}]
    for img_b64 in site_data.get("encoded_images", []):
        content_items.append({"type": "image_url", "image_url": {"url": img_b64}})

    raw = _call_deepseek(client, system, content_items, temperature=0.4, fallback_text=text_prompt)
    return _extract_json(raw)


# =============================================================================
# AGENT 2 — Growth Opportunity Spotter
# Thinks: "What is this business leaving on the table?"
# Maps real growth opportunities to our products — only the ones that FIT
# =============================================================================
def agent_strategist(site_data: Dict[str, Any], client: OpenAI) -> Dict[str, Any]:
    """
    Agent 2: Growth strategist.
    Looks at what competitors probably have, what this business is missing,
    and maps specific Element Labs products to real growth levers.
    Thinks in revenue, customers, efficiency — not features.
    """
    business_context = " ".join([
        site_data.get("domain", ""),
        site_data.get("title", ""),
        site_data.get("meta_description", ""),
        site_data.get("text_sample", "")[:1200]
    ])
    pre_matched = match_products(business_context, max_results=5)
    pre_matched_summary = "\n".join([
        f"- [{p['id']}] {p['name']} ({p['category']}): {p['short_desc']}"
        for p in pre_matched
    ]) or "No keyword match found — reason from business context."

    all_products_summary = "\n".join([
        f"[{p['id']}] {p['name']} ({p['category']}): {p['short_desc']}"
        for p in PRODUCTS
    ])

    system = (
        "You are a growth advisor who has helped 100+ businesses scale using the right digital tools.\n"
        "You look at a business and immediately see: What are they LEAVING ON THE TABLE?\n"
        "What are their competitors doing that they are not? What would double their lead volume or save their team 10 hours/week?\n\n"
        "Rules:\n"
        "1. Think in business outcomes: more customers, more revenue, less manual work, better retention.\n"
        "2. Only recommend things that make OBVIOUS sense for this exact business.\n"
        "3. For product matches: pick 1-3 from our portfolio. Only include ones that DIRECTLY solve a gap you spotted.\n"
        "4. Frame everything as 'Here is what this business is missing and what it would do for them' — not as features.\n"
        "5. Return valid JSON only."
    )

    text_prompt = f"""
Business website: {site_data.get('domain')}
What they do: {site_data.get('title')} — {site_data.get('meta_description')}
Page content: {site_data.get('text_sample', '')[:1500]}
Current digital tools detected: form={site_data.get('has_contact_or_lead_form')}, chat={site_data.get('has_chat_widget')}, ctas={site_data.get('cta_found')}

Our Product Portfolio (Element Labs):
{all_products_summary}

Keyword-scored pre-matches for context:
{pre_matched_summary}

As a growth advisor, identify:
1. What WEBSITE opportunity would bring them more leads if fixed today?
2. Would a MOBILE APP open a new revenue channel or improve customer experience?
3. Is there an AUTOMATION or AI workflow that would save them time or find them more customers?
4. Which 1-3 of our products are a genuine fit — and what exact gap do they fill for this business?

Do not list all products. Only list what truly applies.

Return JSON:
{{
  "business_summary": "2-sentence description of what this business does and who their customers are",
  "biggest_missed_opportunity": "The single most impactful thing they are leaving on the table right now",
  "website_opportunities": [
    {{"opportunity": "What they should add/change", "business_impact": "What this would do for their revenue/leads"}}
  ],
  "mobile_app_opportunities": [
    {{"opportunity": "Mobile channel or feature", "business_impact": "New revenue or better retention"}}
  ],
  "automation_opportunities": [
    {{"opportunity": "Specific automation or AI", "business_impact": "Hours saved or leads generated"}}
  ],
  "relevant_products": [
    {{
      "product_id": "id from portfolio",
      "product_name": "Name",
      "category": "Category",
      "gap_it_fills": "What this business is currently doing WITHOUT this product (the pain)",
      "what_it_does_for_them": "Specific outcome for their exact business — in plain English",
      "pitch_line": "One compelling sentence framed as a benefit, not a feature"
    }}
  ]
}}
"""

    raw = _call_deepseek(client, system, text_prompt, temperature=0.5)
    return _extract_json(raw)


# =============================================================================
# AGENT 3 — Human Outreach Writer
# Writes as a person who genuinely understands the client's business.
# Not a sales template. Sounds like a smart peer reaching out.
# =============================================================================
def agent_outreach_drafter(
    site_data: Dict[str, Any],
    audit_result: Dict[str, Any],
    strategy_result: Dict[str, Any],
    client: OpenAI
) -> Dict[str, Any]:
    """
    Agent 3: Human outreach writer.
    Writes as someone who genuinely spent time on their site and thought about their business.
    Format: Problem Identified (business pain, not tech) → Our Solution (specific product/outcome).
    """
    errors = audit_result.get("errors_list", [])
    has_errors = audit_result.get("has_errors", False)
    first_impression = audit_result.get("customer_first_impression", "")
    biggest_opportunity = strategy_result.get("biggest_missed_opportunity", "")
    products = strategy_result.get("relevant_products", [])
    business_summary = strategy_result.get("business_summary", "")

    # Build a rich context for the writer
    pain_points = "\n".join([
        f"- {e.get('title')}: {e.get('impact')}" for e in errors[:3]
    ]) or "Site is reasonably solid — opportunity is more about growth than fixing."

    product_pitches = "\n".join([
        f"- {p.get('product_name')}: {p.get('what_it_does_for_them')} | Pitch: {p.get('pitch_line')}"
        for p in products[:2]
    ]) or "General digital solutions from our Element Labs portfolio."

    system = (
        f"You are Raza Shaikh from Movenetics. You are a smart, direct person — not a salesperson.\n"
        f"You genuinely spent 10 minutes on this business's website and thought hard about their situation.\n"
        f"You are reaching out as a peer who spotted something useful, not as someone pitching a product.\n\n"
        f"TONE:\n"
        f"- Conversational, warm, specific — not corporate or salesy\n"
        f"- Reference something REAL and SPECIFIC about their business (not 'I noticed your site')\n"
        f"- Make them feel: 'This person actually understands my business'\n"
        f"- The recommended solution should feel like an obvious win for THEM, not a sale for you\n\n"
        f"FORMAT:\n"
        f"msg: Max 3 sentences. 1 specific observation → 1 specific solution → soft CTA. Under 80 words.\n"
        f"email: 3 short paragraphs (not long walls of text):\n"
        f"  Paragraph 1 — Problem Identified: Reference something specific about their business/site. What's it costing them.\n"
        f"  Paragraph 2 — Our Solution: Name the specific product/feature. Frame it as an outcome, not a feature list.\n"
        f"  Paragraph 3 — CTA: One relaxed line. No pressure.\n"
        f"  Sign-off: '{config.sender_name}\\nMovenetics\\n{config.sender_email}'\n\n"
        f"Return valid JSON only."
    )

    text_prompt = f"""
Business: {site_data.get('domain')}
What they do: {business_summary}

As a potential customer, the first impression is:
"{first_impression}"

Real problems costing them customers or revenue:
{pain_points}

The biggest thing they are missing:
{biggest_opportunity}

What we can specifically offer them:
{product_pitches}

Write the outreach. Make it feel like it came from a sharp person who cares, not a template.

Return JSON:
{{
  "draft_msg": "Short DM — specific observation, specific solution, soft CTA. Max 80 words. No corporate words.",
  "draft_email_subject": "Specific to their business — sounds like a peer emailing, not a sales pitch. 4-7 words.",
  "draft_email_body": "Full email:\\nP1: Problem Identified (specific, business-language)\\nP2: Our Solution (specific product/outcome, what it does FOR THEM)\\nP3: Soft CTA (one relaxed sentence)\\n\\nSign off as Raza Shaikh\\nMovenetics\\nraza.shaikh@moveneticsdigital.com"
}}
"""

    raw = _call_deepseek(client, system, text_prompt, temperature=0.7)
    return _extract_json(raw)


# =============================================================================
# MAIN ORCHESTRATOR — runs all 3 agents, merges results
# =============================================================================
class WebsiteAnalyzer:
    def __init__(self):
        self.client = _make_client()

    def analyze(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in site_data:
            return {"success": False, "error": site_data["error"], "url": site_data.get("url", "")}

        # Quick deterministic pre-checks (translated to business language)
        dom_flags = []
        if not site_data.get("has_viewport"):
            dom_flags.append("Site breaks on mobile — most visitors today are on their phones")
        if site_data.get("h1_count", 0) == 0:
            dom_flags.append("Visitor lands with no clear headline — unclear what this company does in the first 3 seconds")
        if site_data.get("total_images", 0) > 2 and site_data.get("images_missing_alt", 0) >= site_data.get("total_images", 1) * 0.75:
            dom_flags.append("Visuals not indexed by Google — missing search traffic from product/service image searches")
        if not site_data.get("has_cta"):
            dom_flags.append("Visitor has no clear next step — interested people leave without contacting")
        if not site_data.get("has_contact_or_lead_form"):
            dom_flags.append("No way to capture a lead — potential customers have to hunt for a contact option")
        if site_data.get("placeholder_links_count", 0) > 4:
            dom_flags.append("Several buttons/links go nowhere — makes the site feel unfinished and hurts trust")

        try:
            audit = agent_auditor(site_data, self.client, dom_flags)
            strategy = agent_strategist(site_data, self.client)
            outreach = agent_outreach_drafter(site_data, audit, strategy, self.client)

            return {
                "success": True,
                "has_errors": audit.get("has_errors", len(dom_flags) > 0),
                "customer_first_impression": audit.get("customer_first_impression", ""),
                "errors_list": audit.get("errors_list", []),
                "business_summary": strategy.get("business_summary", ""),
                "biggest_missed_opportunity": strategy.get("biggest_missed_opportunity", ""),
                "website_opportunities": strategy.get("website_opportunities", []),
                "mobile_app_opportunities": strategy.get("mobile_app_opportunities", []),
                "automation_opportunities": strategy.get("automation_opportunities", []),
                "relevant_products": strategy.get("relevant_products", []),
                "draft_msg": outreach.get("draft_msg", ""),
                "draft_email_subject": outreach.get("draft_email_subject", ""),
                "draft_email_body": outreach.get("draft_email_body", ""),
                "site_info": site_data,
            }

        except Exception as e:
            return self._fallback(site_data, dom_flags, str(e))

    def _fallback(self, site_data: Dict[str, Any], dom_flags: List[str], err: str) -> Dict[str, Any]:
        domain = site_data.get("domain", "your website")
        has_errors = len(dom_flags) > 0
        business_context = " ".join([
            site_data.get("domain", ""),
            site_data.get("title", ""),
            site_data.get("text_sample", "")[:500]
        ])
        matched = match_products(business_context, max_results=2)
        errors_list = [{"title": f, "severity": "Medium", "impact": f, "fix": "Worth addressing"} for f in dom_flags]
        products_out = [{"product_name": p["name"], "category": p["category"], "pitch_line": p["pitch"]} for p in matched]

        draft_msg = (
            f"Hey — I spent some time on {domain}. "
            + (f"Right now, {dom_flags[0].lower()} which I think is costing you leads. " if dom_flags else "Site's solid overall. ")
            + f"At Movenetics we can fix this fast — open to a quick look? — Raza"
        )
        return {
            "success": True,
            "has_errors": has_errors,
            "customer_first_impression": "",
            "errors_list": errors_list,
            "business_summary": "",
            "biggest_missed_opportunity": "",
            "website_opportunities": [],
            "mobile_app_opportunities": [],
            "automation_opportunities": [],
            "relevant_products": products_out,
            "draft_msg": draft_msg,
            "draft_email_subject": f"Spotted something on {domain}",
            "draft_email_body": f"Hi,\n\nProblem Identified:\nI checked out {domain} — {dom_flags[0].lower() if dom_flags else 'some real growth opportunities visible'}.\n\nOur Solution:\nAt Movenetics we have {'a ready-to-deploy ' + matched[0]['name'] if matched else 'tools'} that would change this.\n\nWould a quick 10 min call make sense?\n\n{config.sender_name}\nMovenetics\n{config.sender_email}",
            "site_info": site_data,
            "api_note": err
        }
