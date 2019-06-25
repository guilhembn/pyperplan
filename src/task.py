#
# This file is part of pyperplan.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
import re

"""
Classes for representing a STRIPS planning task
"""


class Operator:
    """
    The preconditions represent the facts that have to be true
    before the operator can be applied.
    add_effects are the facts that the operator makes true.
    delete_effects are the facts that the operator makes false.
    """
    def __init__(self, name, preconditions, add_effects, del_effects, possible_preconditions, possible_add,
                 possible_del=[]):
        self.name = name
        self.preconditions = frozenset(preconditions)
        self.add_effects = frozenset(add_effects)
        self.del_effects = frozenset(del_effects)
        self.possible_preconditions = frozenset(possible_preconditions)
        self.possible_add = frozenset(possible_add)
        self.possible_del = frozenset(possible_del)

    def applicable(self, state):
        """
        Operators are applicable when their set of preconditions is a subset
        of the facts that are true in "state".

        @return True if the operator's preconditions is a subset of the state,
                False otherwise
        """
        return self.preconditions <= state

    def apply(self, state):
        """
        Applying an operator means removing the facts that are made false
        by the operator from the set of true facts in state and adding
        the facts made true.

        Note that therefore it is possible to have operands that make a
        fact both false and true. This results in the fact being true
        at the end.

        @param state The state that the operator should be applied to
        @return A new state (set of facts) after the application of the
                operator
        """
        assert self.applicable(state)
        assert type(state) in (frozenset, set)
        return (state - self.del_effects) | self.add_effects

    def __str__(self):
        s = '%s\n' % self.name
        for group, facts in [('PRE', self.preconditions),
                             ('ADD', self.add_effects),
                             ('DEL', self.del_effects),
                             ('PRE~', self.possible_preconditions),
                             ('ADD~', self.possible_add),
                             ('DEL~', self.possible_del)]:
            for fact in facts:
                s += '  %s: %s\n' % (group, fact)
        return s

    def __repr__(self):
        return '<Op %s>' % self.name


class Task:
    """
    A STRIPS planning task
    """
    DEFAULT_NAME = 0

    def __init__(self, name, facts, initial_state, goals, operators):
        """
        @param name The task's name
        @param facts A set of all the fact names that are valid in the domain
        @param initial_state A set of fact names that are true at the beginning
        @param goals A set of fact names that must be true to solve the problem
        @param operators A set of operator instances for the domain
        """
        self.name = name
        self.facts = facts
        self.initial_state = initial_state
        self.goals = goals
        self.operators = operators

    def goal_reached(self, state):
        """
        The goal has been reached if all facts that are true in "goals"
        are true in "state".

        @return True if all the goals are reached, False otherwise
        """
        return self.goals <= state

    def get_successor_states(self, state):
        """
        @return A list with (op, new_state) pairs where "op" is the applicable
        operator and "new_state" the state that results when "op" is applied
        in state "state".
        """
        return [(op, op.apply(state)) for op in self.operators
                if op.applicable(state)]

    def __str__(self):
        s = 'Task {0}\n  Vars:  {1}\n  Init:  {2}\n  Goals: {3}\n  Ops:   {4}'
        return s.format(self.name, ', '.join(self.facts),
                             self.initial_state, self.goals,
                             '\n'.join(map(str, self.operators)))

    def __repr__(self):
        string = '<Task {0}, vars: {1}, operators: {2}>'
        return string.format(self.name, len(self.facts), len(self.operators))

    def get_meta_task(self, other):
        facts = set()
        for f in self.facts | other.facts:
            facts.add("init-has-{}".format(f))
            facts.add("goal-has-{}".format(f))
            for a in self.operators + other.operators:
                facts.add("{}-has-precondition-{}".format(a.name, f))
                facts.add("{}-has-add-effect-{}".format(a.name, f))
                facts.add("{}-has-del-effect-{}".format(a.name, f))
        init_state = self.get_gamma()
        goal_state = other.get_gamma()
        return Task("meta-{}-to-{}".format(self.name, other.name), facts, init_state, goal_state, frozenset())

    def get_gamma(self):
        gamma = set()
        used_facts = self.initial_state | self.goals
        for a in self.operators:
            used_facts |= a.preconditions | a.add_effects | a.del_effects
        for f in used_facts:
            gamma = gamma | self.tau(f)
        return frozenset(gamma)

    def tau(self, fact):
        s = set()
        if fact in self.initial_state:
            s.add("init-has-{}".format(fact))
        if fact in self.goals:
            s.add("goal-has-{}".format(fact))
        for a in self.operators:
            if fact in a.preconditions:
                s.add("{}-has-precondition-{}".format(a.name, fact))
            if fact in a.add_effects:
                s.add("{}-has-add-effect-{}".format(a.name, fact))
            if fact in a.del_effects:
                s.add("{}-has-del-effect-{}".format(a.name, fact))
        return frozenset(s)

    @staticmethod
    def from_gamma(meta_facts):
        facts = set()
        initial_state = set()
        goal_state = set()
        operators = {} # name: ({preconds}, {add_effects}, {del_effects]})
        for f in meta_facts:
            init = re.search("init-has-(.*)", f)
            if init:
                facts.add(init.group(1))
                initial_state.add(init.group(1))
                continue
            goal = re.search("goal-has-(.*)", f)
            if goal:
                facts.add(goal.group(1))
                goal_state.add(goal.group(1))
                continue
            precond = re.search("(.*)-has-precondition-(.*)", f)
            if precond:
                facts.add(precond.group(2))
                if precond.group(1) not in operators:
                    operators[precond.group(1)] = (set(), set(), set())
                operators[precond.group(1)][0].add(precond.group(2))
                continue
            add_eff = re.search("(.*)-has-add-effect-(.*)", f)
            if add_eff:
                facts.add(add_eff.group(2))
                if add_eff.group(1) not in operators:
                    operators[add_eff.group(1)] = (set(), set(), set())
                operators[add_eff.group(1)][1].add(add_eff.group(2))
                continue
            del_eff = re.search("(.*)-has-del-effect-(.*)", f)
            if del_eff:
                facts.add(del_eff.group(2))
                if del_eff.group(1) not in operators:
                    operators[del_eff.group(1)] = (set(), set(), set())
                operators[del_eff.group(1)][2].add(del_eff.group(2))
                continue
            print("Warning when generating task from gamma, unknown fact: '{}'".format(f))
        op = [Operator(k, v[0], v[1], v[2]) for k, v in operators.items()]
        Task.DEFAULT_NAME += 1
        return Task(Task.DEFAULT_NAME, facts, frozenset(initial_state), frozenset(goal_state), op)




