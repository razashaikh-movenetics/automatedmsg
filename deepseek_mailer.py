import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI
from config import config


class DeepSeekMailer:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.deepseek_api_key
        self.base_url = base_url or config.deepseek_base_url
        self.model = model or config.deepseek_model

    def generate_personalized_email(
        self,
        receiver_email: str,
        receiver_name: str,
        receiver_wants: str,
        product_available: str,
        tone: str = "consultative and high-impact",
        custom_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Generates a tailored email pitch matching the prospect's need to our available product.
        Returns a dict with: 'subject', 'body_text', 'body_html', 'key_angle'.
        """
        # If API key is not configured, fallback gracefully to template generation
        if not self.api_key or self.api_key.startswith("your_"):
            return self._generate_fallback(
                receiver_name=receiver_name,
                receiver_wants=receiver_wants,
                product_available=product_available
            )

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        system_prompt = (
            "You are an elite B2B sales copywriter and executive outreach specialist. "
            "Your objective is to craft an authentic, high-converting, personalized cold email. "
            "You directly bridge what the receiver wants/needs with the exact product or solution available.\n\n"
            "Rules for effective outreach:\n"
            "1. Subject line: 3 to 6 words, relevant, no clickbait or spam words.\n"
            "2. Opening: Address the receiver naturally, acknowledging their specific requirement or pain point.\n"
            "3. Value pitch: Clearly explain how our available product directly satisfies their need.\n"
            "4. Brevity: Keep the body crisp (under 140 words). No unnecessary corporate fluff.\n"
            "5. Call to Action: Low-friction (e.g. 'Open to a brief 10-minute walkthrough this week?').\n"
            "6. Sign-off: Must use sender's exact name, company, and contact.\n"
            "7. Return JSON ONLY with keys: 'subject', 'body_text', 'body_html', 'key_angle'."
        )

        user_prompt = f"""
Prospect / Receiver Information:
- Name/Company: {receiver_name or 'there'}
- Email: {receiver_email}
- What Receiver Wants / Needs / Pain Point: {receiver_wants}

Product / Solution Available:
- Product/Service: {product_available}

Sender Information:
- Name: {config.sender_name}
- Title: {config.sender_title}
- Company: {config.sender_company}
- Email: {config.sender_email}

Tone: {tone}
{f'Additional Instructions: {custom_instructions}' if custom_instructions else ''}

Return ONLY valid JSON matching this schema:
{{
  "subject": "Compelling subject line",
  "body_text": "Plain text email with clean paragraphs",
  "body_html": "<p>Clean HTML formatted email version</p>",
  "key_angle": "Brief explanation of how the pitch bridges their requirement"
}}
"""

        raw_content = ""
        try:
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                raw_content = response.choices[0].message.content or ""
            except Exception:
                # If json_object mode fails (e.g. model incompatibility), fallback to standard completion
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                raw_content = response.choices[0].message.content or ""

            data = self._extract_json(raw_content)

            # Ensure expected fields exist
            if not data.get("subject") or not data.get("body_text"):
                raise ValueError("Parsed JSON missing required 'subject' or 'body_text'")

            if not data.get("body_html"):
                data["body_html"] = f"<div style='font-family: Arial, sans-serif; line-height: 1.6;'>{data['body_text'].replace(chr(10), '<br>')}</div>"

            return data

        except Exception as e:
            # Fallback to local template if API call fails or is blocked
            fallback = self._generate_fallback(
                receiver_name=receiver_name,
                receiver_wants=receiver_wants,
                product_available=product_available
            )
            fallback["warning"] = f"DeepSeek API notice: {str(e)} (used fallback generator)"
            return fallback

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extracts JSON object from text even if enclosed in markdown code fences."""
        text = text.strip()
        # Direct parse attempt
        try:
            return json.loads(text)
        except Exception:
            pass

        # Regex search for ```json ... ``` or { ... }
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        match_bracket = re.search(r"(\{.*\})", text, re.DOTALL)
        if match_bracket:
            return json.loads(match_bracket.group(1))

        raise ValueError("Could not parse JSON from model output")

    def _generate_fallback(
        self,
        receiver_name: str,
        receiver_wants: str,
        product_available: str
    ) -> Dict[str, Any]:
        """Provides a robust, professionally crafted fallback template if API is offline or key missing."""
        name_clean = receiver_name.strip() if receiver_name else "there"
        first_name = name_clean.split()[0] if " " in name_clean else name_clean

        clean_wants = receiver_wants.split(',')[0].strip()
        subject = f"Quick question regarding {clean_wants[:28]}"

        body_text = (
            f"Hi {first_name},\n\n"
            f"I came across your focus on {receiver_wants}.\n\n"
            f"At {config.sender_company}, we built {product_available} specifically designed "
            f"to address this exact goal—eliminating friction and driving measurable outcomes.\n\n"
            f"Here is how we help:\n"
            f"• Directly engineered for {receiver_wants}\n"
            f"• Rapid turnaround with dedicated integration support\n"
            f"• Reliable and built to scale as your operations grow\n\n"
            f"Would you be open to a 10-minute chat this week to see if this matches what you need?\n\n"
            f"Best regards,\n"
            f"{config.sender_name}\n"
            f"{config.sender_title} | {config.sender_company}\n"
            f"{config.sender_email}"
        )

        body_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #222;">
            <p>Hi {first_name},</p>
            <p>I came across your focus on <strong>{receiver_wants}</strong>.</p>
            <p>At <strong>{config.sender_company}</strong>, we built <strong>{product_available}</strong> specifically designed to address this exact goal—eliminating friction and driving measurable outcomes.</p>
            <p><strong>Here is how we help:</strong></p>
            <ul>
                <li>Directly engineered for {receiver_wants}</li>
                <li>Rapid turnaround with dedicated integration support</li>
                <li>Reliable and built to scale as your operations grow</li>
            </ul>
            <p>Would you be open to a 10-minute chat this week to see if this matches what you need?</p>
            <p>Best regards,<br>
            <strong>{config.sender_name}</strong><br>
            {config.sender_title} | {config.sender_company}<br>
            <a href="mailto:{config.sender_email}" style="color: #0066cc;">{config.sender_email}</a></p>
        </div>
        """

        return {
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html.strip(),
            "key_angle": f"Targeted proposition matching prospect's desire for '{receiver_wants}' with '{product_available}'",
            "is_fallback": True
        }
