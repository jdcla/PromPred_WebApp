import time
import numpy as np
from flask_login import current_user
from . import celery, db
from .models import Sequence

@celery.task
def wait(seconds):
    time.sleep(seconds)
    np.random

@celery.task
def create_promoter_lib(user, library, plan,n=10,th=0.9):
    time.sleep(5)
    sequences = createSequencesMC(plan, n, th)
    for sequence in sequences:
        s = Sequence(body=sequence, library_seq=library, creator_seq=user)
        db.session.add(s)
    library.status = "complete"
    db.session.commit()


def createSequencesMC(plan, n, th):
    m = plan.count('N')
    nt = [plan.count('a'), plan.count('t'), plan.count('c'), plan.count('g')]
    dual = [plan.count('R'), plan.count('Y'), plan.count('K'), plan.count('M')]
    triple = [plan.count('B'), plan.count('D'), plan.count('H'), plan.count('V')]

    indices = []
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'N']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'a']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 't']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'c']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'g']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'R']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'Y']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'K']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'M']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'B']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'D']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'H']))
    indices.append(np.array([pos for pos, char in enumerate(plan) if char == 'V']))

    checks = []
    for i in range(len(nt)):
        checks.append(np.random.rand(n, nt[i]))

    MC = []
    MC.append(np.array([np.random.choice(['A', 'T', 'C', 'G'], size=m) for i in range(n)]))
    MC.append(np.array(
        [np.array([np.random.choice(['T', 'C', 'G']) if checks[0][j, i] >= th else 'A' for i in range(nt[0])]) for j in
         range(n)]))
    MC.append(np.array(
        [np.array([np.random.choice(['A', 'C', 'G']) if checks[1][j, i] >= th else 'T' for i in range(nt[1])]) for j in
         range(n)]))
    MC.append(np.array(
        [np.array([np.random.choice(['A', 'T', 'G']) if checks[2][j, i] >= th else 'C' for i in range(nt[2])]) for j in
         range(n)]))
    MC.append(np.array(
        [np.array([np.random.choice(['A', 'T', 'C']) if checks[3][j, i] >= th else 'G' for i in range(nt[3])]) for j in
         range(n)]))
    MC.append(np.array([np.random.choice(['A', 'G'], size=dual[0]) for i in range(n)]))
    MC.append(np.array([np.random.choice(['T', 'C'], size=dual[1]) for i in range(n)]))
    MC.append(np.array([np.random.choice(['T', 'G'], size=dual[2]) for i in range(n)]))
    MC.append(np.array([np.random.choice(['A', 'C'], size=dual[3]) for i in range(n)]))
    MC.append(np.array([np.random.choice(['T', 'C', 'G'], size=triple[0]) for i in range(n)]))
    MC.append(np.array([np.random.choice(['A', 'T', 'G'], size=triple[1]) for i in range(n)]))
    MC.append(np.array([np.random.choice(['A', 'T', 'C'], size=triple[2]) for i in range(n)]))
    MC.append(np.array([np.random.choice(['A', 'C', 'G'], size=triple[3]) for i in range(n)]))
    # MC = np.array(MC).reshape(n,m)

    sequences = np.array([[i for n in range(n)] for i in plan])
    for j, index in enumerate(indices):
        for i, index_value in enumerate(index):
            sequences[index_value, :] = MC[j][:, i]

    sequences = [''.join(seq) for seq in sequences.T]

    return sequences