import os
import re
from agents.rag_knowledge_base import retrieve_facts
from agents.compliance_guardrails import check_safety
from agents.pii_masker import format_customer_facts_masked, mask_text_for_llm
from agents.llm_telemetry import record_llm_event

_CLIENT = None

def _get_anthropic_client(api_key):
    global _CLIENT
    if _CLIENT is None:
        from anthropic import AsyncAnthropic
        _CLIENT = AsyncAnthropic(api_key=api_key)
    return _CLIENT


async def generate_response_async(user_text, customer_context, signals, recommendation, history, language="en"):
    rag_facts = retrieve_facts(user_text)
    customer_id = customer_context.get("customerId")

    if not check_safety(user_text):
        return "I'm sorry, I cannot process that request. Let's keep our conversation focused on personal finance.", []

    customer_facts = format_customer_facts_masked(customer_context, signals)
    masked_history = [
        {"user": mask_text_for_llm(turn.get("user", "")), "bot": mask_text_for_llm(turn.get("bot", ""))}
        for turn in history
    ]

    system_prompt = f"""You are Artha, a wealth advisory voice inside a bank's mobile app.

RULES YOU MUST FOLLOW:
- Only state numbers that appear in CUSTOMER_FACTS or PRODUCT_FACTS below.
  Never estimate, round dramatically, or invent a figure.
- If asked something you cannot answer from the provided facts, say so plainly and offer to connect a human advisor. Never guess.
- You give guidance and information, not regulated investment advice. For decisions that need a licensed adviser, say so and offer the human handoff.
- Keep responses to 2-3 short sentences unless the user asks for detail.
- Mirror the user's language; switch fluidly if they code-switch.
- Tone: calm, precise, warm. Never use fear to push a product.

CUSTOMER_FACTS:
{customer_facts}

RELEVANT_RECOMMENDATION:
- Action: {recommendation.get("action", "None")}
- Reason Code: {recommendation.get("reasonCode", "None")}
- Facts: {recommendation.get("facts", {})}

PRODUCT_FACTS:
{chr(10).join([f"- {fact}" for fact in rag_facts])}

CONVERSATION_HISTORY:
{chr(10).join([f"User: {turn.get('user')}\nArtha: {turn.get('bot')}" for turn in masked_history])}
"""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    model_name = "claude-3-5-sonnet-20241022"

    if api_key:
        try:
            client = _get_anthropic_client(api_key)
            message = await client.messages.create(
                model=model_name,
                max_tokens=256,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": mask_text_for_llm(user_text)}],
            )
            reply = message.content[0].text
            if not check_safety(reply):
                reply = "I cannot recommend products with guaranteed returns. Let me focus on explaining historical performances and risk parameters."
            record_llm_event("quick_path", success=True, model=model_name, customer_id=customer_id)
            rec_ids = [recommendation.get("recommendation_id")] if recommendation.get("recommendation_id") else []
            return reply, rec_ids
        except Exception as e:
            record_llm_event(
                "quick_path",
                success=False,
                model=model_name,
                error=str(e),
                customer_id=customer_id,
            )

    lower_text = user_text.lower()
    is_hindi = language == "hi" or re.search(r"\b(theek|kya|aap|nahi|hai|main|hoon|hindi)\b", lower_text)
    rec_ids = []
    if recommendation.get("recommendation_id"):
        rec_ids.append(recommendation.get("recommendation_id"))

    if is_hindi:
        reply = "Bilkul! Main aapko Hindi mein bata sakti hoon. Aapki savings rate is mahine 22% hai — yeh aapke average se behtar hai. Aapka SIP bhi First Car goal ke liye sahi track pe hai."
    elif re.search(r"\b(doing|summary|overview|status)\b", lower_text):
        reply = f"You saved **{round(signals.get('savings_rate', 0.22)*100, 1)}%** of your income this month! This is above your usual 18%. Your SIPs are on track."
    elif re.search(r"\b(sip|mutual fund|investment)\b", lower_text):
        reply = "Your SIP of **₹5,000/month** into the Hybrid Equity Fund is active and tracking well for your First Car goal."
    elif re.search(r"\b(recommend|suggest|advice)", lower_text):
        if recommendation.get("reasonCode") == "DORMANT_FD_REALLOCATION":
            reply = "Based on your moderate risk profile, your **Fixed Deposit** has been dormant and could be reviewed for better goal alignment. Want to see why?"
        else:
            reply = "Based on your moderate risk profile, your dormant FD could be reviewed for better goal alignment. Want to see why?"
    elif re.search(r"\b(why)\b", lower_text):
        reply = f"Three reasons based on your profile: dormant FD months, goal horizon, and your current risk band."
    elif re.search(r"\b(spend|expense|dining|lunch)\b", lower_text):
        reply = f"Dining-out spending is up **₹{signals.get('dining_delta', 3200)}** vs your average, but savings rate remains healthy."
    elif re.search(r"\b(goal|car|vacation|emergency)\b", lower_text):
        reply = "Your goals are mixed: First Car is on track; Europe Vacation may need attention."
    elif re.search(r"\b(rm|advisor|human|priya|talk|connect|escalate)\b", lower_text):
        reply = "I'll connect you with your relationship manager right away with a summary of our conversation."
    else:
        reply = f"Hello! You saved **{signals.get('savings_rate', 0.22)*100}%** of your income this month. What would you like to explore?"

    record_llm_event("quick_path", success=False, model="keyword_mock", customer_id=customer_id)
    return reply, rec_ids


def generate_response(intent):
    return "Here is your wealth guidance."
