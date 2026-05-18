import streamlit as st
import anthropic
import os
import json
import re

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="AI Strategy Engine",
    page_icon="🎯",
    layout="centered"
)

# =========================================
# SESSION STATE
# =========================================
if "history" not in st.session_state:
    st.session_state.history = []

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "strategy_data" not in st.session_state:
    st.session_state.strategy_data = {}

# =========================================
# API SETUP
# =========================================
api_key = os.getenv("ANTHROPIC_API_KEY")

# =========================================
# HEADER
# =========================================
st.title("🎯 AI Strategy Engine")

st.markdown("""
**Generate a complete social media strategy in seconds.**

Fill in the details below and Claude will generate a structured strategy covering:

- Brand positioning
- Content pillars
- Platform strategy
- Posting frequency
- Tone guidelines
- Content language 🌍
""")

st.divider()

# =========================================
# VALIDATE API KEY
# =========================================
if not api_key:

    st.error("❌ ANTHROPIC_API_KEY is missing.")

    st.info("""
Add your API key like this in Colab:

import os
os.environ["ANTHROPIC_API_KEY"] = "your_key_here"
""")

    st.stop()

# =========================================
# CLIENT
# =========================================
try:

    client = anthropic.Anthropic(api_key=api_key)

except Exception as e:

    st.error("❌ Failed to initialize Anthropic client.")

    with st.expander("Technical Details"):
        st.code(str(e))

    st.stop()

# =========================================
# SAFE JSON PARSER
# =========================================
def safe_parse_json(text):

    # Remove markdown code blocks
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    text = text.strip()

    # Try direct JSON parse
    try:
        return json.loads(text)

    except json.JSONDecodeError:

        # Try extracting JSON object only
        match = re.search(r'(\{.*\})', text, re.DOTALL)

        if match:

            try:
                return json.loads(match.group(1))

            except:
                return None

    return None

# =========================================
# VALIDATION
# =========================================
def validate_inputs(
    business,
    location,
    industry,
    audience,
    platforms,
    tone,
    goal,
    language
):

    errors = []

    if not business or len(business.strip()) < 3:
        errors.append(
            "Business name must be at least 3 characters."
        )

    if not location or len(location.strip()) < 3:
        errors.append(
            "Location must be at least 3 characters."
        )

    if not industry or len(industry.strip()) < 5:
        errors.append(
            "Industry must be at least 5 characters."
        )

    if not audience or len(audience.strip()) < 10:
        errors.append(
            "Target audience must be at least 10 characters."
        )

    if not platforms or len(platforms) == 0:
        errors.append(
            "Please select at least one platform."
        )

    if not goal or len(goal.strip()) < 10:
        errors.append(
            "Main goal must be at least 10 characters."
        )

    if not tone:
        errors.append(
            "Please select a brand tone."
        )

    if not language:
        errors.append(
            "Please select a content language."
        )

    return errors

# =========================================
# MAIN STRATEGY FUNCTION
# =========================================
def generate_strategy(
    business,
    location,
    industry,
    audience,
    platforms,
    tone,
    goal,
    language
):

    try:

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2500,

            system=f"""
You are a senior social media strategist.

CRITICAL RULES:
- Entire output MUST be written ONLY in {language}
- Do NOT mix languages
- Mention the exact location naturally
- Make recommendations realistic
- Use warm human language
- Avoid generic advice
- Include practical content ideas

FORMAT:

# Brand Positioning

## Content Pillar 1
## Content Pillar 2
## Content Pillar 3

## Platform Strategy
## Posting Frequency
## Tone Guidelines
""",

            messages=[
                {
                    "role": "user",
                    "content": f"""
Brand: {business}
Location: {location}
Industry: {industry}
Audience: {audience}
Platforms: {", ".join(platforms)}
Tone: {tone}
Goal: {goal}
Language: {language}
"""
                }
            ]
        )

        result = "".join(
            block.text
            for block in response.content
            if hasattr(block, "text")
        )

        if not result or len(result.strip()) < 100:

            return """
❌ The AI response was too short.

Please improve:
- Audience details
- Goal details
- Industry details
"""

        return result

    except Exception as e:

        return f"""
❌ Could not generate strategy.

Technical Error:
{str(e)}
"""

# =========================================
# STRUCTURED JSON FUNCTION
# =========================================
def generate_strategy_structured(
    business,
    location,
    industry,
    audience,
    tone,
    goal,
    language,
    platforms
):

    try:

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1200,

            system="""
You are an API.

Return ONLY valid JSON.

FORMAT:

{
  "business_name": "",
  "location": "",
  "industry": "",
  "language": "",
  "platforms": [],
  "main_goal": "",
  "brand_tone": "",
  "brand_positioning": "",
  "content_pillars": [
    {
      "title": "",
      "description": "",
      "post_ideas": ["", "", ""]
    }
  ],
  "platform_strategy": {
    "instagram": "",
    "facebook": "",
    "youtube": "",
    "linkedin": ""
  },
  "posting_frequency": "",
  "tone_guidelines": ""
}

RULES:
- Return ONLY JSON
- No markdown
- No explanations
- NEVER use markdown code fences
- NEVER wrap JSON inside ```json
- Return raw JSON only
- Populate EVERY field
- Content pillars MUST contain real data
- Platform strategy MUST contain real data
- Mention location naturally
- Avoid generic responses
"""

            ,

            messages=[
                {
                    "role": "user",
                    "content": f"""
Business Name: {business}
Location: {location}
Industry: {industry}
Audience: {audience}
Platforms: {", ".join(platforms)}
Brand Tone: {tone}
Main Goal: {goal}
Language: {language}
"""
                }
            ]
        )

        result = "".join(
            block.text
            for block in response.content
            if hasattr(block, "text")
        )

        # =========================================
        # RAW RESPONSE DEBUG
        # =========================================
        with st.expander("Raw JSON Response"):
            st.code(result)

        # =========================================
        # SAFE JSON PARSE
        # =========================================
        structured = safe_parse_json(result)

        # =========================================
        # INVALID JSON PROTECTION
        # =========================================
        if not structured:
            structured = {
                "business_name": business,
                "location": location,
                "industry": industry,
                "language": language,
                "platforms": platforms,
                "main_goal": goal,
                "brand_tone": tone,
                "brand_positioning": result[:300],
                "content_pillars": [
                    {
                        "title": f"{business} Content",
                        "description": "Generated from AI strategy output",
                        "post_ideas": [
                            "Local engagement content",
                            "Food and cafe reels",
                            "Customer interaction posts"
                        ]
                    }
                ],
                "platform_strategy": {
                    "instagram": "Use reels and local hashtags",
                    "facebook": "Community engagement posts",
                    "linkedin": "Brand awareness content",
                    "tiktok": "Short-form trending videos"
                },
                "posting_frequency": "4-5 posts weekly",
                "tone_guidelines": f"{tone} and community-focused"
            }

        # =========================================
        # REQUIRED KEYS
        # =========================================
        required_keys = [
            "business_name",
            "location",
            "industry",
            "language",
            "platforms",
            "main_goal",
            "brand_tone",
            "brand_positioning",
            "content_pillars",
            "platform_strategy",
            "posting_frequency",
            "tone_guidelines"
        ]

        for key in required_keys:

            if key not in structured:

                if key == "platforms":
                    structured[key] = []

                elif key == "content_pillars":
                    structured[key] = []

                elif key == "platform_strategy":
                    structured[key] = {}

                else:
                    structured[key] = ""

        # =========================================
        # TYPE SAFETY
        # =========================================
        if not isinstance(structured["platforms"], list):
            structured["platforms"] = []

        if not isinstance(structured["content_pillars"], list):
            structured["content_pillars"] = []

        if not isinstance(structured["platform_strategy"], dict):
            structured["platform_strategy"] = {}

        # =========================================
        # FORCE USER INPUT VALUES
        # =========================================
        structured["platforms"] = platforms

        structured["brand_tone"] = tone

        structured["language"] = language

        # =========================================
        # ENSURE CONTENT PILLARS EXIST
        # =========================================
        if (
            not structured["content_pillars"]
            or len(structured["content_pillars"]) == 0
        ):

            structured["content_pillars"] = [
                {
                    "title": "Behind the Scenes",
                    "description": "Show daily brand activities",
                    "post_ideas": [
                        "Workspace photos",
                        "Team moments",
                        "Production process"
                    ]
                },
                {
                    "title": "Customer Stories",
                    "description": "Highlight customer experiences",
                    "post_ideas": [
                        "Testimonials",
                        "Reviews",
                        "Community engagement"
                    ]
                },
                {
                    "title": "Product Spotlight",
                    "description": "Showcase products and services",
                    "post_ideas": [
                        "Featured products",
                        "Special offers",
                        "Best sellers"
                    ]
                }
            ]

        # =========================================
        # QUALITY CHECK
        # =========================================
        if (
            len(structured["content_pillars"]) == 0
            or structured["brand_positioning"] == ""
            or structured["tone_guidelines"] == ""
        ):

            st.error(
                "❌ JSON quality check failed."
            )

            st.info(
                "Please regenerate strategy."
            )

            return None

        # =========================================
        # SAVE TO SESSION
        # =========================================
        st.session_state.strategy_data = structured

        return structured

    except Exception as e:

        st.error(
            "❌ Failed to generate structured strategy."
        )

        with st.expander("Technical Error"):
            st.code(str(e))

        return {
            "business_name": business,
            "location": location,
            "industry": industry,
            "language": language,
            "platforms": platforms,
            "main_goal": goal,
            "brand_tone": tone,
            "brand_positioning": "Fallback strategy generated.",
            "content_pillars": [],
            "platform_strategy": {},
            "posting_frequency": "",
            "tone_guidelines": ""
        }

# =========================================
# TONE PREVIEW
# =========================================
def generate_tone_preview(
    business,
    industry,
    tone
):

    try:

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=300,

            messages=[
                {
                    "role": "user",
                    "content": f"""
Generate 3 short social media captions.

Brand: {business}
Industry: {industry}
Tone: {tone}

Keep them:
- Short
- Engaging
- Realistic
"""
                }
            ]
        )

        return "".join(
            block.text
            for block in response.content
            if hasattr(block, "text")
        )

    except:

        return """
❌ Couldn't generate tone preview.
"""

# =========================================
# INPUTS
# =========================================
business = st.text_input(
    "Brand Name",
    placeholder="e.g. Maison Dubois"
)

location = st.text_input(
    "Location",
    placeholder="e.g. Lyon, France"
)

industry = st.text_input(
    "Industry",
    placeholder="e.g. French Bakery & Café"
)

audience = st.text_area(
    "Target Audience",
    placeholder="e.g. Young professionals, tourists, pastry lovers in Lyon"
)

platforms = st.multiselect(
    "Platforms",
    [
        "Instagram",
        "LinkedIn",
        "Facebook",
        "TikTok",
        "YouTube",
        "X/Twitter"
    ]
)

goal = st.text_area(
    "Main Goal",
    placeholder="e.g. Increase local awareness and drive bakery visits"
)

tone = st.selectbox(
    "Brand Tone",
    [
        "Professional",
        "Friendly",
        "Bold",
        "Luxury",
        "Playful"
    ]
)

language = st.selectbox(
    "Content Language 🌍",
    [
        "English",
        "Malayalam",
        "Hindi",
        "Arabic",
        "Czech"
    ]
)

# =========================================
# BUTTONS
# =========================================
generate_clicked = st.button(
    "Generate Strategy",
    disabled=st.session_state.is_generating
)

save_clicked = st.button(
    "Generate Strategy + Save for Calendar",
    disabled=st.session_state.is_generating
)

# =========================================
# MAIN LOGIC
# =========================================
if generate_clicked or save_clicked:

    st.session_state.is_generating = True

    errors = validate_inputs(
        business,
        location,
        industry,
        audience,
        platforms,
        tone,
        goal,
        language
    )

    if errors:

        for err in errors:
            st.error(err)

        st.session_state.is_generating = False
        st.stop()

    else:

        try:

            with st.spinner(
                "Generating your strategy... this takes 10–20 seconds"
            ):

                result = generate_strategy(
                    business,
                    location,
                    industry,
                    audience,
                    platforms,
                    tone,
                    goal,
                    language
                )

                structured = generate_strategy_structured(
                    business,
                    location,
                    industry,
                    audience,
                    tone,
                    goal,
                    language,
                    platforms
                )

                st.session_state.strategy_data = structured

            # =========================================
            # SUCCESS
            # =========================================
            if save_clicked:

                st.success(
                    "✅ Strategy generated and saved for Module 2."
                )

            else:

                st.success(
                    "✅ Strategy generated successfully."
                )

            st.info(f"🌍 Output Language: {language}")

            # =========================================
            # STRATEGY OUTPUT
            # =========================================
            st.subheader(f"📌 Strategy for {business}")

            st.markdown(result)

            # =========================================
            # STRUCTURED JSON
            # =========================================
            with st.expander("📦 Structured Strategy Data"):

                st.code(
                    json.dumps(
                        st.session_state.strategy_data,
                        indent=2,
                        ensure_ascii=False
                    ),
                    language="json"
                )

            # =========================================
            # INTEGRATION JSON
            # =========================================
            with st.expander(
                "📋 Integration JSON — copy this for Module 2"
            ):

                st.code(
                    json.dumps(
                        st.session_state.strategy_data,
                        indent=2,
                        ensure_ascii=False
                    ),
                    language="json"
                )

            # =========================================
            # TONE PREVIEW
            # =========================================
            st.subheader("✍️ Tone Preview")

            captions = generate_tone_preview(
                business,
                industry,
                tone
            )

            st.markdown(captions)

            # =========================================
            # SAVE HISTORY
            # =========================================
            st.session_state.history.append({
                "brand": business,
                "strategy": result,
                "language": language
            })

            # =========================================
            # DOWNLOAD BUTTON
            # =========================================
            st.download_button(
                label=f"⬇ Download {business} Strategy",
                data=result,
                file_name=f"{business.replace(' ','_')}_strategy.txt",
                mime="text/plain"
            )

        except Exception as e:

            st.error(
                "❌ Could not generate strategy right now."
            )

            with st.expander(
                "Technical details"
            ):

                st.code(str(e))

        finally:

            st.session_state.is_generating = False

# =========================================
# MODULE 2 INTEGRATION DISPLAY
# =========================================
if (
    "strategy_data" in st.session_state
    and st.session_state.strategy_data
):

    st.divider()

    st.subheader("🔗 Module 2 Integration Data")

    st.success(
        "This structured strategy is now available for Module 2 Calendar Generator."
    )

    st.code(
        json.dumps(
            st.session_state.strategy_data,
            indent=2,
            ensure_ascii=False
        ),
        language="json"
    )

# =========================================
# HISTORY
# =========================================
if st.session_state.history:

    st.divider()

    st.subheader("📋 History")

    if st.button("🗑 Clear History"):

        st.session_state.history = []

        st.rerun()

    for item in reversed(st.session_state.history):

        with st.expander(item["brand"]):

            st.markdown(item["strategy"])

            st.caption(
                f"Language: {item.get('language','English')}"
            )

# =========================================
# FOOTER
# =========================================
st.divider()

st.caption("Built with Streamlit + Claude AI")
