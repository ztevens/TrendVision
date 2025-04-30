"""
HuggingFace Integration Module for TrendVision AI

This module provides functions to interact with HuggingFace's free inference API
for generating content ideas and trend analysis assistance.
"""
import json
import logging
import os
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"  # A good free model with no API key requirement
BACKUP_MODEL = "google/flan-t5-xxl"  # Backup model if the primary fails

def generate_with_huggingface(prompt, model_name=DEFAULT_MODEL, api_key=None):
    """
    Generate content using HuggingFace's inference API.
    
    Args:
        prompt (str): The prompt to send to the model
        model_name (str): HuggingFace model ID to use
        api_key (str, optional): HuggingFace API key for increased rate limits
        
    Returns:
        str: Generated content
    """
    try:
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add API key if provided
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Prepare payload based on model type
        if "mistral" in model_name.lower() or "llama" in model_name.lower():
            # Format for chat models
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
        else:
            # Format for completion models
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
        
        # Make API request
        logger.info(f"Sending request to HuggingFace model: {model_name}")
        response = requests.post(
            f"{HUGGINGFACE_API_URL}{model_name}",
            headers=headers,
            json=payload,
            timeout=60  # Increased timeout for model loading
        )
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            
            # Different models return different response formats
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                else:
                    return str(result[0])
            else:
                return str(result)
        else:
            error_msg = f"Error from HuggingFace API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            
            # Try backup model if primary fails
            if model_name != BACKUP_MODEL:
                logger.info(f"Trying backup model: {BACKUP_MODEL}")
                return generate_with_huggingface(prompt, BACKUP_MODEL, api_key)
            
            raise Exception(error_msg)
            
    except Exception as e:
        logger.error(f"Exception in HuggingFace generation: {str(e)}")
        raise

def generate_content_ideas_with_huggingface(platform, metric, trend_data=None):
    """
    Generate content ideas using HuggingFace's inference API.
    
    Args:
        platform (str): Social media platform
        metric (str): Performance metric
        trend_data (dict, optional): Trend data for context
        
    Returns:
        dict: Content ideas and suggestions
    """
    try:
        # Create a detailed prompt
        prompt = f"""You are a social media content expert. Generate creative and strategic content ideas for {platform} focused on improving {metric.lower()}.

Please provide 4-5 specific content ideas that will work well on {platform} for increasing {metric.lower()}.
For each idea, include:
1. A catchy title
2. A detailed description explaining the content
3. Best formats to use (e.g., video, carousel, etc.)
4. Relevant hashtags

Format your response as a JSON array with this structure:
[
  {{
    "title": "Idea title",
    "description": "Detailed explanation",
    "best_formats": ["Format 1", "Format 2"],
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
  }},
  ...more ideas
]

Make sure your ideas are specifically tailored for {platform} and optimized for {metric.lower()}.
"""
        
        # Add context from trend data if available
        if trend_data and isinstance(trend_data, dict):
            prompt += "\n\nHere's some context about current performance and trends:\n"
            
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
            
            if "trend_patterns" in trend_data:
                patterns = trend_data["trend_patterns"]
                prompt += "\nCurrent trends on the platform:\n"
                for trend in patterns.get("current_trends", [])[:3]:
                    prompt += f"- {trend}\n"
        
        # Get API key if available
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        
        # Generate content
        response_text = generate_with_huggingface(prompt, api_key=api_key)
        
        # Try to extract and parse JSON from the response
        try:
            # Look for JSON array in the response
            import re
            json_match = re.search(r'\[(.*?)\]', response_text, re.DOTALL)
            
            if json_match:
                json_content = f"[{json_match.group(1)}]"
                content_ideas = json.loads(json_content)
            else:
                # Try to see if the whole response is JSON
                content_ideas = json.loads(response_text)
                
            # Ensure we have a list of ideas
            if not isinstance(content_ideas, list):
                content_ideas = [content_ideas]
                
            return {
                "status": "success",
                "provider": "huggingface",
                "content_ideas": content_ideas,
                "message": "Content ideas generated successfully with HuggingFace."
            }
            
        except Exception as json_error:
            logger.error(f"Failed to parse JSON from response: {str(json_error)}")
            
            # If JSON parsing fails, return the raw text in a structured format
            default_idea = {
                "title": "Content Strategy",
                "description": response_text[:500] + ("..." if len(response_text) > 500 else ""),
                "best_formats": ["Various formats"],
                "hashtags": [f"#{platform.lower()}", f"#{metric.lower()}", "#contentstrategy"]
            }
            
            return {
                "status": "partial_success",
                "provider": "huggingface",
                "content_ideas": [default_idea],
                "message": "Generated content with HuggingFace, but couldn't format as JSON."
            }
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating content with HuggingFace: {error_message}")
        
        return {
            "status": "error",
            "message": f"Error with HuggingFace API: {error_message}",
            "provider": "huggingface",
            "content_ideas": []
        }

# Export the main function for use in other modules
__all__ = ['generate_content_ideas_with_huggingface']