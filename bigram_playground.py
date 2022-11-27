import json
import string
# import pulp as pp
from itertools import product

# TODO: with solver to do this problem
# mylp = pp.LpProblem("lp1", pp.LpMinimize)

with open('bigram-pairs.json') as fp:
    data = json.load(fp)

data = dict(data)
# print(data)

not_count = 'etaoinshrd'
other_letters = [e for e in string.ascii_letters[:26] if e not in not_count]

letter_counts = {a: 0 for a in not_count}

for k, v in data.items():
    a, b = k
    if a in not_count and b in other_letters:
        letter_counts[a] += v
    if a in other_letters and b in not_count:
        letter_counts[b] += v

letter_ord = sorted(not_count, key=lambda x: letter_counts[x], reverse=True)
print(letter_ord[:2])

g_keys = [k for k in data if 'e' in k and k.strip('e') in other_letters]
g_keys = sorted(g_keys,  key=lambda x: data[x], reverse=True)
letters1 = [k.strip('e') for k in g_keys[:8]]
print(letters1)
letters2 = [e for e in other_letters if e not in letters1]
print(letters2)

# letters = 'abcdefghijklmnopqrstuvwxyz'
# frq_single_gram = "etaoins"
# len_s = len(frq_single_gram)
# double_grams = [a for a in letters if a not in frq_single_gram]
#
# table_size = 3
#
# cm = {s: {} for s in frq_single_gram}
# for s, d in product(frq_single_gram, double_grams):
#     cm[s][d] = data[''.join(sorted(s + d))]
#
# already_selected = []
#
# for s in frq_single_gram:
#     choices = {d: v for d, v in cm[s].items() if d not in already_selected}
#     last_chosen = sorted(choices.items(), key=lambda x: x[1])[:table_size]
#     print(s, last_chosen)
#     already_selected.extend([x[0] for x in last_chosen])
