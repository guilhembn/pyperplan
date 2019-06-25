import random

from task import Task, Operator


def tau_inv(meta_facts):
    concerned_facts = set([mf.split('-')[-1] for mf in meta_facts])
    return concerned_facts


class PrioQueue:
    def __init__(self, search, heuristic, p_r):
        self._l = []  # type: list[tuple[float, tuple[Task, list]]]
        self.search = search
        self.heuristic = heuristic
        self.p_r = p_r # type: list[Operator] # Optimal plan being explained

    def push(self, item, cost):
        self._l.append((cost, item))

    def pop(self, task: Task):
        min_cost = min(self._l, key=lambda x: x[0])
        candidates = [x for x in self._l if x[0] == min_cost[0]]
        pruned_list = []
        if self.heuristic:
            p_h = self.search(task, self.heuristic)  # type: list[Operator]
        else:
            p_h = self.search(task)  # type: list[Operator]
        if p_h is None:
            p_h = []

        for x in candidates:
            gamma_m = task.get_gamma()
            gamma_diff = x[1][0].get_gamma() ^ gamma_m
            t_1_diff = tau_inv(gamma_diff)
            found = False
            for a in set(p_h) | set(self.p_r):
                for f in t_1_diff:
                    if f in a.preconditions or f in a.add_effects or f in a.del_effects:
                        found = True
                        pruned_list.append(x)
                        break
                if found:
                    break

        if len(pruned_list) == 0:
            c, m = random.choice(candidates)
            self._l.remove((c, m))
            return m, c
        else:
            c, m = random.choice(pruned_list)
            self._l.remove((c, m))
            return m, c

    def __len__(self):
        return len(self._l)