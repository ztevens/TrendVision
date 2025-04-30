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

def generate_content_ideas_with_ai(platform, metric, trend_data=None, api_provider="gemini"):
    """
    Generate content ideas using AI services. Uses the application's API key.
    
    Args:
        platform (str): Social media platform
        metric (str): Performance metric
        trend_data (dict, optional): Trend data for context
        api_provider (str): AI provider to use (openai, anthropic, or gemini)
        
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
        elif api_provider == "gemini":
            return generate_with_gemini(platform, metric, trend_data, api_key)
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
    """Get expert-crafted content ideas for specific platforms and metrics."""
    
    platform = platform.lower()
    metric = metric.lower()
    
    # Create an enhanced dictionary of ideas for all platforms
    all_platform_ideas = {
        "instagram": {
            "engagement": [
                {
                    "title": "Interactive Instagram Story Polls",
                    "description": "Create a series of polls in your Instagram Stories that ask audience opinions on topics relevant to your niche. Follow up with results and your thoughts to keep the conversation going.",
                    "best_formats": ["Stories", "Poll stickers"],
                    "hashtags": ["instapoll", "interactivestories", "engagewithme"]
                },
                {
                    "title": "User-Generated Content Challenge",
                    "description": "Launch a branded hashtag challenge asking followers to create content related to your products or services. Showcase the best submissions on your feed and stories.",
                    "best_formats": ["Reels", "Feed post", "Stories"],
                    "hashtags": ["ugcchallenge", "brandedhashtag", "yourcommunity"]
                },
                {
                    "title": "Behind-the-Scenes Instagram Carousel",
                    "description": "Create a 10-slide carousel showing the step-by-step process behind your work, product creation, or service delivery. Include interesting details that wouldn't normally be visible to customers.",
                    "best_formats": ["Carousel post", "Image sequence"],
                    "hashtags": ["behindthescenes", "makingof", "processvideo"]
                },
                {
                    "title": "Question Sticker Q&A Series",
                    "description": "Use the question sticker to collect questions from your audience, then create a series of story slides or short Reels answering those questions in an engaging way.",
                    "best_formats": ["Stories", "Reels"],
                    "hashtags": ["askmeanything", "qatime", "expertadvice"]
                }
            ],
            "growth": [
                {
                    "title": "Trendjacking Reel Series",
                    "description": "Create a series of Reels that leverage current Instagram audio trends but with a twist related to your industry or niche. Focus on short, attention-grabbing hooks in the first 3 seconds.",
                    "best_formats": ["Reels", "Short video"],
                    "hashtags": ["trendingaudio", "reelsinstagram", "trendalert"]
                },
                {
                    "title": "Viral Hook Carousel Tutorial",
                    "description": "Start with a bold claim or surprising statistic as the first slide, then deliver valuable step-by-step information in the following slides. End with a clear call to action to follow for more insights.",
                    "best_formats": ["Carousel post"],
                    "hashtags": ["learnwithme", "educationalcontent", "experttips"]
                },
                {
                    "title": "Collaboration Content Series",
                    "description": "Partner with complementary creators or brands in your niche for a content exchange. Create joint Reels, takeovers, or carousel posts that introduce each other to your respective audiences.",
                    "best_formats": ["Reels", "Stories takeover", "Feed collaboration"],
                    "hashtags": ["collab", "contentpartnership", "featurefriday"]
                }
            ],
            "conversion": [
                {
                    "title": "Limited-Time Offer Countdown",
                    "description": "Create an eye-catching post or story series with the countdown sticker for a special offer. Follow up with reminder stories leading to the deadline to create urgency.",
                    "best_formats": ["Stories with countdown", "Feed announcement"],
                    "hashtags": ["limitedtime", "specialoffer", "dontmissout"]
                },
                {
                    "title": "Before-and-After Transformation Series",
                    "description": "Showcase impressive before-and-after results from your product or service using carousel posts or side-by-side comparisons. Include testimonials and specific outcomes in the caption.",
                    "best_formats": ["Carousel post", "Side-by-side images"],
                    "hashtags": ["transformation", "realresults", "beforeandafter"]
                },
                {
                    "title": "Product Demo with User Pain Points",
                    "description": "Create a Reel demonstrating how your product or service solves specific customer problems. Address common objections and end with a clear call to action to purchase or learn more.",
                    "best_formats": ["Reels", "Product demonstration"],
                    "hashtags": ["problemsolved", "productdemo", "musthavenow"]
                }
            ]
        },
        "tiktok": {
            "engagement": [
                {
                    "title": "Duet Chain Challenge",
                    "description": "Start a video designed specifically for duets, encouraging followers to add their version or reaction. Create a compilation of the best duets to showcase community participation.",
                    "best_formats": ["TikTok Duet", "Challenge format"],
                    "hashtags": ["duetchallenge", "duetchain", "jointhefun"]
                },
                {
                    "title": "Comment-to-Video Response Series",
                    "description": "Create videos that directly respond to user comments from previous videos. This shows you're actively listening to your audience and encourages more comments on future content.",
                    "best_formats": ["Comment response", "Stitch feature"],
                    "hashtags": ["commentresponse", "youasked", "tiktokconversation"]
                },
                {
                    "title": "Day-In-The-Life POV",
                    "description": "Create an authentic, behind-the-scenes look at your daily routine, business operations, or creative process using TikTok's fast-paced editing style.",
                    "best_formats": ["POV video", "Day-in-the-life"],
                    "hashtags": ["dayinthelife", "tiktokreality", "behindthebrand"]
                }
            ],
            "growth": [
                {
                    "title": "Trending Sound Hook Series",
                    "description": "Create a series of videos using currently trending sounds, but with unique visuals related to your niche. Focus on pattern interruption in the first 1-2 seconds to stop the scroll.",
                    "best_formats": ["Trending sound video"],
                    "hashtags": ["trendingsound", "fyp", "viralsound"]
                },
                {
                    "title": "Educational Hook-Teach-Tease Format",
                    "description": "Start with a bold hook (\"Did you know...\"), deliver quick valuable information, then tease more content available on your profile or link in bio.",
                    "best_formats": ["Educational video", "Quick tips"],
                    "hashtags": ["learnontiktok", "didyouknow", "tiktokskills"]
                },
                {
                    "title": "Green Screen Fact Series",
                    "description": "Use TikTok's green screen effect to place yourself in front of interesting visuals while sharing surprising facts or statistics relevant to your industry.",
                    "best_formats": ["Green screen video", "Slideshow style"],
                    "hashtags": ["greenscreen", "factseries", "mindblown"]
                }
            ],
            "conversion": [
                {
                    "title": "Problem-Solution-Proof TikTok",
                    "description": "Create a three-part video identifying a common problem your audience faces, presenting your product/service as the solution, then showing proof it works (reviews, results, demonstrations).",
                    "best_formats": ["Before/after video", "Testimonial showcase"],
                    "hashtags": ["problemsolved", "lifehack", "gamechanger"]
                },
                {
                    "title": "\"TikTok Made Me Buy It\" Style Review",
                    "description": "Create content that mimics the popular \"TikTok Made Me Buy It\" format, showcasing your product in an authentic, review-style video that emphasizes unique selling points.",
                    "best_formats": ["Product review", "Unboxing style"],
                    "hashtags": ["tiktokmademebuyit", "honestreviews", "worthit"]
                },
                {
                    "title": "Limited Offer Countdown",
                    "description": "Create a series of TikToks announcing a special offer with countdown updates as the deadline approaches, creating urgency and FOMO (fear of missing out).",
                    "best_formats": ["Countdown video", "Special offer announcement"],
                    "hashtags": ["limitedoffer", "dontwait", "specialdeal"]
                }
            ]
        },
        "youtube": {
            "engagement": [
                {
                    "title": "Audience-Requested Tutorial Series",
                    "description": "Create a series of tutorials specifically addressing questions and topics requested by your audience in comments. Reference the viewer who suggested each topic to increase community connection.",
                    "best_formats": ["How-to video", "Step-by-step tutorial"],
                    "hashtags": ["howtoyoutube", "tutorialseries", "youaskedweanswered"]
                },
                {
                    "title": "Community Poll Follow-Up Video",
                    "description": "Use YouTube's Community tab to post a poll, then create a video based on the winning option. This gives viewers direct input into your content and increases their investment.",
                    "best_formats": ["Discussion video", "Poll-based content"],
                    "hashtags": ["youtubepolls", "yourdecision", "audiencechoice"]
                },
                {
                    "title": "Live Q&A Session with Timestamps",
                    "description": "Host a live stream Q&A session, then add comprehensive timestamps to the recording for easy navigation. This creates both live engagement and a valuable resource afterward.",
                    "best_formats": ["YouTube Live", "Q&A format"],
                    "hashtags": ["livequestions", "askmeanything", "youtuberlive"]
                }
            ],
            "growth": [
                {
                    "title": "Searchable How-To Tutorial",
                    "description": "Create a comprehensive tutorial solving a specific problem that people actively search for. Research keywords using YouTube's search suggestion feature to optimize the title and content.",
                    "best_formats": ["Tutorial video", "Step-by-step guide"],
                    "hashtags": ["youtubetutorial", "howtoguide", "problemsolved"]
                },
                {
                    "title": "Shorts to Long-Form Content Pipeline",
                    "description": "Create a YouTube Short that hooks viewers with an interesting tip or fact, then direct them to a full-length video that explores the topic comprehensively.",
                    "best_formats": ["YouTube Shorts", "Long-form video"],
                    "hashtags": ["youtubeshorts", "moreinfo", "deepdive"]
                },
                {
                    "title": "Trending Topic Analysis Video",
                    "description": "Create timely content addressing current trends, news, or developments in your industry. Add your unique perspective or expertise to make it stand out.",
                    "best_formats": ["Analysis video", "Commentary"],
                    "hashtags": ["trending", "newsanalysis", "hottopics"]
                }
            ],
            "conversion": [
                {
                    "title": "Case Study Results Video",
                    "description": "Create an in-depth case study video showcasing the journey of a customer or client who achieved significant results with your product or service. Include specific metrics and testimonials.",
                    "best_formats": ["Case study", "Success story"],
                    "hashtags": ["casestudy", "successstory", "resultsproof"]
                },
                {
                    "title": "Product Comparison Review",
                    "description": "Create an honest, detailed comparison between your product and alternatives, highlighting your unique advantages while remaining balanced in your assessment.",
                    "best_formats": ["Comparison video", "Review"],
                    "hashtags": ["comparisonreview", "bestchoice", "productshowdown"]
                },
                {
                    "title": "Problem-Based Tutorial with Solution Offer",
                    "description": "Create a helpful tutorial addressing a problem your audience faces, then naturally introduce your product or service as an enhanced solution toward the end of the video.",
                    "best_formats": ["Tutorial video", "Problem-solution format"],
                    "hashtags": ["problemsolver", "easysolution", "upgradeyourresults"]
                }
            ]
        },
        "linkedin": {
            "engagement": [
                {
                    "title": "Industry Poll with Insights Follow-Up",
                    "description": "Post a thought-provoking poll about a relevant industry topic, then share the results with your analysis in a follow-up post or article. Tag participants who commented to bring them back to the conversation.",
                    "best_formats": ["Poll post", "LinkedIn article"],
                    "hashtags": ["industryinsights", "professionalpoll", "expertanalysis"]
                },
                {
                    "title": "Career Lesson Storytelling Post",
                    "description": "Share a personal story about a professional challenge you faced and the key lessons learned. Format it with clear paragraphs, line breaks, and a reflective question at the end to encourage comments.",
                    "best_formats": ["Text post", "Personal narrative"],
                    "hashtags": ["careerlessons", "professionaljourney", "leadershipinsights"]
                },
                {
                    "title": "Contrarian Thought Leadership Piece",
                    "description": "Take a common industry belief or practice and present a well-reasoned alternative perspective. Back it with data and experience to start a meaningful discussion.",
                    "best_formats": ["LinkedIn article", "Opinion post"],
                    "hashtags": ["unpopularopinion", "thoughtleadership", "industrydisruption"]
                }
            ],
            "growth": [
                {
                    "title": "Collaborative Expert Roundup",
                    "description": "Create a post or article featuring insights from multiple industry experts on a specific topic. Tag all contributors to leverage their combined networks and establish yourself as a connector.",
                    "best_formats": ["LinkedIn article", "Carousel post"],
                    "hashtags": ["expertinsights", "industryvoices", "thoughtleaders"]
                },
                {
                    "title": "Data-Driven Industry Analysis",
                    "description": "Share original research or analysis of industry trends with clear visualizations and actionable takeaways. Include a clear call to action to follow you for more insights.",
                    "best_formats": ["Document post", "Data visualization"],
                    "hashtags": ["datadriveninsights", "industryanalysis", "markettrends"]
                },
                {
                    "title": "Valuable Resource Compilation",
                    "description": "Create and share a free resource like a checklist, template, or guide that addresses a common challenge in your industry. Request follows or connections in exchange for the value provided.",
                    "best_formats": ["Document post", "LinkedIn article with download"],
                    "hashtags": ["freeresource", "professionaldevelopment", "industrytoolkit"]
                }
            ],
            "conversion": [
                {
                    "title": "Client Success Spotlight",
                    "description": "Create a detailed post or article highlighting a client's success story. Include specific challenges, solutions, and measurable results while tagging the client to increase reach and credibility.",
                    "best_formats": ["Case study post", "Carousel testimonial"],
                    "hashtags": ["clientsuccess", "testimonial", "resultsdriven"]
                },
                {
                    "title": "Industry Challenge Solution Framework",
                    "description": "Identify a significant challenge facing your industry, then outline a clear framework for addressing it, with your service or expertise positioned as a critical component of the solution.",
                    "best_formats": ["LinkedIn article", "Document post"],
                    "hashtags": ["problemsolver", "businesssolutions", "expertframework"]
                },
                {
                    "title": "Event or Webinar Promotion Series",
                    "description": "Create a series of teaser posts highlighting key insights that will be shared in an upcoming webinar or event. Include clear registration information and emphasize limited availability if applicable.",
                    "best_formats": ["Event post", "Video invitation"],
                    "hashtags": ["upcomingwebinar", "professionaltraining", "limitedspots"]
                }
            ]
        },
        "facebook": {
            "engagement": [
                {
                    "title": "Community Question Thread",
                    "description": "Post a thought-provoking question related to your industry or niche that encourages meaningful responses. Reply to each comment to create threaded conversations and boost the post's algorithm visibility.",
                    "best_formats": ["Text post", "Question format"],
                    "hashtags": ["jointheconversation", "communityquestion", "tellus"]
                },
                {
                    "title": "Facebook Live Expert Session",
                    "description": "Host a Facebook Live session where you share expertise, demonstrate a process, or teach a skill. Promote it in advance, and actively respond to live comments during the broadcast.",
                    "best_formats": ["Facebook Live", "Interactive broadcast"],
                    "hashtags": ["facebooklive", "expertsession", "liveanswers"]
                },
                {
                    "title": "Nostalgia or Milestone Post",
                    "description": "Share a 'Throwback Thursday' or milestone celebration post that highlights your journey, company history, or industry evolution. Invite followers to share their own memories or experiences.",
                    "best_formats": ["Photo post", "Then vs now comparison"],
                    "hashtags": ["tbt", "throwbackthursday", "businessjourney"]
                }
            ],
            "growth": [
                {
                    "title": "Shareable Infographic or Guide",
                    "description": "Create a visually appealing infographic or guide that provides valuable information your audience will want to save and share with their networks. Include branding and a call to follow for more resources.",
                    "best_formats": ["Infographic", "Carousel guide"],
                    "hashtags": ["saveandshare", "usefulinfo", "freeguide"]
                },
                {
                    "title": "Viral Social Experiment or Challenge",
                    "description": "Launch a simple, engaging challenge that's easy for followers to participate in and share. Showcase participants' contributions to encourage more people to join in.",
                    "best_formats": ["Challenge post", "UGC compilation"],
                    "hashtags": ["joinchallenge", "communityspirit", "yourturn"]
                },
                {
                    "title": "Facebook Group Exclusive Content",
                    "description": "Create or leverage a Facebook Group to share exclusive content, fostering a sense of community while encouraging new members to join for access to these special resources.",
                    "best_formats": ["Group post", "Exclusive content"],
                    "hashtags": ["exclusivecontent", "membershipbenefits", "joinnow"]
                }
            ],
            "conversion": [
                {
                    "title": "Customer Testimonial Spotlight",
                    "description": "Share authentic customer testimonials with compelling visuals of the customer using your product or service. Include specific results and tag the featured customers when appropriate.",
                    "best_formats": ["Testimonial post", "Video testimonial"],
                    "hashtags": ["customerlove", "successstory", "realresults"]
                },
                {
                    "title": "Limited-Time Offer Announcement",
                    "description": "Create an eye-catching post announcing a special offer with clear expiration dates. Use Facebook's event reminder feature to notify interested users when the offer is about to end.",
                    "best_formats": ["Offer post", "Countdown announcement"],
                    "hashtags": ["limitedtimeoffer", "specialdeal", "actfast"]
                },
                {
                    "title": "Problem-Solution Video Series",
                    "description": "Create a short video series that clearly identifies common problems your audience faces and demonstrates how your product or service provides the ideal solution.",
                    "best_formats": ["Short video", "Demo series"],
                    "hashtags": ["problemsolved", "easysolution", "perfectfit"]
                }
            ]
        },
        "twitter": {
            "engagement": [
                {
                    "title": "Twitter Thread Expert Breakdown",
                    "description": "Create a numbered thread that breaks down a complex topic into digestible points. End with a question to encourage replies and further discussion.",
                    "best_formats": ["Thread", "Text posts"],
                    "hashtags": ["twitterthread", "expertbreakdown", "learnwithme"]
                },
                {
                    "title": "Twitter Poll with Analysis",
                    "description": "Post an interesting poll relevant to your industry, then share your analysis of the results and invite further discussion on the topic.",
                    "best_formats": ["Poll tweet", "Follow-up analysis"],
                    "hashtags": ["twitterpoll", "haveyoursay", "interestingresults"]
                },
                {
                    "title": "Quote Tweet Commentary Series",
                    "description": "Find relevant tweets from industry experts or news sources and add your unique perspective or additional insights through quote tweets.",
                    "best_formats": ["Quote tweets", "Commentary"],
                    "hashtags": ["perspective", "expertopinion", "joiningtheconversation"]
                }
            ],
            "growth": [
                {
                    "title": "Viral Hook + Link Tweet",
                    "description": "Craft tweets with powerful hooks, surprising statistics, or controversial questions followed by a link to your longer content. Focus on creating that initial curiosity that drives clicks.",
                    "best_formats": ["Hook + link", "Teaser tweet"],
                    "hashtags": ["clickable", "readmore", "fullstorybelow"]
                },
                {
                    "title": "Trending Hashtag Relevance",
                    "description": "Monitor trending hashtags and topics, then create timely content that connects these trends to your expertise or offerings in an authentic way.",
                    "best_formats": ["Trending topic tweet", "Newsjacking"],
                    "hashtags": ["trending", "currentevents", "relevantinsights"]
                },
                {
                    "title": "Helpful List Thread",
                    "description": "Create a thread of practical tips, resources, or insights that provides immediate value to your audience. Make each tweet in the thread valuable enough to stand alone if shared.",
                    "best_formats": ["Numbered thread", "Tips collection"],
                    "hashtags": ["usefultips", "savethread", "resourcethread"]
                }
            ],
            "conversion": [
                {
                    "title": "Exclusive Offer Tweet",
                    "description": "Create tweets announcing Twitter-exclusive offers or early access opportunities for your followers. Include a clear, direct link to the offer landing page.",
                    "best_formats": ["Offer announcement", "Exclusive deal"],
                    "hashtags": ["twitterexclusive", "specialoffer", "limitedtime"]
                },
                {
                    "title": "Social Proof Spotlight",
                    "description": "Share screenshots of positive customer feedback, testimonials, or impressive metrics. Briefly explain the value provided to establish credibility.",
                    "best_formats": ["Testimonial tweet", "Results showcase"],
                    "hashtags": ["customerfeedback", "socialproof", "results"]
                },
                {
                    "title": "Pain Point + Solution Tweet",
                    "description": "Identify a specific customer pain point in a tweet, then introduce your solution with a clear call to action and link for more information.",
                    "best_formats": ["Problem-solution format", "Direct CTA"],
                    "hashtags": ["solution", "problemsolved", "checkitout"]
                }
            ]
        }
    }
    
    # Select the relevant platform
    if platform.lower() in all_platform_ideas:
        platform_content = all_platform_ideas[platform.lower()]
        
        # Select content based on metric
        if metric.lower() in platform_content:
            content_ideas = platform_content[metric.lower()]
        else:
            # If metric not found, use engagement as default
            content_ideas = platform_content.get("engagement", [])
            
        return content_ideas
    else:
        # Fallback to generic ideas if platform not found
        return [
            {
                "title": "Behind-the-Scenes Content",
                "description": "Share the process behind your work or daily operations. This humanizes your brand and builds authenticity.",
                "best_formats": ["Video", "Image carousel", "Stories"]
            },
            {
                "title": "User-Generated Content Highlight",
                "description": "Showcase content created by your audience that features your product or service.",
                "best_formats": ["Repost", "Image", "Video"]
            },
            {
                "title": "Industry News Commentary",
                "description": "Share your perspective on recent industry developments to demonstrate expertise.",
                "best_formats": ["Text post", "Video", "Carousel"]
            }
        ]

def generate_with_gemini(platform, metric, trend_data, api_key):
    """Generate content ideas using Google's Gemini AI."""
    try:
        # Import here to avoid dependency if not used
        import google.generativeai as genai
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
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
        
        # Set up the model - get available models
        models = genai.list_models()
        # Use the first available text generation model
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        if available_models:
            model_name = available_models[0]
            logger.info(f"Using Gemini model: {model_name}")
            model = genai.GenerativeModel(model_name)
        else:
            # Fall back to the most common model name
            logger.info("No models found, trying gemini-1.5-pro")
            model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Extract the text from the response
        content = response.text
        
        # Try to find and parse JSON in the response
        try:
            # Extract JSON content
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
            "provider": "gemini",
            "ideas": ideas,
            "message": "Content ideas generated successfully with Google Gemini."
        }
    except ImportError:
        logger.error("Google Generative AI package not installed")
        return {
            "status": "error",
            "message": "Google Generative AI package not installed. Please install it with: pip install google-generativeai",
            "ideas": get_fallback_ideas(platform, metric)
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error with Gemini: {error_message}")
        
        return {
            "status": "error",
            "message": f"Error with Gemini API: {error_message}",
            "ideas": get_fallback_ideas(platform, metric)
        }

def check_ai_availability():
    """Check if AI services are available based on API keys."""
    openai_available = get_api_key("openai") is not None
    anthropic_available = get_api_key("anthropic") is not None
    gemini_available = get_api_key("gemini") is not None
    
    return {
        "openai": openai_available,
        "anthropic": anthropic_available,
        "gemini": gemini_available,
        "any_available": openai_available or anthropic_available or gemini_available
    }