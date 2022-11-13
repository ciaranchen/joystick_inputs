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

cm = {d: [] for d in double_grams}
for s, d in product(frq_single_gram, double_grams):
    cm[d].append(data[''.join(sorted(s + d))])
print(cm)

all_grams = double_grams + ['?', "'"]

assert len(all_grams) == table_size * len_s


def calc_number(d, i):
    d = d[0]
    if d == '?' or d == "'":
        return 0
    return cm[d][i]


possible_tables = [tuple(c) for c in pp.allcombinations(all_grams, table_size)]

x = pp.LpVariable.dicts(
    "table", possible_tables, lowBound=0, upBound=1, cat=pp.LpInteger
)

seating_model = pp.LpProblem("Wedding Seating Model", pp.LpMinimize)

seating_model += pp.lpSum([calc_number(table, x[table]) for table in possible_tables])

seating_model += (
    pp.lpSum([x[table] for table in possible_tables]) == table_size * frq_single_gram,
    "Maximum_number_of_tables",
)

for guest in all_grams:
    seating_model += (
        pp.lpSum([x[table] for table in possible_tables if guest in table]) == 1,
        f"Must_seat_{guest}",
    )

seating_model.solve()

print(f"The choosen tables are out of a total of {len(possible_tables)}:")
for table in possible_tables:
    if x[table].value() == 1.0:
        print(table)
