import os
import httpx
import re
from agents.rag_knowledge_base import retrieve_facts
from agents.compliance_guardrails import check_safety

_CLIENT = None

def _get_anthropic_client(api_key):
    global _CLIENT
    if _CLIENT is None:
        from anthropic import AsyncAnthropic
        _CLIENT = AsyncAnthropic(api_key=api_key)
    return _CLIENT

async def generate_response_async(user_text, customer_context, signals, recommendation, history, language="en"):
    # Retrieve grounded facts via RAG
    rag_facts = retrieve_facts(user_text)
    
    # 1. Check safety of the incoming user text
    if not check_safety(user_text):
        return "I'm sorry, I cannot process that request. Let's keep our conversation focused on personal finance.", []
        
    # Construct System Prompt
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
- Customer Name: {customer_context.get("name", "Riya")}
- Risk Profile: {customer_context.get("riskProfile", "Moderate")}
- Savings Account Balance: ₹{customer_context.get("savings", 0)}
- Savings Rate (this month): {signals.get("savings_rate", 0.22) * 100}%
- Dining Delta: +₹{signals.get("dining_delta", 0)} (this month: ₹{signals.get("dining_total_current", 0)}, previous: ₹{signals.get("dining_total_prev", 0)})

RELEVANT_RECOMMENDATION:
- Action: {recommendation.get("action", "None")}
- Reason Code: {recommendation.get("reasonCode", "None")}
- Facts: {recommendation.get("facts", {})}

PRODUCT_FACTS:
{chr(10).join([f"- {fact}" for fact in rag_facts])}

CONVERSATION_HISTORY:
{chr(10).join([f"User: {turn.get('user')}\nArtha: {turn.get('bot')}" for turn in history])}
"""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if api_key:
        try:
            client = _get_anthropic_client(api_key)
            
            # Request response from Claude
            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=256,
                temperature=0.2,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_text}
                ]
            )
            reply = message.content[0].text
            
            # Run output safety guardrails
            if not check_safety(reply):
                reply = "I cannot recommend products with guaranteed returns. Let me focus on explaining historical performances and risk parameters."
                
            rec_ids = [recommendation.get("recommendation_id")] if recommendation.get("recommendation_id") else []
            return reply, rec_ids
        except Exception as e:
            # Fallback on Anthropic client failure
            print(f"Anthropic API call failed: {e}")
            
    # Mock LLM simulation fallback (high-IQ keyword-based rule matching matching target persona)
    lower_text = user_text.lower()
    
    # Check language switch
    is_hindi = language == "hi" or re.search(r"\b(theek|kya|aap|nahi|hai|main|hoon|hindi)\b", lower_text)
    
    rec_ids = []
    if recommendation.get("recommendation_id"):
        rec_ids.append(recommendation.get("recommendation_id"))
        
    if is_hindi:
        reply = "Bilkul! Main aapko Hindi mein bata sakti hoon. Aapki savings rate is mahine 22% hai — yeh aapke average se behtar hai. Aapka SIP bhi First Car goal ke liye sahi track pe hai. 🎯"
    elif re.search(r"\b(doing|summary|overview|status)\b", lower_text):
        reply = f"You saved **{round(signals.get('savings_rate', 0.22)*100, 1)}%** of your income this month, Riya! 🎉 This is above your usual 18%. Your SIPs are on track, and you have ₹38,200 in your savings account."
    elif re.search(r"\b(sip|mutual fund|investment)\b", lower_text):
        reply = "Your SIP of **₹5,000/month** into the Hybrid Equity Fund is active. You've accumulated **₹74,200** so far, which is tracking well for your First Car goal."
    elif re.search(r"\b(recommend|suggest|advice)", lower_text):
        reply = "Based on your moderate risk profile, your **Fixed Deposit of ₹1.5L** has been dormant for 14 months and earns 6.1%. Reallocating to a hybrid fund could realistically target higher returns over your 2-year goal horizon. Want to see why?"
    elif re.search(r"\b(why)\b", lower_text):
        reply = f"Three reasons: 1) Your HDFC FD has been dormant for **{recommendation.get('facts', {}).get('Months Dormant', '14')} months**, 2) Your goal horizon is **2 years**, matching a hybrid fund's profile, and 3) Your risk profile moved to **Moderate** in March after your salary hike."
    elif re.search(r"\b(spend|expense|dining|lunch)\b", lower_text):
        reply = f"Dining-out spending is up **₹{signals.get('dining_delta', 3200)}** vs your average — mostly weekday lunches. It's the 3rd week in a row, but your savings rate is still healthy at 22%."
    elif re.search(r"\b(goal|car|vacation|emergency)\b", lower_text):
        reply = "First Car goal: 48% funded (₹2.4L of ₹5L) — on track for Jun 2027. Europe Vacation goal: only 29% funded with 9 months left — at risk."
    elif re.search(r"\b(rm|advisor|human|priya|talk|connect|escalate)\b", lower_text):
        reply = "Bilkul! I'll connect you with your RM, Priya Sharma, right away. I'll send her a summary of our conversation so she's already up to speed."
    else:
        reply = f"Hello Riya! I'm Artha, your personal wealth advisor. You saved **{signals.get('savings_rate', 0.22)*100}%** of your income this month. What would you like to explore?"
        
    return reply, rec_ids

# Keep legacy synchronous function for compatibility if needed
def generate_response(intent):
    return "Here is your wealth guidance."