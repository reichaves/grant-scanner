"""
Sources from the Institucional spreadsheet tab.

These cover both individual fellowships and institutional grants, with a broader
set of opportunities than the Individual/Project tab.
Ref: https://docs.google.com/spreadsheets/d/1vQs72vGfa2_LWBNMbVAr3WCeusTGrAIKSjkGtTR84Xo
     tab: Institucional
"""

from typing import TypedDict


class Source(TypedDict):
    name: str
    url: str
    focus: str


INSTITUTIONAL_SOURCES: list[Source] = [
    {
        "name": "Above the Fray Fellowship",
        "url": "https://www.thejohnalexanderproject.org/faq",
        "focus": "Strengthening democracy, new narratives",
    },
    {
        "name": "AHCJ Health System Reporting Fellowship",
        "url": "https://healthjournalism.org/fellowships/ahcj-reporting-fellowships-on-health-care-performance/",
        "focus": "Health reporting",
    },
    {
        "name": "Alicia Patterson Fellowship",
        "url": "https://aliciapatterson.org/apply/",
        "focus": "General reporting",
    },
    {
        "name": "American Council on Germany – Kellen Fellowship",
        "url": "https://www.acgusa.org/fellowships/kellen-fellowships/",
        "focus": "German-American relations",
    },
    {
        "name": "American Council on Germany – McCloy Fellowship",
        "url": "https://acgusa.org/fellowships/mccloy-fellowships/",
        "focus": "German-American relations",
    },
    {
        "name": "Arthur L. Carter Journalism Institute – Reporting Award",
        "url": "https://journalism.nyu.edu/about-us/awards-and-fellowships/the-reporting-award/",
        "focus": "General reporting",
    },
    {
        "name": "Atlantic Magazine Editorial Fellowship",
        "url": "https://www.theatlantic.com/press-releases/",
        "focus": "Investigative journalism, fact-checking",
    },
    {
        "name": "Ben Bagdikian Fellowship / Mother Jones",
        "url": "https://www.motherjones.com/careers/fellowships/",
        "focus": "Investigative/accountability journalism",
    },
    {
        "name": "Bertha Challenge / Bertha Foundation",
        "url": "https://berthafoundation.org/bertha-challenge/",
        "focus": "Investigative/long-form journalism",
    },
    {
        "name": "California Local News Fellowship",
        "url": "https://fellowships.journalism.berkeley.edu/cafellows/",
        "focus": "Local journalism",
    },
    {
        "name": "Carnegie Foundation – Andrew Carnegie Fellows Program",
        "url": "https://www.carnegie.org/news/articles/andrew-carnegie-fellows-program-info/",
        "focus": "General scholarship",
    },
    {
        "name": "Center for Health Journalism – National Fellowship",
        "url": "https://centerforhealthjournalism.org/fellowships-grants/national-fellowship",
        "focus": "Health inequities reporting",
    },
    {
        "name": "Complex Systems Summer School – Journalism Fellowship",
        "url": "https://www.santafe.edu/news-center/journalism-fellowship",
        "focus": "Complex systems science journalism",
    },
    {
        "name": "CUNY McGraw Business Journalism Fellowships",
        "url": "https://www.mcgrawcenter.org/the-harold-w-mcgraw-jr-business-journalism-fellowships/",
        "focus": "Business and economic reporting",
    },
    {
        "name": "Daniel Pearl Investigative Journalism Initiative",
        "url": "https://www.dpiji.org/",
        "focus": "Investigative journalism",
    },
    {
        "name": "Data-Driven Reporting Project",
        "url": "https://datadrivenreporting.medill.northwestern.edu/",
        "focus": "Data journalism projects",
    },
    {
        "name": "Economic Hardship Reporting Project",
        "url": "https://economichardship.org/pitch-portal/",
        "focus": "Poverty and inequality reporting",
    },
    {
        "name": "Education Writers Association Reporting Fellowship",
        "url": "https://ewa.org/fellowships",
        "focus": "Education reporting",
    },
    {
        "name": "Edward R. Murrow Press Fellowship",
        "url": "https://www.cfr.org/fellowships/edward-r-murrow-press-fellowship",
        "focus": "Global affairs, international reporting",
    },
    {
        "name": "Eugene C. Pulliam Fellowship for Public Service Journalism",
        "url": "https://www.spj.org/eugene-c-pulliam-fellowship-for-public-service-journalism/",
        "focus": "Public service journalism",
    },
    {
        "name": "European Cross-Border Grants – Journalismfund",
        "url": "https://grants.journalismfund.eu/en/european-cross-border-grants",
        "focus": "Migration, corruption investigations",
    },
    {
        "name": "FIRE Virtual Newsroom",
        "url": "https://firenewsroom.org/program/virtual-newsroom",
        "focus": "Investigative journalism",
    },
    {
        "name": "Ford Foundation – JustFilms",
        "url": "https://www.fordfoundation.org/work/our-grants/justfilms/",
        "focus": "Social justice, documentary films",
    },
    {
        "name": "Fulbright Scholar Program",
        "url": "https://fulbrightscholars.org/",
        "focus": "Global reporting",
    },
    {
        "name": "Fund for Investigative Journalism",
        "url": "https://fij.org/grantees-work/",
        "focus": "Investigative reporting",
    },
    {
        "name": "Pulitzer Center – Gender Equity Grants",
        "url": "https://pulitzercenter.org/grants-fellowships/opportunities-journalists/",
        "focus": "Gender equality and women's empowerment",
    },
    {
        "name": "Hearst Fellowship",
        "url": "https://hearstfellows.com/program-information",
        "focus": "General newsroom training",
    },
    {
        "name": "Ida B. Wells Society Investigative Reporting Fellowship",
        "url": "https://idabwellssociety.org/",
        "focus": "Investigative reporting",
    },
    {
        "name": "IJ4EU – Investigative Journalism for Europe",
        "url": "https://www.investigativejournalismforeu.net/grants/",
        "focus": "Cross-border EU investigations",
    },
    {
        "name": "Institute of Current World Affairs",
        "url": "https://www.icwa.org/apply/",
        "focus": "Global cultures and affairs",
    },
    {
        "name": "International Center for Journalists / Arthur F. Burns Fellowship",
        "url": "https://www.icfj.org/our-work/burns",
        "focus": "German-American journalism relations",
    },
    {
        "name": "Investigative Reporters & Editors – Freelance Fellowship",
        "url": "https://www.ire.org/training/fellowships-and-scholarships/freelance-fellowship/",
        "focus": "Investigative reporting",
    },
    {
        "name": "Ira A. Lipman Fellowship – Columbia Journalism School",
        "url": "https://journalism.columbia.edu/ira-lipman-fellowship",
        "focus": "Civil and human rights reporting",
    },
    {
        "name": "IWMF – Fund for Women Journalists",
        "url": "https://www.iwmf.org/programs/fund-for-women-journalists/",
        "focus": "Women-identifying journalists",
    },
    {
        "name": "John S. Knight Fellowships at Stanford",
        "url": "https://jsk.stanford.edu/become-a-fellow/",
        "focus": "Journalism innovation",
    },
    {
        "name": "Knight-Bagehot Fellowship – Columbia University",
        "url": "https://journalism.columbia.edu/knight-bagehot",
        "focus": "Business/economics reporting",
    },
    {
        "name": "Knight Science Journalism Fellowship – MIT",
        "url": "https://ksj.mit.edu/fellowships/academic-year-fellowship/",
        "focus": "Science and technology reporting",
    },
    {
        "name": "Knight-Wallace Fellowship – University of Michigan",
        "url": "https://wallacehouse.umich.edu/knight-wallace/",
        "focus": "General journalism advancement",
    },
    {
        "name": "Leonard C. Goodman Investigative Fellowship",
        "url": "https://inthesetimes.com/call-for-investigative-proposals",
        "focus": "Climate, labor, corporate influence",
    },
    {
        "name": "Lighthouse Reports Reporting Fellowship",
        "url": "https://www.lighthousereports.com/",
        "focus": "Investigative coalitions, impact strategy",
    },
    {
        "name": "Marquette University O'Brien Fellowship",
        "url": "https://www.marquette.edu/obrien-fellowship/application.php",
        "focus": "In-depth reporting projects",
    },
    {
        "name": "Matthew Power Literary Reporting Award – NYU",
        "url": "https://journalism.nyu.edu/about-us/awards-and-fellowships/matthew-power-literary-reporting-award/",
        "focus": "Literary journalism",
    },
    {
        "name": "Metcalf Ocean Nexus Academy (MONA) Fellowship",
        "url": "https://uprootproject.org/mona-fellowship/",
        "focus": "Ocean justice, systemic inequities",
    },
    {
        "name": "Money Trail Grant",
        "url": "https://www.money-trail.org/grants/",
        "focus": "Cross-border corruption investigations",
    },
    {
        "name": "New York Times Newsroom Fellowship",
        "url": "https://www.nytco.com/careers/early-career-opportunities/newsroom-fellowship/",
        "focus": "General newsroom positions",
    },
    {
        "name": "Nieman Foundation for Journalism at Harvard",
        "url": "https://nieman.harvard.edu/fellowships/",
        "focus": "General journalism advancement",
    },
    {
        "name": "NIHCM Foundation – Journalism Grants",
        "url": "https://nihcm.org/grants/journalism-grants",
        "focus": "Health reporting and education",
    },
    {
        "name": "Nova Institute for Health – Media Fellows",
        "url": "https://novainstituteforhealth.org/our-communities/media-fellows/",
        "focus": "Health and wellness reporting",
    },
    {
        "name": "Omidyar Reporter in Residence Program",
        "url": "https://omidyar.com/where-we-focus/reporters-in-residence-program/",
        "focus": "Technology and AI reporting",
    },
    {
        "name": "Open Notebook Early-Career Science Journalism Fellowship",
        "url": "https://www.theopennotebook.com/early-career-fellowship-program",
        "focus": "Science journalism mentorship",
    },
    {
        "name": "Open Society Foundations – Grants",
        "url": "https://www.opensocietyfoundations.org/grants",
        "focus": "Education, immigration, justice reform",
    },
    {
        "name": "Open Society / Soros Justice Fellowships",
        "url": "https://www.opensocietyfoundations.org/grants/soros-justice-fellowships",
        "focus": "Criminal justice reform, equity",
    },
    {
        "name": "Outrider AI + Nuclear Reporting Fund",
        "url": "https://outrider.org/projects/outrider-ai-nuclear-reporting-fund",
        "focus": "AI and nuclear weapons coverage",
    },
    {
        "name": "Pulitzer Center – Persephone Miel Fellowships",
        "url": "https://pulitzercenter.org/grants-fellowships/opportunities-journalists/persephone-miel-fellowships",
        "focus": "International reporting support, non-US/Western Europe journalists",
    },
    {
        "name": "ProPublica Fellowship",
        "url": "https://www.propublica.org/fellowships",
        "focus": "Investigative journalism",
    },
    {
        "name": "Pulitzer Center – Reporting Grants and Fellowships",
        "url": "https://pulitzercenter.org/opportunities/reporting-grants-fellowships",
        "focus": "Gender equity, climate, AI accountability, international reporting",
    },
    {
        "name": "Rest & Resilience Fellowship – taz Panter Stiftung",
        "url": "https://taz.de/taz-panter-stiftung/rest-resilience-fellowship/",
        "focus": "Press freedom restoration, journalists at risk",
    },
    {
        "name": "Reynolds Journalism Institute Fellowship",
        "url": "https://rjionline.org/about-rji-fellowships/",
        "focus": "Community-centered news innovation",
    },
    {
        "name": "Robert Novak Journalism Fellowship",
        "url": "https://tfas.org/programs/center-for-excellence-in-journalism/robert-novak-journalism-fellowship/",
        "focus": "Enterprise journalism projects",
    },
    {
        "name": "Sir Harry Evans Memorial Fund – Global Fellowship",
        "url": "https://www.durham.ac.uk/sir-harry-evans-memorial-fund/global-fellowship/",
        "focus": "International reporting",
    },
    {
        "name": "Solutions Journalism Network – Fellowships",
        "url": "https://www.solutionsjournalism.org/fellowships",
        "focus": "Solutions-focused reporting",
    },
    {
        "name": "Spencer Fellowship for Education Reporting",
        "url": "https://spencerfellows.org/about-the-fellowship/",
        "focus": "Long-form education journalism",
    },
    {
        "name": "Stigler Center Journalists in Residence – Chicago Booth",
        "url": "https://www.chicagobooth.edu/research/stigler/education/journalists-in-residence-program",
        "focus": "Business and economics reporting",
    },
    {
        "name": "Tarbell Fellowship – AI Reporting",
        "url": "https://www.tarbellcenter.org/fellowship",
        "focus": "Artificial intelligence reporting",
    },
    {
        "name": "Ted Scripps Fellowship in Environmental Journalism",
        "url": "https://www.colorado.edu/cej/scripps-fellowships/core-program",
        "focus": "Environmental journalism",
    },
    {
        "name": "Stringer Foundation Grants",
        "url": "https://stringerjournalism.org/apply-for-grants",
        "focus": "Broad creative media practices, public interest journalism",
    },
    {
        "name": "Type Investigations",
        "url": "https://www.typeinvestigations.org/",
        "focus": "Investigative journalism partnerships",
    },
    {
        "name": "Wilson Center Fellowship",
        "url": "https://www.wilsoncenter.org/fellowship-application-guidelines",
        "focus": "Strategic competition, tech, statecraft",
    },
    {
        "name": "World Press Institute Fellowship",
        "url": "https://worldpressinstitute.org/fellowships/",
        "focus": "US media landscape exploration for international journalists",
    },
    {
        "name": "Craig Newmark Philanthropies",
        "url": "https://craignewmarkphilanthropies.org/apply",
        "focus": "Journalism, press freedom, disinformation, cybersecurity for newsrooms",
    },
    {
        "name": "EU-LAC Social Accelerator (European Commission)",
        "url": "https://international-partnerships.ec.europa.eu/policies/programming/projects/social-accelerator_en",
        "focus": "Social innovation and civil society organizations in Latin America and the Caribbean",
    },
]
