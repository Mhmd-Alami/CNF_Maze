from itertools import product
from sympy import symbols, Or, And, Not
from sympy.logic.inference import satisfiable

class LocalizationKB:
    def __init__(self, maze):
        self.maze = maze
        self.H = len(maze)
        self.W = len(maze[0])
        self.time = 0
        self.vars = {}
        self.clauses = []
        self.history = []
        self.belief = set()
        self._init_time(0)
        self._exactly_one(0)
        self._update_belief(0)

    def _init_time(self, t):
        for r, c in product(range(self.H), range(self.W)):
            if self.maze[r][c] == 0 and (r,c,t) not in self.vars:
                self.vars[(r, c, t)] = symbols(f"v_{r}_{c}_{t}")

    def _exactly_one(self, t):
        syms = [v for (r,c,tt), v in self.vars.items() if tt == t]
        self.clauses.append(Or(*syms))
        for i in range(len(syms)):
            for j in range(i+1, len(syms)):
                self.clauses.append(Or(Not(syms[i]), Not(syms[j])))

    def _add_transition(self, t, act):
        self._init_time(t)
        self._exactly_one(t)
        prev = {(r,c): self.vars[(r,c,t-1)] for (r,c,tt) in self.vars if tt == t-1}
        curr = {(r,c): self.vars[(r,c,t)]   for (r,c,tt) in self.vars if tt == t}
        for (r,c), sym in curr.items():
            neighbors = []
            acting = {'N':[1,0], 'S':[-1,0], 'E':[0,-1], 'W':[0,1], 'O':[0,0]}
            dr, dc = acting[act]
            p = (r+dr, c+dc)
            if p in prev:
                neighbors.append(prev[p])
            if neighbors:
                self.clauses.append(Or(Not(sym), Or(*neighbors)))

    def _add_sensor(self, percept, t):
        for (r,c,tt), sym in self.vars.items():
            if tt != t:
                continue
            actual = ''.join('1' if (r+dr < 0 or r+dr >= self.H or c+dc < 0 or c+dc >= self.W or self.maze[r+dr][c+dc] == 1) else '0' for dr,dc in [(-1,0),(1,0),(0,1),(0,-1)])
            if actual != percept:
                self.clauses.append(Not(sym))

    def _update_belief(self, t):
        base = And(*self.clauses)
        remaining = base
        new_belief = set()
        while True:
            model = satisfiable(remaining)
            if not model:
                break
            for (r,c,tt), sym in self.vars.items():
                if tt == t and model.get(sym, False):
                    new_belief.add((r,c))
                    remaining = And(remaining, Not(sym))
                    break
        self.belief = new_belief

    def add_observation(self, action, percept):
        self.history.append((action, percept))
        self.time += 1
        t = self.time
        self._add_transition(t, action)
        self._add_sensor(percept, t)
        self._update_belief(t)

    def get_belief(self):
        return self.belief

    def get_history(self):
        return self.history
