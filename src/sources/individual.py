"""
Sources from the Individual/Project spreadsheet tab.

These are primarily individual journalist fellowships.
Ref: https://docs.google.com/spreadsheets/d/1vQs72vGfa2_LWBNMbVAr3WCeusTGrAIKSjkGtTR84Xo
     tab: Individual/Project
"""

from typing import TypedDict


class Source(TypedDict):
    name: str
    url: str
    focus: str


INDIVIDUAL_SOURCES: list[Source] = [
    {
        "name": "19th News Fellowship",
        "url": "https://19thnews.org/apply-for-a-19th-news-fellowship/",
        "focus": "General journalism, environmental coverage",
    },
    {
        "name": "Arthur L. Carter Journalism Institute – Reporting Award",
        "url": "https://journalism.nyu.edu/about-us/awards-and-fellowships/the-reporting-award/",
        "focus": "General reporting",
    },
    {
        "name": "Ben Bagdikian Fellowship / Mother Jones",
        "url": "https://www.motherjones.com/careers/fellowships/",
        "focus": "Investigative journalism",
    },
    {
        "name": "Edward R. Murrow Press Fellowship",
        "url": "https://www.cfr.org/fellowships/edward-r-murrow-press-fellowship",
        "focus": "Global affairs, international reporting",
    },
    {
        "name": "Fund for Investigative Journalism",
        "url": "https://fij.org/grantees-work/",
        "focus": "Investigative reporting",
    },
    {
        "name": "Nieman Foundation for Journalism at Harvard",
        "url": "https://nieman.harvard.edu/fellowships/",
        "focus": "General journalism advancement",
    },
    {
        "name": "Pulitzer Center – Reporting Grants and Fellowships",
        "url": "https://pulitzercenter.org/opportunities/reporting-grants-fellowships",
        "focus": "Gender equity, climate, AI accountability, international reporting",
    },
    {
        "name": "Spencer Fellowship for Education Reporting",
        "url": "https://spencerfellows.org/about-the-fellowship/",
        "focus": "Education journalism",
    },
]
