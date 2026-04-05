"""Data module with fixed traits, questions, and careers."""

traits = [
    "analytical",
    "creativity",
    "social",
    "risk",
    "discipline"
]

questions = [
  {"id":"Q1","text":"I enjoy solving complex logical problems","trait":"analytical","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.7,"5":0.9}},
  {"id":"Q2","text":"I prefer data-driven decisions over intuition","trait":"analytical","likelihood":{"1":0.2,"2":0.4,"3":0.5,"4":0.7,"5":0.9}},
  {"id":"Q3","text":"I enjoy analyzing patterns in data","trait":"analytical","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.8,"5":0.9}},
  {"id":"Q4","text":"I like breaking complex problems into steps","trait":"analytical","likelihood":{"1":0.2,"2":0.4,"3":0.5,"4":0.7,"5":0.85}},

  {"id":"Q5","text":"I enjoy coming up with new ideas","trait":"creativity","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.8,"5":0.9}},
  {"id":"Q6","text":"I get bored doing repetitive tasks","trait":"creativity","likelihood":{"1":0.2,"2":0.3,"3":0.5,"4":0.7,"5":0.9}},
  {"id":"Q7","text":"I prefer designing over following instructions","trait":"creativity","likelihood":{"1":0.2,"2":0.4,"3":0.5,"4":0.8,"5":0.9}},
  {"id":"Q8","text":"I think of multiple solutions to problems","trait":"creativity","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.7,"5":0.85}},

  {"id":"Q9","text":"I enjoy interacting with new people","trait":"social","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.8,"5":0.9}},
  {"id":"Q10","text":"I prefer teamwork over working alone","trait":"social","likelihood":{"1":0.2,"2":0.4,"3":0.5,"4":0.7,"5":0.9}},
  {"id":"Q11","text":"I feel comfortable speaking in public","trait":"social","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.7,"5":0.85}},
  {"id":"Q12","text":"I enjoy influencing or persuading others","trait":"social","likelihood":{"1":0.2,"2":0.3,"3":0.5,"4":0.7,"5":0.9}},

  {"id":"Q13","text":"I am comfortable taking decisions under uncertainty","trait":"risk","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.8,"5":0.9}},
  {"id":"Q14","text":"I prefer experimenting over safe choices","trait":"risk","likelihood":{"1":0.2,"2":0.3,"3":0.5,"4":0.7,"5":0.9}},
  {"id":"Q15","text":"I enjoy taking risks even if I might fail","trait":"risk","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.8,"5":0.9}},
  {"id":"Q16","text":"I take initiative without waiting","trait":"risk","likelihood":{"1":0.2,"2":0.4,"3":0.5,"4":0.7,"5":0.85}},

  {"id":"Q17","text":"I follow a structured routine","trait":"discipline","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.7,"5":0.9}},
  {"id":"Q18","text":"I complete tasks even without motivation","trait":"discipline","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.8,"5":0.9}},
  {"id":"Q19","text":"I prefer planning before execution","trait":"discipline","likelihood":{"1":0.2,"2":0.4,"3":0.5,"4":0.7,"5":0.85}},
  {"id":"Q20","text":"I am consistent with long-term goals","trait":"discipline","likelihood":{"1":0.1,"2":0.3,"3":0.5,"4":0.8,"5":0.9}}
]

careers = [
 {"role":"Data Analyst","vector":[9,4,3,3,8]},
 {"role":"Product Manager","vector":[7,7,9,6,7]},
 {"role":"Software Developer","vector":[8,5,3,4,8]},
 {"role":"UI/UX Designer","vector":[5,9,6,5,6]},
 {"role":"Marketing Manager","vector":[6,8,9,7,6]},
 {"role":"Management Consultant","vector":[9,6,8,7,9]},
 {"role":"Entrepreneur","vector":[7,8,7,10,6]},
 {"role":"Financial Analyst","vector":[9,4,4,3,9]},
 {"role":"HR Manager","vector":[5,6,10,4,7]},
 {"role":"Business Analyst","vector":[8,5,7,5,8]}
]


def _validate_data() -> None:
    """Fail fast if fixed datasets are edited into an invalid shape."""
    trait_set = set(traits)
    expected_answers = {"1", "2", "3", "4", "5"}

    if len(traits) != len(trait_set):
        raise ValueError("Duplicate trait names found in 'traits'.")

    question_ids = set()
    for question in questions:
        question_id = question["id"]
        if question_id in question_ids:
            raise ValueError(f"Duplicate question id found: {question_id}")
        question_ids.add(question_id)

        if question["trait"] not in trait_set:
            raise ValueError(f"Question {question_id} references unknown trait '{question['trait']}'.")

        likelihood = question["likelihood"]
        if set(likelihood.keys()) != expected_answers:
            raise ValueError(f"Question {question_id} likelihood keys must be exactly 1..5.")
        for answer_key, answer_likelihood in likelihood.items():
            if not (0.0 <= answer_likelihood <= 1.0):
                raise ValueError(
                    f"Question {question_id} likelihood for answer {answer_key} "
                    f"is out of [0,1]: {answer_likelihood}"
                )

    if len(questions) < 10:
        raise ValueError("Question bank must include at least 10 items for stopping-rule compatibility.")

    for career in careers:
        if len(career["vector"]) != len(traits):
            raise ValueError(
                f"Career '{career['role']}' vector length {len(career['vector'])} "
                f"does not match number of traits {len(traits)}."
            )
        for value in career["vector"]:
            if not (1 <= value <= 10):
                raise ValueError(
                    f"Career '{career['role']}' has out-of-range vector value {value}; expected 1..10."
                )


_validate_data()
