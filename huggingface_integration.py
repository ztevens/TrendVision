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
# Use smaller models that fit within free API limits (less than 10GB)
DEFAULT_MODEL = "gpt2"  # Small but powerful text generation model (~500MB)
BACKUP_MODEL = "facebook/bart-large-cnn"  # Backup model for summarization (~1.6GB)

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
        # Simplified prompt for smaller models that might not handle complex instructions well
        # Focus on getting plain text that we can process
        prompt = f"""Social media content ideas for {platform} to improve {metric.lower()}.

Generate 3 specific content ideas for {platform} to increase {metric.lower()}.
For each idea include a title, description, best formats to use, and hashtags.
"""
        
        # Get API key if available
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        
        # Generate content
        response_text = generate_with_huggingface(prompt, api_key=api_key)
        logger.info(f"Response from HuggingFace: {response_text[:100]}...")
        
        # Process the response - smaller models won't generate perfect JSON
        # So we'll parse the text and structure it ourselves
        formatted_ideas = []
        
        # Split by numbers or line breaks to identify different ideas
        import re
        ideas_sections = re.split(r'(?:\n\n|\n\d+[\.\)]\s+)', response_text)
        
        for i, section in enumerate(ideas_sections):
            # Skip empty sections
            if not section.strip():
                continue
                
            section = section.strip()
            
            # Try to extract a title
            title_match = re.search(r'^([^\.:\n]+)[\.:\n]', section)
            title = title_match.group(1).strip() if title_match else f"Content Idea {i+1}"
            
            # The rest is the description
            description = section
            
            # Try to find formats mentioned
            formats = []
            format_keywords = ["video", "image", "carousel", "story", "stories", "post", "reel", "live", "article"]
            for keyword in format_keywords:
                if keyword in section.lower():
                    formats.append(keyword.capitalize())
            
            if not formats:
                formats = ["Post", "Video"]  # Default formats
                
            # Extract potential hashtags or generate relevant ones
            hashtags = []
            # Try to find hashtag-like words
            hashtag_matches = re.findall(r'#([a-zA-Z0-9_]+)', section)
            if hashtag_matches:
                hashtags = hashtag_matches
            else:
                # Generate some based on platform and metric
                hashtags = [platform.lower(), metric.lower(), "content", "social"]
            
            # Add the idea to our list
            formatted_ideas.append({
                "title": title,
                "description": description,
                "best_formats": formats,
                "hashtags": hashtags
            })
        
        # If we couldn't parse any ideas, create a fallback
        if not formatted_ideas:
            formatted_ideas = [{
                "title": f"{platform} Content Strategy",
                "description": response_text[:500] + ("..." if len(response_text) > 500 else ""),
                "best_formats": ["Post", "Video"],
                "hashtags": [platform.lower(), metric.lower(), "contentstrategy"]
            }]
        
        return {
            "status": "success",
            "provider": "huggingface",
            "content_ideas": formatted_ideas,
            "message": "Content ideas generated successfully with HuggingFace."
        }
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating content with HuggingFace: {error_message}")
        
        # Fall back to our expert-crafted templates
        from ai_content_generator import get_fallback_ideas
        fallback_content = get_fallback_ideas(platform, metric)
        
        return {
            "status": "partial_success",
            "message": f"Used fallback templates due to HuggingFace API error: {error_message}",
            "provider": "template",
            "content_ideas": fallback_content
        }

# Export the main function for use in other modules
__all__ = ['generate_content_ideas_with_huggingface']