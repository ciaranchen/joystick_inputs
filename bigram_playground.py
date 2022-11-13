import json
import pulp as pp
from itertools import product

# TODO: with solver to do this problem.


mylp = pp.LpProblem("lp1", pp.LpMinimize)

with open('bigram-pairs.json') as fp:
    data = json.load(fp)

data = dict(data)
print(data)

letters = 'abcdefghijklmnopqrstuvwxyz'
frq_single_gram = "etaoins"
len_s = len(frq_single_gram)
double_grams = [a for a in letters if a not in frq_single_gram]

table_size = 3

cm = {s: {} for s in frq_single_gram}
for s, d in product(frq_single_gram, double_grams):
    cm[s][d] = data[''.join(sorted(s + d))]

already_selected = []

for s in frq_single_gram:
    choices = {d: v for d, v in cm[s].items() if d not in already_selected}
    last_chosen = sorted(choices.items(), key=lambda x: x[1])[:table_size]
    print(s, last_chosen)
    already_selected.extend([x[0] for x in last_chosen])


