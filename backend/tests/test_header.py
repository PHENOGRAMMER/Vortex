from backend.services.heading_detector import HeadingDetector

tests = [

    "Planning Agent",

    "Agent Responsibilities",

    "III. Methodology",

    "4. Results",

    "Conclusion",

    "This is a normal sentence.",

    "The planner analyses the query."
]

for t in tests:
    print(
        t,
        "->",
        HeadingDetector.is_heading(t)
    )