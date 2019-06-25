from itertools import chain, combinations

from task import Task, Operator
from .prio_queue import PrioQueue
from .utils import search_plan


def is_plan_applicable(plan, model):
    assert plan is not None
    s = model.initial_state
    for a in plan:
        if a.applicable(s):
            s = a.apply(s)
        else:
            return False
    return True

def subsets(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def mme_search(search, heuristic, explained_plan, m_r: Task, m_h: Task):
    eps_mme = []
    fringe = PrioQueue(search, heuristic, explained_plan)
    c_list = []
    h_list = []
    fringe.push((m_r, []), 0)
    m_hat = m_h
    while len(fringe) != 0:
        x, c = fringe.pop(m_hat)
        m_hat, eps = x
        m_hat_optimal = search_plan(m_hat, search, heuristic)
        if m_hat_optimal is None or not is_plan_applicable(explained_plan, m_hat) or len(explained_plan) > len(m_hat_optimal):
            h_list.append(m_hat.get_gamma() ^ m_r.get_gamma())
        else:
            c_list.append(m_hat.get_gamma())
            for f in m_hat.get_gamma() - m_h.get_gamma():
                lamb = Operator("del-{}".format(f), m_hat.get_gamma(), {}, {f})
                new_gamma = lamb.apply(m_hat.get_gamma())
                if new_gamma not in c_list:
                    sym_diff = m_hat.get_gamma() ^ m_r.get_gamma()
                    prop3_violated = False
                    for s in subsets(sym_diff):
                        if s in h_list:
                            prop3_violated = True
                            break
                    if not prop3_violated:
                        fringe.push((Task.from_gamma(new_gamma), eps + [lamb]), c + 1)
                        if len(eps) > len(eps_mme):
                            eps_mme = eps

            for f in m_h.get_gamma() - m_hat.get_gamma():
                lamb = Operator("add-{}".format(f), m_hat.get_gamma(), {f}, {})
                new_gamma = lamb.apply(m_hat.get_gamma())
                if new_gamma not in c_list:
                    sym_diff = m_hat.get_gamma() ^ m_r.get_gamma()
                    prop3_violated = False
                    for s in subsets(sym_diff):
                        if s in h_list:
                            prop3_violated = True
                            break
                    if not prop3_violated:
                        fringe.push((Task.from_gamma(new_gamma), eps + [lamb]), c + 1)
                        if len(eps) > len(eps_mme):
                            eps_mme = eps

    print(m_hat.get_gamma() ^ m_r.get_gamma())
    return explained_plan, eps_mme

