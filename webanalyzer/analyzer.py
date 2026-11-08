import json
import re
from typing import Dict, Any, List
from openai import OpenAI
from config import config


class WebsiteAnalyzer:
    def __init__(self):
        self.api_key = config.deepseek_api_key
        self.base_url = config.deepseek_base_url
        self.model = config.deepseek_model

    def analyze(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the website using DeepSeek multimodal vision and text data.
        Inspects UI/UX errors with strict accuracy rules, identifies features to add,
        and drafts terminal msg and mail using Raza Shaikh (no team lead title).
        """
        if "error" in site_data:
            return {
                "success": False,
                "error": site_data["error"],
                "url": site_data.get("url", "")
            }

        # Deterministic checks gathered from DOM
        dom_flags = []
        if not site_data.get("has_viewport"):
            dom_flags.append("Critical: Missing <meta name='viewport'> tag (site is not mobile-responsive).")
        if site_data.get("h1_count", 0) == 0:
            dom_flags.append("Medium: Missing primary <h1> heading tag (hurts accessibility, hierarchy, and SEO).")
        if site_data.get("total_images", 0) > 0 and site_data.get("images_missing_alt", 0) == site_data.get("total_images", 0):
            dom_flags.append(f"Low/Accessibility: All {site_data.get('total_images')} images lack alt text descriptions.")
        if not site_data.get("has_cta"):
            dom_flags.append("High/UX: No clear Call to Action (CTA) buttons or next steps detected on the page.")
        if site_data.get("placeholder_links_count", 0) > 4:
            dom_flags.append(f"Medium/UX: Found {site_data.get('placeholder_links_count')} empty placeholder links (href='#').")

        system_prompt = (
            "You are a strict, senior UI/UX auditor, visual designer, and product strategist at Movenetics.\n"
            "Your company, Movenetics, helps businesses fix website design/technical flaws and build modern high-converting features.\n\n"
            "CRITICAL RULES - STRICT ACCURACY:\n"
            "1. You are provided with real visual images/screenshots of the website along with DOM structural data. Inspect the visual layout, contrast, whitespace, visual hierarchy, and readability.\n"
            "2. DO NOT invent, exaggerate, or hallucinate UI/UX errors. If the website is clean, modern, properly structured, and has no notable errors, you MUST set 'has_errors' to false and explicitly state: 'No significant UI/UX errors detected.'\n"
            "3. Only report genuine, demonstrable visual or structural errors based on the provided images and data.\n"
            "4. For features: Recommend 2-3 realistic, high-impact features that make sense for this specific business (e.g. AI booking assistant, interactive quote calculator, customer portal, automated scheduling).\n"
            "5. Sender Identity: Write ONLY the name 'Raza Shaikh' and 'Movenetics' (do NOT include any title like 'Team Lead' or 'Solutions Lead').\n"
            "6. Output MUST be valid JSON only."
        )

        user_prompt_text = f"""
Analyze this website:
- Domain: {site_data.get('domain')}
- URL: {site_data.get('url')}
- Title: {site_data.get('title')}
- Meta Description: {site_data.get('meta_description')}
- Mobile Viewport Present: {site_data.get('has_viewport')}
- H1 Headings: {site_data.get('h1_tags')} (Total count: {site_data.get('h1_count')})
- Headings: H2: {site_data.get('h2_count')}, H3: {site_data.get('h3_count')}
- Images on page: {site_data.get('total_images')} (Missing alt: {site_data.get('images_missing_alt')})
- Visual Screenshots/Images Attached: {site_data.get('visual_image_count', 0)}
- CTAs Found: {site_data.get('cta_found')}
- Has Form: {site_data.get('has_contact_or_lead_form')}
- Has Navigation: {site_data.get('has_navigation')}
- Has Chat Widget: {site_data.get('has_chat_widget')}
- Deterministic Flags: {dom_flags}
- Visible Text Sample: {site_data.get('text_sample')[:1800]}

Sender Information:
- Name: {config.sender_name}
- Company: {config.company_name}
- Email: {config.sender_email}
- Note: DO NOT use any title like 'Team Lead' or 'Solutions Lead'. Just use '{config.sender_name}'.

Return JSON strictly matching this format:
{{
  "has_errors": true_or_false,
  "ui_ux_status": "ERRORS_FOUND" or "NO_ERRORS_FOUND",
  "errors_summary": "Clean sentence summarizing errors, or 'No significant UI/UX errors detected.'",
  "errors_list": [
    {{
      "title": "Short title of issue",
      "severity": "High" | "Medium" | "Low",
      "impact": "Why it hurts conversions or user experience",
      "solution": "How Movenetics can fix it"
    }}
  ],
  "features_to_add": [
    {{
      "feature_name": "Feature Title",
      "benefit": "Why this business needs it",
      "how_it_works": "Brief description of the feature"
    }}
  ],
  "draft_msg": "Concise DM (under 90 words) tailored to the findings. Pitching Movenetics directly and naturally.",
  "draft_email_subject": "3 to 6 word engaging subject line",
  "draft_email_body": "Complete cold email body with greeting, specific site observations, Movenetics solution, low-friction CTA, and signature: Raza Shaikh, Movenetics, raza.shaikh@moveneticsdigital.com."
}}
"""

        # Construct multimodal message content with visual images
        content_items: List[Dict[str, Any]] = [
            {"type": "text", "text": user_prompt_text}
        ]

        encoded_images = site_data.get("encoded_images", [])
        for img_b64 in encoded_images:
            content_items.append({
                "type": "image_url",
                "image_url": {"url": img_b64}
            })

        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            try:
                # First attempt: with multimodal image inputs
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content_items}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
            except Exception:
                # If image payload is rejected or times out, fallback to text-only completion
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt_text}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

            raw = response.choices[0].message.content or "{}"
            result = self._extract_json(raw)
            result["success"] = True
            result["site_info"] = site_data
            return result

        except Exception as e:
            return self._fallback_analysis(site_data, dom_flags, error_note=str(e))

    def _extract_json(self, text: str) -> Dict[str, Any]:
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

        raise ValueError("Could not parse JSON response from DeepSeek API")

    def _fallback_analysis(self, site_data: Dict[str, Any], dom_flags: List[str], error_note: str = "") -> Dict[str, Any]:
        """Provides deterministic fallback when API is offline."""
        domain = site_data.get("domain", "your website")
        has_errors = len(dom_flags) > 0

        errors_list = []
        for flag in dom_flags:
            parts = flag.split(":", 1)
            sev = parts[0].strip() if len(parts) > 1 else "Medium"
            desc = parts[1].strip() if len(parts) > 1 else flag
            errors_list.append({
                "title": desc.split("(")[0].strip(),
                "severity": sev,
                "impact": "Causes friction for prospective visitors and reduces conversions.",
                "solution": f"{config.company_name} can optimize and fix this directly."
            })

        features_to_add = [
            {
                "feature_name": "AI Customer Assistant / Booking Agent",
                "benefit": "Engages visitors 24/7, answers product questions, and captures qualified leads automatically.",
                "how_it_works": "Custom-trained AI widget embedded seamlessly into the site."
            },
            {
                "feature_name": "Interactive Quote / Estimation Calculator",
                "benefit": "Gives instant value to high-intent buyers and dramatically increases form completions.",
                "how_it_works": "Step-by-step interactive calculator tailored to your service pricing."
            }
        ]

        if has_errors:
            error_headline = errors_list[0]["title"]
            draft_msg = (
                f"Hi there! Came across {domain} while researching businesses in your space. "
                f"Noticed a couple of UX friction points (specifically {error_headline.lower()}) that might be hurting your conversion rate. "
                f"We help brands fix these at {config.company_name} and add modern high-converting features. "
                f"Would you be open to a quick 5-min chat on how we'd fix this? — {config.sender_name}, {config.company_name}"
            )
            email_subject = f"Quick UX observation on {domain}"
            email_body = (
                f"Hi there,\n\n"
                f"I was recently reviewing {domain} and noticed a few quick UI/UX improvements that could help boost your conversions:\n\n"
                f"• {error_headline} — currently creating friction for prospective clients.\n"
                f"• Opportunity to introduce an automated booking/quote workflow to capture high-intent visitors.\n\n"
                f"At {config.company_name}, we specialize in optimizing websites and engineering custom digital features that turn more traffic into booked clients.\n\n"
                f"Would you be open to a quick 10-minute walkthrough this week to see a quick preview of how we'd improve this?\n\n"
                f"Best regards,\n"
                f"{config.sender_name}\n"
                f"{config.company_name}\n"
                f"{config.sender_email}"
            )
        else:
            draft_msg = (
                f"Hi there! Checked out {domain}—really clean and solid design overall. "
                f"We work with companies at {config.company_name} building modern conversion tools like AI client assistants and interactive quote engines. "
                f"Would you be open to seeing a 2-minute demo of how that could work for {domain}? — {config.sender_name}, {config.company_name}"
            )
            email_subject = f"Feature idea for {domain}"
            email_body = (
                f"Hi there,\n\n"
                f"I recently took a look at {domain}—great clean design and brand presentation.\n\n"
                f"We noticed an opportunity to add an interactive customer feature (such as an automated AI lead capture assistant or dynamic quote tool) to help turn more of your daily visitors into qualified inquiries.\n\n"
                f"At {config.company_name}, we design and build these custom features rapidly without disrupting your current site.\n\n"
                f"Would you be open to a quick 5-minute chat to see a preview of what this could look like for {domain}?\n\n"
                f"Best regards,\n"
                f"{config.sender_name}\n"
                f"{config.company_name}\n"
                f"{config.sender_email}"
            )

        return {
            "success": True,
            "has_errors": has_errors,
            "ui_ux_status": "ERRORS_FOUND" if has_errors else "NO_ERRORS_FOUND",
            "errors_summary": f"Detected {len(errors_list)} UI/UX improvement areas." if has_errors else "No significant UI/UX errors detected.",
            "errors_list": errors_list,
            "features_to_add": features_to_add,
            "draft_msg": draft_msg,
            "draft_email_subject": email_subject,
            "draft_email_body": email_body,
            "site_info": site_data,
            "api_note": error_note
        }
