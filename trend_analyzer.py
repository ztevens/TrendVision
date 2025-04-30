"""
Trend Analyzer Module for TrendVision AI

This module provides trend analysis and content suggestions based on social media data.
It identifies trending topics, engagement patterns, and provides actionable content ideas.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Predefined trend patterns and content suggestions
SOCIAL_MEDIA_TRENDS = {
    "Twitter": {
        "current_trends": [
            "Short-form commentary on current events",
            "Thread storytelling",
            "Visual sharing with carousel posts",
            "Community-focused discussions",
            "Real-time reactions to global events"
        ],
        "emerging_trends": [
            "Interactive polls with engaging follow-ups",
            "Creator collabs across different niches",
            "AI-generated content fusion",
            "Voice conversations and Spaces",
            "Behind-the-scenes authentic moments"
        ],
        "content_strategies": {
            "Engagement": [
                "Ask thought-provoking questions that invite diverse opinions",
                "Create threads that tell compelling stories over multiple posts",
                "Share insider knowledge that helps your audience solve problems",
                "Participate in trending conversations with unique perspectives",
                "Use custom graphics that stand out in the timeline"
            ],
            "Followers": [
                "Maintain a consistent posting schedule (3-5 times daily)",
                "Develop a unique voice that differentiates you from others",
                "Engage with replies personally rather than with generic responses",
                "Join Twitter Spaces as a speaker in your niche",
                "Cross-promote with complementary creators"
            ],
            "Reach": [
                "Leverage trending hashtags when relevant to your content",
                "Time posts to your audience's peak activity hours",
                "Create content formats that encourage sharing (lists, how-tos)",
                "Tag relevant accounts when appropriate (but not excessive)",
                "Participate in viral challenges with your unique spin"
            ],
            "Impressions": [
                "Use eye-catching visuals that stop the scroll",
                "Write compelling first lines that hook readers immediately",
                "Create content series that keep followers coming back",
                "Position yourself as a thought leader with original insights",
                "Incorporate timely topics while maintaining your niche focus"
            ]
        }
    },
    "Facebook": {
        "current_trends": [
            "Long-form storytelling content",
            "Community group discussions",
            "Live video events and Q&As",
            "Nostalgia and memory-based content",
            "Educational and informative posts"
        ],
        "emerging_trends": [
            "Interactive group challenges",
            "Hybrid event experiences",
            "Specialized community building",
            "Creator subscriptions and exclusive content",
            "AR-enhanced promotional content"
        ],
        "content_strategies": {
            "Engagement": [
                "Create polls that tap into current discussions in your niche",
                "Share personal stories that resonate with your audience's experiences",
                "Post discussion starters that encourage community conversation",
                "Use carousel posts to tell visual stories with multiple images",
                "Host regular live sessions addressing audience questions"
            ],
            "Followers": [
                "Create a content calendar mixing educational, entertaining, and promotional posts",
                "Build an active Facebook Group around your niche",
                "Cross-promote your Facebook content on other platforms",
                "Use Facebook Stories to maintain daily visibility",
                "Collaborate with complementary Pages for wider exposure"
            ],
            "Reach": [
                "Time posts for when your specific audience is most active",
                "Create shareable graphics with valuable information",
                "Develop topical content related to seasonal events",
                "Encourage tagging in comments to expand organic reach",
                "Repurpose your best-performing content in new formats"
            ],
            "Impressions": [
                "Use eye-catching thumbnails for video content",
                "Create native videos directly uploaded to Facebook",
                "Write headlines that provoke curiosity without being clickbait",
                "Design posts with mobile viewers in mind (most Facebook traffic)",
                "Vary content formats to appeal to different segments of your audience"
            ]
        }
    },
    "Instagram": {
        "current_trends": [
            "Authentic behind-the-scenes content",
            "Carousel posts with multiple images/slides",
            "Short-form video storytelling",
            "Interactive Stories with polls/questions",
            "Aesthetic and visually cohesive feeds"
        ],
        "emerging_trends": [
            "AI-enhanced creative content",
            "Collaborative reels with trending sounds",
            "Augmented reality filters and effects",
            "Shoppable posts linking to products",
            "Creator collectives and partnerships"
        ],
        "content_strategies": {
            "Engagement": [
                "Create carousel posts with multiple valuable tips",
                "Use the question sticker in Stories to gather audience input",
                "Respond to comments with thoughtful, personalized replies",
                "Share user-generated content with proper credit",
                "Create Reels that educate while entertaining"
            ],
            "Followers": [
                "Maintain a consistent aesthetic that makes your profile visually appealing",
                "Post Instagram guides compiling valuable resources",
                "Use strategic hashtags specific to your niche (mix of popular and targeted)",
                "Host Instagram Lives with other creators in your space",
                "Create content series that followers anticipate"
            ],
            "Reach": [
                "Leverage trending audio in Reels to increase discoverability",
                "Post consistently during your audience's peak engagement times",
                "Create saveable content that provides lasting value",
                "Participate in Instagram challenges relevant to your niche",
                "Cross-promote your Instagram content on other platforms"
            ],
            "Impressions": [
                "Design eye-catching graphics that stop the scroll",
                "Use strong color contrast in thumbnails and first slides",
                "Create content that encourages multiple views (tutorials, how-tos)",
                "Optimize your profile with relevant keywords",
                "Batch create content to maintain consistent quality"
            ]
        }
    },
    "LinkedIn": {
        "current_trends": [
            "Professional storytelling with personal elements",
            "Thought leadership articles",
            "Career development advice",
            "Industry insights and analysis",
            "Professional milestone celebrations"
        ],
        "emerging_trends": [
            "Video resumes and introductions",
            "Professional community building",
            "Live expert discussions and panels",
            "Learning-focused content series",
            "Interactive career development tools"
        ],
        "content_strategies": {
            "Engagement": [
                "Share personal career lessons with actionable takeaways",
                "Create posts that ask for professional opinions on industry topics",
                "Write 'how I did it' stories that provide genuine value",
                "Comment thoughtfully on posts from industry leaders",
                "Share interesting industry statistics with your analysis"
            ],
            "Followers": [
                "Establish a consistent posting cadence (3-5 times weekly)",
                "Create content pillars around your professional expertise",
                "Engage with commenters in meaningful conversations",
                "Share a mix of original content and curated industry news",
                "Highlight team members and company culture (if appropriate)"
            ],
            "Reach": [
                "Use relevant industry hashtags (3-5 per post maximum)",
                "Tag individuals mentioned in posts (when appropriate)",
                "Create LinkedIn articles for in-depth topics",
                "Participate in industry group discussions",
                "Cross-promote LinkedIn content through your email signature"
            ],
            "Impressions": [
                "Start posts with a compelling hook or statistic",
                "Use slide carousels for step-by-step advice",
                "Break up text with bullet points and white space",
                "Include a clear call-to-action in posts",
                "Share content during business hours on weekdays"
            ]
        }
    },
    "TikTok": {
        "current_trends": [
            "Educational content in entertaining formats",
            "Authentic day-in-the-life videos",
            "Trending sound and dance challenges",
            "Behind-the-scenes glimpses",
            "Quick tutorials and hacks"
        ],
        "emerging_trends": [
            "AI-powered visual effects",
            "Collaborative split-screen content",
            "Interactive challenges with audience participation",
            "Niche-focused serialized content",
            "Live shopping and product demonstrations"
        ],
        "content_strategies": {
            "Engagement": [
                "Create videos that ask viewers to share their opinions in the comments",
                "Use trending sounds in creative ways specific to your niche",
                "Respond to comments with follow-up videos",
                "Stitch popular videos with your unique perspective",
                "Create content that shows your authentic personality"
            ],
            "Followers": [
                "Post consistently (1-3 times daily)",
                "Develop a recognizable content style or format",
                "Interact with followers in comments and through duets",
                "Create series content that keeps viewers coming back",
                "Participate in trending challenges that fit your brand"
            ],
            "Reach": [
                "Study TikTok trends and adapt them to your niche",
                "Use 3-5 relevant hashtags including a mix of trending and niche tags",
                "Create content around seasonal events and holidays",
                "Optimize for watch time with engaging hooks in the first 3 seconds",
                "Cross-promote your TikTok content on other platforms"
            ],
            "Impressions": [
                "Use strong hooks in the first second of your videos",
                "Create content that encourages multiple views",
                "Develop recognizable visual elements (filters, transitions, etc.)",
                "Post when your audience is most active",
                "Keep videos concise and focused on a single concept"
            ]
        }
    },
    "YouTube": {
        "current_trends": [
            "Long-form deep dives into specialized topics",
            "High-value tutorial and educational content",
            "Day-in-the-life and behind-the-scenes vlogs",
            "Commentary on current events/trends",
            "Storytelling and narrative-driven content"
        ],
        "emerging_trends": [
            "Multi-format content with Shorts integration",
            "Interactive video experiences",
            "Community tab engagement strategies",
            "Cross-platform content universes",
            "Specialized series for channel members"
        ],
        "content_strategies": {
            "Engagement": [
                "Ask specific questions in your videos that prompt comment responses",
                "Create content that addresses viewer questions from previous videos",
                "Use cards and end screens to encourage further viewing",
                "Include calls-to-action at strategic points in your videos",
                "Hold premiere events for major video releases"
            ],
            "Followers": [
                "Maintain a consistent uploading schedule (communicate any changes)",
                "Create a clear content value proposition for your channel",
                "Develop playlists that organize your content by themes or topics",
                "Use YouTube Community posts between video uploads",
                "Create Shorts that drive viewers to your long-form content"
            ],
            "Reach": [
                "Research keywords for titles, descriptions, and tags",
                "Create custom thumbnails with consistent branding",
                "Optimize video descriptions with timestamps and links",
                "Collaborate with complementary creators in your niche",
                "Analyze your Analytics to understand what content performs best"
            ],
            "Impressions": [
                "Design eye-catching thumbnails with clear text and high contrast",
                "Craft titles that balance searchability with click-appeal",
                "Create intros that immediately communicate video value",
                "Keep viewers engaged with pattern interrupts throughout videos",
                "Maintain high production quality appropriate for your niche"
            ]
        }
    }
}

def analyze_trend_data(data):
    """
    Analyze trend data to identify patterns and insights.
    
    Args:
        data (pd.DataFrame): Data to analyze
        
    Returns:
        dict: Dictionary containing trend analysis and insights
    """
    if data is None or len(data) == 0:
        return {
            "status": "error",
            "message": "No data available for analysis"
        }
    
    # Initialize results
    results = {
        "status": "success",
        "platform": data.get("platform", ["Unknown"])[0] if "platform" in data else "Unknown",
        "metric": data.get("metric", ["Unknown"])[0] if "metric" in data else "Unknown",
        "period_analyzed": f"{data['date'].min().strftime('%Y-%m-%d')} to {data['date'].max().strftime('%Y-%m-%d')}",
        "data_points": len(data),
        "insights": {},
        "trend_patterns": {},
        "recommendations": {}
    }
    
    # Extract platform and metric if available
    platform = results["platform"]
    metric = results["metric"]
    
    # Get overall trend direction
    if "value" in data.columns and len(data) > 1:
        first_value = data["value"].iloc[0]
        last_value = data["value"].iloc[-1]
        percent_change = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        
        results["insights"]["overall_trend"] = {
            "direction": "up" if percent_change > 0 else "down" if percent_change < 0 else "flat",
            "percent_change": round(percent_change, 2),
            "interpretation": get_trend_interpretation(percent_change, platform, metric)
        }
        
        # Calculate volatility
        std_dev = data["value"].std()
        mean = data["value"].mean()
        volatility = (std_dev / mean) if mean != 0 else 0
        
        results["insights"]["volatility"] = {
            "value": round(volatility * 100, 2),
            "interpretation": get_volatility_interpretation(volatility, platform, metric)
        }
        
        # Identify seasonality if enough data
        if len(data) >= 14:  # At least two weeks of data
            data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
            day_avg = data.groupby('day_of_week')['value'].mean()
            max_day = day_avg.idxmax()
            min_day = day_avg.idxmin()
            day_names = {
                0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
            }
            
            results["insights"]["seasonality"] = {
                "best_day": day_names[max_day],
                "worst_day": day_names[min_day],
                "day_variance": round((day_avg.max() - day_avg.min()) / day_avg.mean() * 100, 2)
            }
    
    # Get upcoming trend predictions
    results["trend_patterns"] = get_trend_patterns(platform)
    
    # Get content recommendations
    results["recommendations"] = get_content_recommendations(platform, metric)
    
    return results

def get_trend_interpretation(percent_change, platform, metric):
    """Get interpretation of trend based on percent change."""
    if platform == "Unknown" or metric == "Unknown":
        if percent_change > 20:
            return "Significant upward trend indicates strong positive momentum."
        elif percent_change > 5:
            return "Moderate growth showing positive direction."
        elif percent_change > -5:
            return "Relatively stable performance with minimal change."
        elif percent_change > -20:
            return "Moderate decline suggesting attention is needed."
        else:
            return "Significant downward trend requiring strategic intervention."
    
    # Platform and metric specific interpretations
    if metric == "Engagement":
        if percent_change > 15:
            return f"Exceptional engagement growth suggesting content is strongly resonating with {platform} audience."
        elif percent_change > 5:
            return f"Healthy engagement increase indicating improved content relevance on {platform}."
        elif percent_change > -5:
            return f"Steady engagement levels maintaining audience interest on {platform}."
        elif percent_change > -15:
            return f"Declining engagement suggesting need for content refresh on {platform}."
        else:
            return f"Significant engagement drop requiring content strategy revision for {platform}."
    
    elif metric == "Followers":
        if percent_change > 10:
            return f"Strong follower growth indicating expanding audience reach on {platform}."
        elif percent_change > 3:
            return f"Healthy follower acquisition rate for {platform}."
        elif percent_change > -2:
            return f"Stable follower count maintaining current audience base on {platform}."
        elif percent_change > -10:
            return f"Follower decline suggesting need for audience retention strategies on {platform}."
        else:
            return f"Significant follower loss requiring audience reconnection strategy for {platform}."
    
    elif metric == "Reach":
        if percent_change > 20:
            return f"Exceptional reach expansion suggesting algorithm favorability on {platform}."
        elif percent_change > 8:
            return f"Improved content distribution across {platform} network."
        elif percent_change > -8:
            return f"Consistent reach maintaining visibility on {platform}."
        elif percent_change > -20:
            return f"Declining reach suggesting need for content format optimization on {platform}."
        else:
            return f"Significant reach reduction requiring distribution strategy revision for {platform}."
    
    elif metric == "Impressions":
        if percent_change > 25:
            return f"Exceptional visibility growth across {platform}."
        elif percent_change > 10:
            return f"Improved content discovery and repetition on {platform}."
        elif percent_change > -10:
            return f"Steady impression count maintaining current visibility on {platform}."
        elif percent_change > -25:
            return f"Declining impressions suggesting need for more shareable content on {platform}."
        else:
            return f"Significant impression loss requiring content format and distribution revision."
    
    # Generic response if metric doesn't match
    return f"Trend shows {round(percent_change, 1)}% change over the analyzed period."

def get_volatility_interpretation(volatility, platform, metric):
    """Get interpretation of volatility based on coefficient of variation."""
    if volatility < 0.1:
        stability = "Very stable"
    elif volatility < 0.2:
        stability = "Relatively stable"
    elif volatility < 0.3:
        stability = "Moderately volatile"
    elif volatility < 0.5:
        stability = "Highly volatile"
    else:
        stability = "Extremely volatile"
    
    if platform == "Unknown" or metric == "Unknown":
        return f"{stability} performance indicating {get_volatility_recommendation(stability.lower())}."
    
    platform_context = {
        "Twitter": "fast-paced environment",
        "Facebook": "algorithm-driven timeline",
        "Instagram": "competitive feed",
        "LinkedIn": "professional network",
        "TikTok": "trend-driven platform",
        "YouTube": "recommendation-based platform"
    }.get(platform, "social media environment")
    
    metric_context = {
        "Engagement": "audience interaction",
        "Followers": "audience growth",
        "Reach": "content distribution",
        "Impressions": "content visibility"
    }.get(metric, "performance")
    
    return f"{stability} {metric_context} in {platform}'s {platform_context}. {get_volatility_recommendation(stability.lower(), platform, metric)}"

def get_volatility_recommendation(stability_level, platform=None, metric=None):
    """Get recommendation based on volatility level."""
    if stability_level in ["very stable", "relatively stable"]:
        if platform and metric:
            if metric == "Engagement":
                return f"Continue current content strategy while testing new formats to find growth opportunities on {platform}"
            elif metric == "Followers":
                return f"Maintain consistency while gradually expanding content topics to attract new audience segments on {platform}"
            elif metric == "Reach":
                return f"Leverage this stability by developing deeper content series that build on previous success on {platform}"
            elif metric == "Impressions":
                return f"Focus on increasing other metrics while maintaining this stable visibility foundation on {platform}"
        return "Indicates consistent performance that can be leveraged for predictable growth"
    
    elif stability_level == "moderately volatile":
        if platform and metric:
            if metric == "Engagement":
                return f"Analyze which content types perform best and focus strategy accordingly on {platform}"
            elif metric == "Followers":
                return f"Implement more consistent posting schedule to stabilize follower acquisition on {platform}"
            elif metric == "Reach":
                return f"Diversify content formats to reduce dependence on algorithm changes on {platform}"
            elif metric == "Impressions":
                return f"Test different posting times to determine optimal visibility windows on {platform}"
        return "Suggests need for more consistent strategy to stabilize performance"
    
    else:  # highly or extremely volatile
        if platform and metric:
            if metric == "Engagement":
                return f"Urgently review content strategy to identify what drives peaks and eliminate what causes valleys on {platform}"
            elif metric == "Followers":
                return f"Focus on retention strategies and consistent value delivery to reduce audience churn on {platform}"
            elif metric == "Reach":
                return f"Develop a more diverse content distribution strategy less dependent on single platform algorithms on {platform}"
            elif metric == "Impressions":
                return f"Establish a more consistent content calendar with reliable formats on {platform}"
        return "Indicates need for strategic intervention to create more predictable outcomes"

def get_trend_patterns(platform):
    """Get current and emerging trend patterns for a platform."""
    if platform in SOCIAL_MEDIA_TRENDS:
        return {
            "current_trends": SOCIAL_MEDIA_TRENDS[platform]["current_trends"],
            "emerging_trends": SOCIAL_MEDIA_TRENDS[platform]["emerging_trends"],
        }
    
    # Default trends for unknown platform
    return {
        "current_trends": [
            "Authentic, behind-the-scenes content",
            "Short-form video formats",
            "Interactive content encouraging audience participation",
            "User-generated content collaborations",
            "Purpose-driven messaging connecting to values"
        ],
        "emerging_trends": [
            "AI-enhanced creative content",
            "Cross-platform content strategies",
            "Community-focused engagement initiatives",
            "Creator collaborations across niches",
            "Personalized content experiences"
        ]
    }

def get_content_recommendations(platform, metric):
    """Get content recommendations for a platform and metric."""
    if platform in SOCIAL_MEDIA_TRENDS and metric in SOCIAL_MEDIA_TRENDS[platform]["content_strategies"]:
        strategies = SOCIAL_MEDIA_TRENDS[platform]["content_strategies"][metric]
        return {
            "content_strategies": strategies,
            "posting_tips": get_posting_tips(platform),
            "content_ideas": generate_content_ideas(platform, metric)
        }
    
    # Default recommendations
    return {
        "content_strategies": [
            "Create valuable content that solves problems for your audience",
            "Establish a consistent posting schedule",
            "Engage authentically with your audience's comments",
            "Use analytics to refine and improve your strategy",
            "Develop a unique voice that differentiates you from competitors"
        ],
        "posting_tips": get_posting_tips(platform),
        "content_ideas": generate_content_ideas(platform, metric)
    }

def get_posting_tips(platform):
    """Get posting tips for a specific platform."""
    platform_tips = {
        "Twitter": [
            "Optimal posting times: 8-10am, 12-1pm, 5-6pm on weekdays",
            "Tweet length: 71-100 characters get most engagement",
            "Include 1-2 relevant hashtags (not more)",
            "Tweets with images get 150% more retweets",
            "Threads (3-5 tweets) get more engagement than single tweets"
        ],
        "Facebook": [
            "Optimal posting times: 1-4pm on weekdays, 12-1pm on weekends",
            "Post length: 40-80 characters get most engagement",
            "Videos get 59% more engagement than other post types",
            "Posts with questions get 100% more comments",
            "Posting 3-5 times per week is optimal for most brands"
        ],
        "Instagram": [
            "Optimal posting times: 11am-1pm, 7-9pm on weekdays",
            "Use 8-15 hashtags for optimal discovery",
            "Carousel posts get 1.4x more reach than single images",
            "Square or portrait images perform better than landscape",
            "Stories with interactive elements get 2-3x more engagement"
        ],
        "LinkedIn": [
            "Optimal posting times: 8-10am, 12pm on weekdays",
            "Articles of 1,900-2,000 words perform best",
            "Posts with 'how-to' and list formats get 2x more views",
            "Adding documents to posts increases engagement by 3x",
            "Posting 2-5 times per week is optimal for engagement"
        ],
        "TikTok": [
            "Optimal posting times: 6-9am, 7-11pm for US audience",
            "Videos 21-34 seconds long get highest engagement",
            "First 3 seconds are critical for retention",
            "Using 3-5 relevant hashtags improves discovery",
            "Posting 1-3 times daily improves algorithm favor"
        ],
        "YouTube": [
            "Optimal posting times: 2-4pm on weekdays, 10-11am on weekends",
            "Videos 7-15 minutes long get best engagement/retention balance",
            "First 15 seconds determine if viewers will continue watching",
            "Custom thumbnails get 90% higher click-through rates",
            "Posting consistently on the same days/times builds viewership"
        ]
    }
    
    return platform_tips.get(platform, [
        "Analyze when your specific audience is most active",
        "Maintain consistent posting frequency",
        "Focus on quality over quantity",
        "Use native content formats for each platform",
        "Test different content types to find what resonates"
    ])

def generate_content_ideas(platform, metric):
    """Generate specific content ideas based on platform and metric."""
    # General ideas that work across platforms
    general_ideas = [
        "Day-in-the-life content showing behind-the-scenes of your work",
        "Tutorial or how-to content solving a specific problem",
        "Industry myth debunking or fact-checking",
        "Trend analysis with your professional perspective",
        "Success story or case study highlighting results"
    ]
    
    # Platform-specific content ideas
    platform_ideas = {
        "Twitter": {
            "Engagement": [
                "Start a collaborative thread asking for tips from your community",
                "Create a Twitter poll on a trending industry topic",
                "Share a controversial (but thoughtful) hot take on your industry",
                "Post before/after transformation with key lessons learned",
                "Create a 'tweet clinic' reviewing examples with permission"
            ],
            "Followers": [
                "Create a 'X tips in X days' series with daily value",
                "Share curated industry news with your expert commentary",
                "Create 'if you only read one thread this week' recommendations",
                "Start meaningful conversations with influencers in your niche",
                "Create a 'whitepaper in a thread' summarizing key research"
            ],
            "Reach": [
                "Join trending hashtag conversations with relevant perspectives",
                "Create tweet templates people can save and customize",
                "Develop shareable infographics with key statistics",
                "Post timely reactions to industry news or announcements",
                "Create 'save this thread' resource collections"
            ],
            "Impressions": [
                "Use contrasting colors in images to stand out in the timeline",
                "Share surprising statistics with eye-catching visualizations",
                "Create 'expectation vs. reality' comparison posts",
                "Develop a consistent visual brand for your tweets",
                "Use emojis strategically to break up text and add personality"
            ]
        },
        "Facebook": {
            "Engagement": [
                "Create 'Fill in the blank' posts related to your industry",
                "Post 'This or That' questions with images representing choices",
                "Share a relatable industry story with 'Has this happened to you?'",
                "Run a 'Weekly Challenge' related to your niche",
                "Create 'Caption This' posts with industry-relevant images"
            ],
            "Followers": [
                "Develop a themed series that posts on the same day weekly",
                "Create a resource guide that can be downloaded from your Page",
                "Run a community spotlight featuring followers/customers",
                "Share industry news roundups with your analysis",
                "Develop 'Facebook Watch Parties' around relevant content"
            ],
            "Reach": [
                "Create shareable graphics with inspirational industry quotes",
                "Develop 'tag a friend who needs to see this' content",
                "Create posts around national/international awareness days",
                "Share user-generated content with proper credit",
                "Develop content tied to current events with your perspective"
            ],
            "Impressions": [
                "Create carousel posts with educational slides",
                "Use text overlay on images to convey key messages",
                "Create short, native Facebook videos with captions",
                "Use bright, contrasting colors in featured images",
                "Create 'swipe through' posts with multiple tips"
            ]
        },
        "Instagram": {
            "Engagement": [
                "Create 'save this' carousel with actionable industry tips",
                "Share a behind-the-scenes Instagram Story with a poll",
                "Post a transformation Reel with before/after results",
                "Create 'Fill in the blank' caption prompts",
                "Share a problem-solving carousel with 'Did you know?' hooks"
            ],
            "Followers": [
                "Create a branded Instagram guide with curated resources",
                "Start a weekly Q&A session using the question sticker",
                "Develop a consistent visual theme across your grid",
                "Share user testimonials or success stories as carousels",
                "Create 'Meet the team/person' content humanizing your brand"
            ],
            "Reach": [
                "Create infographic carousels people will want to save",
                "Join trending Reels challenges with your brand twist",
                "Share timely content around seasonal events",
                "Create 'bookmark this for later' educational content",
                "Develop shareable quotes or statistics as standalone posts"
            ],
            "Impressions": [
                "Use bright, attention-grabbing colors in your thumbnails",
                "Create stop-motion or timelapse content showing processes",
                "Use text overlays to communicate key messages in Reels",
                "Share before/after transformations with dramatic contrast",
                "Create 'how it started vs. how it's going' comparative content"
            ]
        },
        "LinkedIn": {
            "Engagement": [
                "Share a career lesson and ask 'What would you have done?'",
                "Create a 'hot take' post challenging industry conventions",
                "Share a 'what I'm seeing in the industry' trend analysis",
                "Post a professional achievement with lessons learned",
                "Create 'agree or disagree?' posts on industry practices"
            ],
            "Followers": [
                "Create a career development series with actionable steps",
                "Share industry research with your professional analysis",
                "Create 'Expert Spotlight' content featuring thought leaders",
                "Develop a 'skills spotlight' series focusing on different competencies",
                "Share professional resources you've created or curated"
            ],
            "Reach": [
                "Create 'Top 5 Trends in [Industry]' listicle posts",
                "Share data-driven insights with original graphics",
                "Create 'lessons from my career' storytelling posts",
                "Share contrarian but well-reasoned perspectives on industry norms",
                "Create 'Template Tuesday' with professional document examples"
            ],
            "Impressions": [
                "Use document posts with branded cover pages",
                "Create slide decks with key statistics or insights",
                "Develop 'Sunday evening preparation' posts for the week ahead",
                "Share 'Myth vs. Reality' posts debunking industry misconceptions",
                "Create 'Monday Motivation' posts with professional development focus"
            ]
        },
        "TikTok": {
            "Engagement": [
                "Create a 'Tell me in the comments' hook about an industry topic",
                "Share a 'Things I wish I knew before starting in [industry]' list",
                "Create a duet-friendly template others can respond to",
                "Share an industry hack with 'Did you know this trick?'",
                "Create a 'Green/Red Flag' series about industry practices"
            ],
            "Followers": [
                "Start a daily/weekly series with consistent branding",
                "Create 'POV' content showing different perspectives in your field",
                "Share 'A day in the life' content showing your work process",
                "Create before/after transformation videos with dramatic reveals",
                "Develop tutorial series breaking down complex skills"
            ],
            "Reach": [
                "Use trending sounds with relevant industry content",
                "Create 'Top 5' countdowns with engaging visuals",
                "Share rapid-fire tips in your area of expertise",
                "Create transition videos showing impressive transformations",
                "Develop 'Things I wish I knew sooner' advice content"
            ],
            "Impressions": [
                "Use text overlays that make bold statements or ask questions",
                "Create stop-motion content showing processes or transformations",
                "Use contrast filters to make your videos visually distinct",
                "Start videos with a controversial or surprising statement",
                "Create 'wait for it' style videos with unexpected outcomes"
            ]
        },
        "YouTube": {
            "Engagement": [
                "Create 'Ask Me Anything' videos addressing audience questions",
                "Start a series where viewers can suggest topics in comments",
                "Create reaction videos to industry news or developments",
                "Develop a case study series featuring detailed analysis",
                "Create 'subscriber spotlight' videos featuring community members"
            ],
            "Followers": [
                "Create an evergreen tutorial series answering common questions",
                "Develop a consistent intro/outro to build channel recognition",
                "Create a 'Start Here' playlist for new subscribers",
                "Develop long-form deep dives into specialized topics",
                "Create behind-the-scenes videos showing your work process"
            ],
            "Reach": [
                "Research top keywords in your niche for titles and descriptions",
                "Create videos addressing trending topics in your industry",
                "Develop list-based videos ('Top 10' formats perform well)",
                "Create tutorial content solving specific problems",
                "Develop comparison videos ('X vs Y' formats)"
            ],
            "Impressions": [
                "Create custom thumbnails with faces showing emotion",
                "Use bright, contrasting colors and clear text in thumbnails",
                "Keep titles under 60 characters for full visibility",
                "Create intriguing titles using questions or numbers",
                "Use hashtags in descriptions (3-5 is optimal)"
            ]
        }
    }
    
    # If we have specific ideas for this platform and metric, use those
    if platform in platform_ideas and metric in platform_ideas[platform]:
        specific_ideas = platform_ideas[platform][metric]
        return specific_ideas + general_ideas[:2]  # Combine with some general ideas
    
    # If we have ideas for this platform but not metric, use platform ideas
    elif platform in platform_ideas:
        # Get a mix of ideas from different metrics for this platform
        mixed_ideas = []
        for m in platform_ideas[platform]:
            mixed_ideas.append(platform_ideas[platform][m][0])  # Take first idea from each metric
        return mixed_ideas + general_ideas[:3]
    
    # Otherwise use general ideas
    return general_ideas