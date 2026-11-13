"""
Element Labs (Movenetics) Product Portfolio — extracted from official induction PDF.
Used for intelligent product matching based on client's industry/business type.
"""

PRODUCTS = [
    {
        "id": "spelcabs",
        "name": "SPELCABS",
        "category": "Mobile App",
        "industry_tags": ["transportation", "logistics", "ride hailing", "mobility", "taxi", "delivery", "courier", "freight", "fleet"],
        "short_desc": "Ride-hailing app with real-time fare bidding between passengers and drivers.",
        "features": ["User app", "Driver app", "City rides", "Intercity rides", "Freight & courier", "Wallet", "Admin panel", "Dark mode", "Multi-language"],
        "pitch": "A ready-to-deploy white-label ride-hailing solution with real-time fare bidding, intercity rides, and freight support — deployable in weeks."
    },
    {
        "id": "safetrip",
        "name": "SafeTrip",
        "category": "Mobile App",
        "industry_tags": ["transportation", "corporate commute", "travel", "bus", "shuttle", "employee transport", "logistics"],
        "short_desc": "Corporate commute app via budget-friendly and luxury buses with subscriptions.",
        "features": ["User app", "Driver app", "Bus operator app", "Subscription model", "Stripe integration", "Admin panel"],
        "pitch": "A corporate commute platform for employees — budget and luxury bus options with subscription plans, Stripe payments, and a full operator dashboard."
    },
    {
        "id": "talo",
        "name": "Talo",
        "category": "Mobile App / Web App",
        "industry_tags": ["real estate", "property", "rental", "housing", "mortgage", "land", "leasing", "tenant"],
        "short_desc": "Real estate app for listing rental/sale properties and connecting owners with buyers/tenants.",
        "features": ["Rental listing", "Land sell listing", "Mortgage calculator", "Chat feature", "Featured properties", "Admin panel"],
        "pitch": "A full-featured real estate platform where property owners can list rentals or land sales, buyers can search and chat directly, and an admin manages listings end-to-end."
    },
    {
        "id": "frush",
        "name": "Frush",
        "category": "Mobile App",
        "industry_tags": ["food", "restaurant", "delivery", "hospitality", "table booking", "catering", "food tech", "pos"],
        "short_desc": "Food delivery and restaurant discovery app with POS and table booking.",
        "features": ["User app", "Restaurant app", "POS system", "Table booking", "Search filters", "Subscription", "Employee roles", "Admin panel"],
        "pitch": "A complete white-label food delivery + restaurant OS — seamlessly connects diners to restaurants with order management, table booking, POS, and admin control from day one."
    },
    {
        "id": "kast_ott",
        "name": "Kast OTT",
        "category": "Web App / Mobile App",
        "industry_tags": ["entertainment", "streaming", "media", "video", "movies", "content", "ott", "subscription", "tv", "web series"],
        "short_desc": "Video streaming platform with movie/series library and personalized recommendations.",
        "features": ["User app", "Web app", "Top 10 charts", "Movie & series library", "Search & filters", "Subscription", "Admin panel"],
        "pitch": "A production-ready OTT streaming platform with personalized recommendations, subscription billing, and a full content admin panel — go live in weeks, not months."
    },
    {
        "id": "wowch",
        "name": "Wowch",
        "category": "Mobile App",
        "industry_tags": ["health", "wellness", "beauty", "home services", "on demand", "healthcare", "personal care", "fitness", "salon"],
        "short_desc": "On-demand home services app for healthcare, beauty, and personal care professionals.",
        "features": ["User app", "Provider app", "Slot scheduling", "Booking management", "Hire from friend list", "Location-based search", "Admin panel"],
        "pitch": "A ready-to-deploy on-demand home services marketplace — connect clients to vetted healthcare, beauty, and care professionals with smart scheduling and location search."
    },
    {
        "id": "bitqik",
        "name": "Bitqik",
        "category": "Web App / Blockchain",
        "industry_tags": ["crypto", "blockchain", "fintech", "exchange", "defi", "trading", "bitcoin", "ethereum", "cryptocurrency", "banking", "finance"],
        "short_desc": "Centralized crypto exchange supporting 20+ cryptocurrencies with banking integration.",
        "features": ["User app", "20+ crypto support", "Fireblocks integration", "Fiat integration", "Crypto wallet", "Admin panel"],
        "pitch": "A battle-tested centralized crypto exchange — 20+ coins, Fireblocks custody, fiat banking integration, and competitive 0.2% fees, ready to white-label for your market."
    },
    {
        "id": "cupchairs",
        "name": "Cupchairs NFT Marketplace",
        "category": "Blockchain / Web App",
        "industry_tags": ["nft", "blockchain", "art", "digital art", "web3", "collector", "token", "tezos", "marketplace", "creative"],
        "short_desc": "NFT marketplace on Tezos blockchain for digital art and creative works.",
        "features": ["Tezos blockchain", "Buy via crypto & fiat", "FA2 token standard", "NFT royalty", "Admin panel"],
        "pitch": "A sustainable, energy-efficient NFT marketplace built on Tezos — artists tokenize and sell digital works with royalty protections, buyers pay in crypto or fiat."
    },
    {
        "id": "cashverse",
        "name": "Cashverse (ICO Platform)",
        "category": "Blockchain / Web App",
        "industry_tags": ["crypto", "ico", "defi", "blockchain", "token launch", "bsc", "binance", "staking", "dex", "fintech", "web3"],
        "short_desc": "BSC-based DeFi ecosystem with token launches, staking, DEX swaps, and liquidity pools.",
        "features": ["Binance Smart Chain", "Token purchase", "Staking", "DEX swap", "Liquidity pools", "Admin panel", "Low fees (~$0.01-$0.10)"],
        "pitch": "A production-ready DeFi & ICO platform on BSC — host token launches, staking rewards, lottery mechanics, and DEX swaps with ultra-low transaction fees."
    },
    {
        "id": "moveglam_ai",
        "name": "MoveGlam.AI",
        "category": "AI Tool / Web App",
        "industry_tags": ["fashion", "clothing", "ecommerce", "retail", "ai", "photography", "model", "apparel", "boutique", "shopify"],
        "short_desc": "AI model generation tool — upload clothing images and generate AI models wearing them.",
        "features": ["AI model aesthetics", "Model pose modification", "Ethnicity & personality selection", "Open source model", "Upload cloth images"],
        "pitch": "Eliminate expensive photoshoots — upload your clothing inventory, choose model body type, pose, and ethnicity, and get professional AI-generated product photos instantly."
    },
    {
        "id": "ecommerce",
        "name": "E-Commerce Platform",
        "category": "Mobile App / Web App",
        "industry_tags": ["ecommerce", "retail", "shopping", "product", "marketplace", "vendor", "store", "online shop", "payment", "d2c"],
        "short_desc": "Full-featured e-commerce app with vendor portal, smart search, and secure payments.",
        "features": ["User app", "Vendor app", "Order tracking", "Smart search", "Secure payments", "Wishlist", "Deals & offers", "Admin panel"],
        "pitch": "A multi-vendor e-commerce platform ready to white-label — smart product discovery, real-time order tracking, vendor management, and secure payment integration built-in."
    },
    {
        "id": "ai_outreach",
        "name": "AI Lead Outreach Engine",
        "category": "Automation / AI",
        "industry_tags": ["sales", "marketing", "lead generation", "b2b", "agency", "crm", "outreach", "automation", "email", "cold email"],
        "short_desc": "Automated pipeline that finds potential clients and sends personalized cold emails.",
        "features": ["Target prospect research", "DeepSeek-powered personalization", "SMTP email dispatch", "Sent history log", "Multi-tone selection"],
        "pitch": "An AI-powered outreach engine that researches prospects, crafts personalized pitch emails matching their exact need, and sends them automatically — no manual work needed."
    },
    {
        "id": "web_analyzer",
        "name": "Website & UI/UX Audit Tool",
        "category": "Automation / AI",
        "industry_tags": ["agency", "marketing", "web design", "website", "digital", "audit", "ux", "startup", "saas"],
        "short_desc": "AI tool that audits any website for UI/UX flaws, recommends features, and drafts outreach.",
        "features": ["DeepSeek Vision analysis", "DOM structural checks", "Industry-matched product suggestions", "Multi-channel outreach drafts (msg + email)"],
        "pitch": "A smart website auditor that uses AI vision to find real UI/UX issues, matches the right products to the client's business, and auto-drafts personalized outreach — ready in seconds."
    }
]

SERVICES = [
    {
        "name": "Mobile App Development",
        "desc": "End-to-end native and cross-platform app creation — iOS and Android — with ready-to-deploy white-label bases for fast go-to-market."
    },
    {
        "name": "Web App Development",
        "desc": "Dynamic, responsive web applications built for scale — from SaaS dashboards to marketplace platforms."
    },
    {
        "name": "Blockchain Development",
        "desc": "Secure, innovative blockchain solutions — smart contracts, NFT marketplaces, DeFi platforms, token launches."
    },
    {
        "name": "AI & Automation",
        "desc": "Custom AI agents, automation pipelines, and intelligent workflows — lead generation, customer support bots, data processing."
    },
    {
        "name": "UI/UX Design",
        "desc": "Mobile app, web, Web3, and SaaS UI design — intuitive, conversion-optimized interfaces."
    },
    {
        "name": "Digital Marketing & Branding",
        "desc": "Social media marketing, digital campaigns, branding, and PR — full-funnel customer journey campaigns."
    }
]


def match_products(business_context: str, max_results: int = 3) -> list:
    """
    Returns the most relevant products for a given business context (domain/text).
    Simple keyword scoring — fast and deterministic.
    """
    context_lower = business_context.lower()
    scored = []

    for product in PRODUCTS:
        score = 0
        for tag in product["industry_tags"]:
            if tag in context_lower:
                score += 2
            elif any(word in context_lower for word in tag.split()):
                score += 1
        if score > 0:
            scored.append((score, product))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:max_results]]

