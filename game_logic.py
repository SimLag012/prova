import random

truths = [
    "Accendo la luce quando ho paura del buio.",
    "A volte parlo da solo come se fossi in un talk show.",
    "Ho pianto guardando un cartone animato."
]

memes = [
    "Quando sogno, sogno come ti picchierei fortissimo.",
    "Il gatto è il vero padrone di casa.",
    "Studio meglio se abbraccio un peluche."
]

def get_random_truth_or_meme():
    if random.random() > 0.5:
        return random.choice(truths), "truth"
    else:
        return random.choice(memes), "meme"
