def recommend(history: list[str], courses: list[dict]) -> list[dict]:
    completed = set(history)
    available = (course for course in courses if course['nome'] not in completed)
    return sorted(available, key=lambda course: course['id'])[:3]
