"""
AI Content Generator Module for TrendVision AI

This module provides AI-powered content idea generation and trend analysis assistance.
Uses the application's API key to generate personalized content suggestions.
"""
import os
import json
import logging
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_content_ideas_with_ai(platform, metric, trend_data=None, api_provider="anthropic"):
    """
    Generate content ideas using AI services. Uses the application's API key.
    
    Args:
        platform (str): Social media platform
        metric (str): Performance metric
        trend_data (dict, optional): Trend data for context
        api_provider (str): AI provider to use (openai or anthropic)
        
    Returns:
        dict: Content ideas and suggestions
    """
    # Check if we have the necessary API key for the selected provider
    api_key = get_api_key(api_provider)
    
    if not api_key:
        return {
            "status": "error",
            "message": f"No API key found for {api_provider}. Please contact support.",
            "ideas": get_fallback_ideas(platform, metric)
        }
    
    try:
        if api_provider == "openai":
            return generate_with_openai(platform, metric, trend_data, api_key)
        elif api_provider == "anthropic":
            return generate_with_anthropic(platform, metric, trend_data, api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {api_provider}")
    except Exception as e:
        logger.error(f"Error generating content with {api_provider}: {str(e)}")
        return {
            "status": "error",
            "message": f"Error generating content: {str(e)}",
            "ideas": get_fallback_ideas(platform, metric)
        }

def get_api_key(provider):
    """Get API key for the specified provider from session state or environment."""
    # Check session state first (user-provided in UI)
    if f"{provider.upper()}_API_KEY" in st.session_state:
        return st.session_state[f"{provider.upper()}_API_KEY"]
    
    # Fall back to environment variables
    return os.environ.get(f"{provider.upper()}_API_KEY")

def generate_with_openai(platform, metric, trend_data, api_key):
    """Generate content ideas using OpenAI."""
    try:
        # Import here to avoid dependency if not used
        from openai import OpenAI
        
        # Create client with the API key
        client = OpenAI(api_key=api_key)
        
        # Create a structured prompt
        prompt = create_prompt_for_content_ideas(platform, metric, trend_data)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Use the newest OpenAI model
            messages=[
                {"role": "system", "content": "You are a social media content strategist specializing in trend analysis and content creation."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        # Parse the response
        content = response.choices[0].message.content
        ideas = json.loads(content)
        
        return {
            "status": "success",
            "provider": "openai",
            "ideas": ideas,
            "message": "Content ideas generated successfully with OpenAI."
        }
    except ImportError:
        logger.error("OpenAI package not installed")
        return {
            "status": "error",
            "message": "OpenAI package not installed. Please install it with: pip install openai",
            "ideas": get_fallback_ideas(platform, metric)
        }
    except Exception as e:
        logger.error(f"Error with OpenAI: {str(e)}")
        raise

def generate_with_anthropic(platform, metric, trend_data, api_key):
    """Generate content ideas using Anthropic."""
    try:
        # Import here to avoid dependency if not used
        from anthropic import Anthropic
        
        # Create client with the API key
        client = Anthropic(api_key=api_key)
        
        # Create a structured prompt
        prompt = create_prompt_for_content_ideas(platform, metric, trend_data)
        
        # Add formatting instructions for JSON
        prompt += "\n\nPlease format your response as a valid JSON object with the following structure:\n"
        prompt += """{
  "content_ideas": [
    {"title": "Idea 1 Title", "description": "Description of the idea", "best_formats": ["format1", "format2"]},
    ...more ideas
  ],
  "hashtag_suggestions": ["hashtag1", "hashtag2", ...],
  "posting_schedule": {
    "best_days": ["day1", "day2"],
    "best_times": ["time1", "time2"],
    "frequency": "Recommended posting frequency"
  },
  "trend_insights": ["insight1", "insight2", ...],
  "content_series_ideas": ["series idea 1", "series idea 2", ...]
}"""
        
        # Call Anthropic API
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the JSON content from the response
        content = response.content[0].text
        
        # Try to find and parse JSON in the response
        try:
            # Look for JSON block
            json_content = extract_json_from_text(content)
            ideas = json.loads(json_content)
        except:
            # If JSON parsing fails, create a structured response from the text
            ideas = {
                "content_ideas": [{"title": "Generated Content", "description": content, "best_formats": ["text"]}],
                "hashtag_suggestions": [],
                "posting_schedule": {},
                "trend_insights": [],
                "content_series_ideas": []
            }
        
        return {
            "status": "success",
            "provider": "anthropic",
            "ideas": ideas,
            "message": "Content ideas generated successfully with Anthropic Claude."
        }
    except ImportError:
        logger.error("Anthropic package not installed")
        return {
            "status": "error",
            "message": "Anthropic package not installed. Please install it with: pip install anthropic",
            "ideas": get_fallback_ideas(platform, metric)
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error with Anthropic: {error_message}")
        
        # Check for specific error types
        if "credit balance is too low" in error_message:
            return {
                "status": "error",
                "message": "The Anthropic API account has insufficient credits. Please contact support to upgrade the API plan.",
                "ideas": get_fallback_ideas(platform, metric)
            }
        else:
            return {
                "status": "error",
                "message": f"Error with Anthropic API: {error_message}",
                "ideas": get_fallback_ideas(platform, metric)
            }

def extract_json_from_text(text):
    """Extract JSON content from text that might contain explanation before/after the JSON."""
    # Try to find JSON between triple backticks
    import re
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    
    if json_match:
        return json_match.group(1)
    
    # If no clear JSON block, try to find content between curly braces
    json_match = re.search(r'(\{[\s\S]*\})', text)
    if json_match:
        return json_match.group(1)
    
    # If all else fails, return the whole text
    return text

def create_prompt_for_content_ideas(platform, metric, trend_data=None):
    """Create a detailed prompt for AI content generation."""
    prompt = f"""I need creative and strategic content ideas for {platform} that will help improve {metric.lower()}.

Please provide the following:
1. 10 specific content ideas tailored for {platform}, focusing on improving {metric.lower()}
2. Relevant hashtag suggestions
3. Optimal posting schedule (days and times)
4. 3-5 trend insights relevant to {platform} right now
5. Ideas for content series that could work well on {platform}

"""
    
    # Add context from trend data if available
    if trend_data and isinstance(trend_data, dict):
        prompt += "Here's some context about current performance and trends:\n"
        
        if "insights" in trend_data:
            insights = trend_data["insights"]
            if "overall_trend" in insights:
                trend = insights["overall_trend"]
                prompt += f"- Overall trend: {trend['direction']} ({trend['percent_change']}% change)\n"
                prompt += f"- Interpretation: {trend['interpretation']}\n"
            
            if "volatility" in insights:
                volatility = insights["volatility"]
                prompt += f"- Performance volatility: {volatility['value']}%\n"
                prompt += f"- Volatility insight: {volatility['interpretation']}\n"
            
            if "seasonality" in insights:
                seasonality = insights["seasonality"]
                prompt += f"- Best performing day: {seasonality['best_day']}\n"
                prompt += f"- Worst performing day: {seasonality['worst_day']}\n"
        
        if "trend_patterns" in trend_data:
            patterns = trend_data["trend_patterns"]
            prompt += "\nCurrent trends on the platform:\n"
            for trend in patterns.get("current_trends", [])[:3]:
                prompt += f"- {trend}\n"
            
            prompt += "\nEmerging trends on the platform:\n"
            for trend in patterns.get("emerging_trends", [])[:3]:
                prompt += f"- {trend}\n"
    
    return prompt

def get_fallback_ideas(platform, metric):
    """Get fallback content ideas when AI generation is not available."""
    fallback_ideas = {
        "content_ideas": [
            {
                "title": "Behind-the-Scenes Content",
                "description": f"Share authentic behind-the-scenes content showing your work process. Great for building trust and increasing {metric.lower()} on {platform}.",
                "best_formats": ["Video", "Image carousel", "Stories"]
            },
            {
                "title": "Industry Trend Analysis",
                "description": f"Share your analysis of current trends in your industry, positioning yourself as a thought leader on {platform}.",
                "best_formats": ["Carousel post", "Article", "Video"]
            },
            {
                "title": "User-Generated Content Spotlight",
                "description": f"Feature content created by your audience, which builds community and increases {metric.lower()}.",
                "best_formats": ["Gallery post", "Stories", "Shoutout"]
            },
            {
                "title": "Tutorial or How-To Content",
                "description": f"Create educational content that solves problems for your audience on {platform}.",
                "best_formats": ["Step-by-step guide", "Video tutorial", "Live demonstration"]
            },
            {
                "title": "Question Prompt to Engage Audience",
                "description": f"Ask thought-provoking questions related to your niche to spark conversation and increase {metric.lower()}.",
                "best_formats": ["Text post", "Poll", "Question sticker"]
            }
        ],
        "hashtag_suggestions": [
            "#ContentCreation",
            "#DigitalMarketing",
            "#SocialMediaTips",
            f"#{platform}Tips",
            "#ContentStrategy"
        ],
        "posting_schedule": {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_times": ["9:00 AM", "12:00 PM", "7:00 PM"],
            "frequency": "3-5 times per week for optimal engagement"
        },
        "trend_insights": [
            "Authentic, unfiltered content is outperforming heavily produced content",
            "Short-form video continues to see the highest growth across platforms",
            "Interactive content that encourages audience participation shows higher engagement",
            "Educational content that provides clear value is being favored by algorithms",
            "Cross-platform content strategies are becoming increasingly important"
        ],
        "content_series_ideas": [
            "Weekly industry news roundup with your expert commentary",
            "Monthly Q&A sessions addressing audience questions",
            "Transformation Tuesday showcasing before/after results",
            "Tips & Tricks Thursday with actionable advice",
            "Success Story Spotlight featuring case studies or testimonials"
        ]
    }
    
    return fallback_ideas

def check_ai_availability():
    """Check if AI services are available based on API keys."""
    openai_available = get_api_key("openai") is not None
    anthropic_available = get_api_key("anthropic") is not None
    
    return {
        "openai": openai_available,
        "anthropic": anthropic_available,
        "any_available": openai_available or anthropic_available
    }