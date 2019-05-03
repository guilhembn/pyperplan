from .prio_queue import PrioQueue
from task import Task, Operator


def search_plan(task, search, heuristic):
    if heuristic:
        return search(task, heuristic)
    else:
        return search(task)


def is_plan_optimal(explained_plan, m: Task, optimal_plan_in_m):
    # TODO: Check for optimality (here we just check for feasability)
    assert explained_plan is not None
    s = m.initial_state
    for a in explained_plan:
        if a.applicable(s):
            s = a.apply(s)
        else:
            return False
    return m.goal_reached(s) and optimal_plan_in_m is not None and len(explained_plan) == len(optimal_plan_in_m)


def mce_search(search, heuristic, explained_plan, m_r: Task, m_h: Task):
    c_list = []  # Closed list
    p_r = explained_plan
    fringe = PrioQueue(search, heuristic, explained_plan)
    fringe.push((m_h, []), 0)
    m_hat = m_h
    i = 0
    print(m_r)
    while True:
        print(i)
        i += 1
        print("Popping")
        x, c = fringe.pop(m_hat)
        m_hat, eps = x
        print("Checking plan optimality")
        p_h = search_plan(m_hat, search, heuristic)
        if is_plan_optimal(p_r, m_hat, p_h):
            return p_r, eps
        else:
            c_list.append(m_hat.get_gamma())
            for f in m_hat.get_gamma() - m_r.get_gamma():
                print("Fact to be removed:", f)
                lamb = Operator("del-{}".format(f), m_hat.get_gamma(), {}, {f})
                new_gamma = lamb.apply(m_hat.get_gamma())
                if new_gamma not in c_list:
                    fringe.push((Task.from_gamma(new_gamma), eps + [lamb]), c+1)
                else:
                    print("In c_list !")

            print("Robot gamma:", m_r.get_gamma(), "\nExplored gamma: ", m_hat.get_gamma(), "\nG(Mr) \\ G(Mh):", m_r.get_gamma() - m_hat.get_gamma())
            for f in m_r.get_gamma() - m_hat.get_gamma():
                print("fact to be added: ", f)
                lamb = Operator("add-{}".format(f), m_hat.get_gamma(), {f}, {})
                new_gamma = lamb.apply(m_hat.get_gamma())
                if new_gamma not in c_list:
                    fringe.push((Task.from_gamma(new_gamma), eps + [lamb]), c+1)
                    print(Task.from_gamma(new_gamma))
                else:
                    print("In c_list !")





