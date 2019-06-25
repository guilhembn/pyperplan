def search_plan(task, search, heuristic):
    if heuristic:
        return search(task, heuristic)
    else:
        return search(task)