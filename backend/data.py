"""Data module with traits, diverse question types, and career vectors."""

traits = [
    "analytical",
    "creativity",
    "social",
    "risk",
    "discipline"
]

questions = [

# =========================
# 🔷 PHASE 1 (Broad / Akinator-style)
# =========================

{
    "id": "Q1",
    "type": "mcq",
    "text": "What excites you the most?",
    "options": [
        "Solving complex problems",
        "Creating something new",
        "Interacting with people", 
        "Taking bold decisions"
    ],
    "weights": [
        {"analytical": 0.9},
        {"creativity": 0.9},
        {"social": 0.9},
        {"risk": 0.9}
    ]
},

{
    "id": "Q2",
    "type": "mcq",
    "text": "In a team, what role do you naturally take?",
    "options": [
        "Problem solver",
        "Idea generator",
        "Coordinator/communicator",
        "Decision maker"
    ],
    "weights": [
        {"analytical": 0.8},
        {"creativity": 0.8},
        {"social": 0.8},
        {"risk": 0.7}
    ]
},

{
    "id": "Q3",
    "type": "binary",
    "text": "Do you enjoy uncertainty and unpredictable outcomes?",
    "weights": {
        "yes": {"risk": 0.9},
        "no": {"discipline": 0.6}
    }
},

{
    "id": "Q4",
    "type": "binary",
    "text": "Do you prefer working alone over group work?",
    "weights": {
        "yes": {"analytical": 0.6},
        "no": {"social": 0.8}
    }
},

# =========================
# 🔷 PHASE 2 (Trait-specific)
# =========================

{"id": "Q5", "type": "scale", "text": "I enjoy analyzing patterns in data", "trait": "analytical"},
{"id": "Q6", "type": "scale", "text": "I break problems into smaller logical steps", "trait": "analytical"},

{"id": "Q7", "type": "scale", "text": "I enjoy experimenting with new ideas", "trait": "creativity"},
{"id": "Q8", "type": "scale", "text": "I get bored with repetitive tasks", "trait": "creativity"},

{"id": "Q9", "type": "scale", "text": "I enjoy networking and meeting new people", "trait": "social"},
{"id": "Q10", "type": "scale", "text": "I feel confident speaking in front of others", "trait": "social"},

{"id": "Q11", "type": "scale", "text": "I take decisions even when outcomes are unclear", "trait": "risk"},
{"id": "Q12", "type": "scale", "text": "I like taking initiative without instructions", "trait": "risk"},

{"id": "Q13", "type": "scale", "text": "I stick to routines and schedules", "trait": "discipline"},
{"id": "Q14", "type": "scale", "text": "I complete tasks even when I don’t feel motivated", "trait": "discipline"},

# =========================
# 🔷 PHASE 3 (Cross-trait)
# =========================

{
    "id": "Q15",
    "type": "mcq",
    "text": "You have a new idea. What do you do first?",
    "options": [
        "Analyze feasibility",
        "Build a prototype",
        "Discuss with people",
        "Take a risk and launch"
    ],
    "weights": [
        {"analytical": 0.8, "discipline": 0.6},
        {"creativity": 0.9},
        {"social": 0.8},
        {"risk": 0.9}
    ]
},

{
    "id": "Q16",
    "type": "mcq",
    "text": "Which activity sounds most satisfying?",
    "options": [
        "Solving a difficult puzzle",
        "Designing something unique",
        "Convincing someone",
        "Launching something risky"
    ],
    "weights": [
        {"analytical": 0.9},
        {"creativity": 0.9},
        {"social": 0.9},
        {"risk": 0.9}
    ]
},

{
    "id": "Q17",
    "type": "binary",
    "text": "Do you prefer planning over spontaneous action?",
    "weights": {
        "yes": {"discipline": 0.9},
        "no": {"risk": 0.7}
    }
},

{
    "id": "Q18",
    "type": "binary",
    "text": "Do you enjoy influencing people's decisions?",
    "weights": {
        "yes": {"social": 0.9},
        "no": {"analytical": 0.5}
    }
},

# =========================
# 🔷 PHASE 4 (Refinement)
# =========================

{"id": "Q19", "type": "scale", "text": "I enjoy optimizing systems and processes", "trait": "analytical"},
{"id": "Q20", "type": "scale", "text": "I think of unconventional solutions", "trait": "creativity"},
{"id": "Q21", "type": "scale", "text": "I build strong relationships easily", "trait": "social"},
{"id": "Q22", "type": "scale", "text": "I take calculated risks", "trait": "risk"},
{"id": "Q23", "type": "scale", "text": "I follow through on long-term goals", "trait": "discipline"},

{
    "id": "Q24",
    "type": "mcq",
    "text": "What would you rather do on a free day?",
    "options": [
        "Learn a new analytical skill",
        "Work on a creative project",
        "Meet people or attend events",
        "Try something risky or new"
    ],
    "weights": [
        {"analytical": 0.8},
        {"creativity": 0.8},
        {"social": 0.8},
        {"risk": 0.8}
    ]
},

{
    "id": "Q25",
    "type": "binary",
    "text": "Do you enjoy leading teams?",
    "weights": {
        "yes": {"social": 0.8, "risk": 0.6},
        "no": {"analytical": 0.5}
    }
},

{
    "id": "Q26",
    "type": "binary",
    "text": "Do you prefer structured environments?",
    "weights": {
        "yes": {"discipline": 0.9},
        "no": {"creativity": 0.6}
    }
},

{"id": "Q27", "type": "scale", "text": "I enjoy working with numbers and data", "trait": "analytical"},
{"id": "Q28", "type": "scale", "text": "I enjoy storytelling and design", "trait": "creativity"},
{"id": "Q29", "type": "scale", "text": "I enjoy persuading people", "trait": "social"},
{"id": "Q30", "type": "scale", "text": "I am comfortable failing and trying again", "trait": "risk"}

]

career_questions = [
    {
        "id": "C1",
        "type": "mcq",
        "text": "When a project gets stuck, what do you usually do first?",
        "options": [
            "Break the problem into parts, check what the data says, and prioritize fixes",
            "Talk to stakeholders, align expectations, and reset the plan",
            "Prototype a quick workaround and improve it through feedback",
            "Push for immediate execution, monitor outcomes, and adjust on the move",
        ],
        "career_weights": [
            {
                "Data Analyst": 0.82,
                "Business Analyst": 0.78,
                "Financial Analyst": 0.74,
                "Operations Manager": 0.66,
            },
            {
                "Product Manager": 0.82,
                "Management Consultant": 0.78,
                "HR Manager": 0.68,
                "Sales Manager": 0.62,
            },
            {
                "Software Developer": 0.80,
                "UI/UX Designer": 0.76,
                "Entrepreneur": 0.67,
                "Product Manager": 0.61,
            },
            {
                "Entrepreneur": 0.84,
                "Sales Manager": 0.72,
                "Marketing Manager": 0.68,
                "Operations Manager": 0.60,
            },
        ],
    },
    {
        "id": "C2",
        "type": "mcq",
        "text": "At the end of a strong work week, what feels most satisfying?",
        "options": [
            "Finding a hidden pattern that changed a key decision",
            "Shipping something useful that people actually use",
            "Seeing teams collaborate smoothly and hit shared goals",
            "Turning a vague idea into visible market traction",
        ],
        "career_weights": [
            {
                "Data Analyst": 0.84,
                "Financial Analyst": 0.79,
                "Business Analyst": 0.74,
                "Management Consultant": 0.58,
            },
            {
                "Software Developer": 0.82,
                "Product Manager": 0.74,
                "UI/UX Designer": 0.68,
                "Entrepreneur": 0.62,
            },
            {
                "HR Manager": 0.80,
                "Operations Manager": 0.76,
                "Product Manager": 0.70,
                "Management Consultant": 0.66,
            },
            {
                "Marketing Manager": 0.82,
                "Sales Manager": 0.78,
                "Entrepreneur": 0.76,
                "Product Manager": 0.60,
            },
        ],
    },
    {
        "id": "C3",
        "type": "mcq",
        "text": "You are joining a new initiative with limited clarity. Which role do you naturally take?",
        "options": [
            "Build the decision framework and define success metrics",
            "Shape user journeys and improve the overall experience",
            "Coordinate people, priorities, and delivery milestones",
            "Drive external conversations to create buy-in and momentum",
        ],
        "career_weights": [
            {
                "Business Analyst": 0.82,
                "Data Analyst": 0.76,
                "Management Consultant": 0.72,
                "Financial Analyst": 0.66,
            },
            {
                "UI/UX Designer": 0.84,
                "Product Manager": 0.70,
                "Marketing Manager": 0.62,
                "Software Developer": 0.57,
            },
            {
                "Product Manager": 0.84,
                "Operations Manager": 0.78,
                "HR Manager": 0.64,
                "Management Consultant": 0.62,
            },
            {
                "Sales Manager": 0.82,
                "Marketing Manager": 0.76,
                "Entrepreneur": 0.70,
                "Management Consultant": 0.58,
            },
        ],
    },
    {
        "id": "C4",
        "type": "mcq",
        "text": "Which work setting helps you perform at your best?",
        "options": [
            "Clear structure, measurable targets, and predictable processes",
            "Fast iterations, changing priorities, and visible product impact",
            "Open-ended briefs where creativity and storytelling matter",
            "High-energy interactions where persuasion and relationships drive outcomes",
        ],
        "career_weights": [
            {
                "Financial Analyst": 0.83,
                "Operations Manager": 0.78,
                "Data Analyst": 0.72,
                "Business Analyst": 0.66,
            },
            {
                "Product Manager": 0.82,
                "Software Developer": 0.75,
                "Entrepreneur": 0.72,
                "Management Consultant": 0.58,
            },
            {
                "UI/UX Designer": 0.84,
                "Marketing Manager": 0.74,
                "Entrepreneur": 0.64,
                "Product Manager": 0.58,
            },
            {
                "Sales Manager": 0.83,
                "HR Manager": 0.74,
                "Marketing Manager": 0.70,
                "Management Consultant": 0.62,
            },
        ],
    },
    {
        "id": "C5",
        "type": "mcq",
        "text": "A business metric is declining for three months. What is your first move?",
        "options": [
            "Audit the numbers, isolate drivers, and quantify the biggest levers",
            "Interview users/customers to understand friction and unmet needs",
            "Redesign the operating workflow to reduce delays and failures",
            "Rework positioning and go-to-market messaging for faster response",
        ],
        "career_weights": [
            {
                "Financial Analyst": 0.84,
                "Data Analyst": 0.80,
                "Business Analyst": 0.74,
                "Management Consultant": 0.64,
            },
            {
                "Product Manager": 0.80,
                "UI/UX Designer": 0.74,
                "Marketing Manager": 0.64,
                "HR Manager": 0.56,
            },
            {
                "Operations Manager": 0.84,
                "Business Analyst": 0.72,
                "Management Consultant": 0.70,
                "Product Manager": 0.58,
            },
            {
                "Marketing Manager": 0.84,
                "Sales Manager": 0.80,
                "Entrepreneur": 0.70,
                "Product Manager": 0.56,
            },
        ],
    },
    {
        "id": "C6",
        "type": "mcq",
        "text": "What would you choose right now?",
        "options": [
            "A stable, structured role with clear progression",
            "A creative, flexible role where you shape experiences",
            "A high-risk, high-reward role with ownership and uncertainty",
            "A people-facing, dynamic role driven by communication and influence",
        ],
        "career_weights": [
            {
                "Financial Analyst": 0.82,
                "Operations Manager": 0.76,
                "Data Analyst": 0.72,
                "Business Analyst": 0.68,
            },
            {
                "UI/UX Designer": 0.84,
                "Marketing Manager": 0.72,
                "Product Manager": 0.64,
                "Software Developer": 0.56,
            },
            {
                "Entrepreneur": 0.85,
                "Sales Manager": 0.70,
                "Product Manager": 0.68,
                "Management Consultant": 0.60,
            },
            {
                "HR Manager": 0.80,
                "Sales Manager": 0.78,
                "Marketing Manager": 0.70,
                "Management Consultant": 0.64,
            },
        ],
    },
    {
        "id": "C7",
        "type": "mcq",
        "text": "You can only optimize one thing in your next role. What do you pick?",
        "options": [
            "Depth of analysis and decision quality",
            "Speed of execution and shipping outcomes",
            "Team alignment, culture, and collaboration",
            "Market growth, influence, and external impact",
        ],
        "career_weights": [
            {
                "Data Analyst": 0.82,
                "Financial Analyst": 0.80,
                "Business Analyst": 0.74,
                "Management Consultant": 0.62,
            },
            {
                "Software Developer": 0.80,
                "Operations Manager": 0.74,
                "Entrepreneur": 0.72,
                "Product Manager": 0.66,
            },
            {
                "HR Manager": 0.82,
                "Product Manager": 0.74,
                "Operations Manager": 0.68,
                "Management Consultant": 0.64,
            },
            {
                "Marketing Manager": 0.82,
                "Sales Manager": 0.80,
                "Entrepreneur": 0.72,
                "Product Manager": 0.58,
            },
        ],
    },
]

# =========================
# 🎯 CAREERS (High Separation)
# =========================

careers = [
    {"role": "Data Analyst", "vector": [10, 3, 3, 2, 9]},
    {"role": "Software Developer", "vector": [9, 4, 2, 3, 9]},
    {"role": "Product Manager", "vector": [7, 7, 9, 6, 8]},
    {"role": "UI/UX Designer", "vector": [4, 10, 6, 4, 5]},
    {"role": "Marketing Manager", "vector": [5, 8, 10, 7, 6]},
    {"role": "Management Consultant", "vector": [9, 6, 9, 7, 9]},
    {"role": "Entrepreneur", "vector": [6, 9, 7, 10, 5]},
    {"role": "Financial Analyst", "vector": [10, 3, 4, 2, 10]},
    {"role": "HR Manager", "vector": [4, 5, 10, 3, 8]},
    {"role": "Business Analyst", "vector": [9, 5, 7, 4, 9]},
    {"role": "Sales Manager", "vector": [4, 6, 10, 8, 6]},
    {"role": "Operations Manager", "vector": [7, 4, 6, 3, 10]}
]


# =========================
# 🔒 VALIDATION
# =========================

def _validate_data() -> None:
    trait_set = set(traits)
    career_roles = {career["role"] for career in careers}

    if len(traits) != len(trait_set):
        raise ValueError("Duplicate trait names found.")

    ids = set()
    for q in questions:
        if q["id"] in ids:
            raise ValueError(f"Duplicate question id: {q['id']}")
        ids.add(q["id"])

        if q["type"] == "scale":
            if q.get("trait") not in trait_set:
                raise ValueError(f"{q['id']} has invalid trait")

        if q["type"] == "mcq":
            if len(q["options"]) != len(q["weights"]):
                raise ValueError(f"{q['id']} options mismatch weights")

        if q["type"] == "binary":
            if "yes" not in q["weights"] or "no" not in q["weights"]:
                raise ValueError(f"{q['id']} must have yes/no weights")

    for cq in career_questions:
        if cq["id"] in ids:
            raise ValueError(f"Duplicate question id: {cq['id']}")
        ids.add(cq["id"])

        if cq.get("type") != "mcq":
            raise ValueError(f"{cq['id']} career question must be mcq")
        if len(cq.get("options", [])) != len(cq.get("career_weights", [])):
            raise ValueError(f"{cq['id']} options mismatch career_weights")

        for option_weights in cq.get("career_weights", []):
            if not isinstance(option_weights, dict) or not option_weights:
                raise ValueError(f"{cq['id']} has invalid career weight map")
            for role, weight in option_weights.items():
                if role not in career_roles:
                    raise ValueError(f"{cq['id']} references unknown career '{role}'")
                if not (0 <= weight <= 1):
                    raise ValueError(f"{cq['id']} has invalid career weight {weight} for '{role}'")

    if len(questions) < 25:
        raise ValueError("Minimum 25 questions required")

    for c in careers:
        if len(c["vector"]) != len(traits):
            raise ValueError(f"{c['role']} vector mismatch")
        for v in c["vector"]:
            if not (1 <= v <= 10):
                raise ValueError(f"{c['role']} has invalid value {v}")


_validate_data()
