# -*- coding: utf-8 -*-
"""Kopia notatnika minrnn_wsb.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nz4q3rp3Ex9HfioiQrHS9X0Ivce1r-WG
"""

# --- SEKCJA 1: Pobieranie tekstu z Projektu Gutenberg ---
import requests

def download_book(book_url, filename="input.txt"):
    response = requests.get(book_url)
    if response.status_code == 200:
        text = response.text.replace('\r\n', ' ').replace('\r', ' ')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✅ Book downloaded to {filename}")
    else:
        print("❌ Failed to download book.")

# --- SEKCJA 2: Pobranie książki ---
book_url = "https://www.gutenberg.org/cache/epub/32461/pg32461.txt"

download_book(book_url)

# --- SEKCJA 2: Pobranie 2 książki ---
book_url = "https://www.gutenberg.org/files/27062/27062-0.txt"
download_book(book_url)

# --- SEKCJA 3: Przygotowanie danych i modelu ---
import numpy as np

with open("input.txt", "r", encoding="utf-8") as f:
    data = f.read()

chars = list(set(data))
data_size, vocab_size = len(data), len(chars)
print(f"📚 Długość danych: {data_size}, unikalnych znaków: {vocab_size}")

char_to_ix = { ch:i for i,ch in enumerate(chars) }
ix_to_char = { i:ch for i,ch in enumerate(chars) }

# Parametry sieci
hidden_size = 80
seq_length = 25
learning_rate = 1e-1

# Parametry modelu
Wxh = np.random.randn(hidden_size, vocab_size) * 0.01
Whh = np.random.randn(hidden_size, hidden_size) * 0.01
Why = np.random.randn(vocab_size, hidden_size) * 0.01
bh = np.zeros((hidden_size, 1))
by = np.zeros((vocab_size, 1))
# --- SEKCJA 4: Funkcja strat i propagacja wsteczna ---
def lossFun(inputs, targets, hprev):
    xs, hs, ys, ps = {}, {}, {}, {}
    hs[-1] = np.copy(hprev)
    loss = 0

    for t in range(len(inputs)):
        xs[t] = np.zeros((vocab_size,1))
        xs[t][inputs[t]] = 1
        hs[t] = np.tanh(np.dot(Wxh, xs[t]) + np.dot(Whh, hs[t-1]) + bh)
        ys[t] = np.dot(Why, hs[t]) + by
        ps[t] = np.exp(ys[t]) / np.sum(np.exp(ys[t]))
        loss += -np.log(ps[t][targets[t],0])

    dWxh, dWhh, dWhy = np.zeros_like(Wxh), np.zeros_like(Whh), np.zeros_like(Why)
    dbh, dby = np.zeros_like(bh), np.zeros_like(by)
    dhnext = np.zeros_like(hs[0])

    for t in reversed(range(len(inputs))):
        dy = np.copy(ps[t])
        dy[targets[t]] -= 1
        dWhy += np.dot(dy, hs[t].T)
        dby += dy
        dh = np.dot(Why.T, dy) + dhnext
        dhraw = (1 - hs[t] * hs[t]) * dh
        dbh += dhraw
        dWxh += np.dot(dhraw, xs[t].T)
        dWhh += np.dot(dhraw, hs[t-1].T)
        dhnext = np.dot(Whh.T, dhraw)

    for dparam in [dWxh, dWhh, dWhy, dbh, dby]:
        np.clip(dparam, -5, 5, out=dparam)

    return loss, dWxh, dWhh, dWhy, dbh, dby, hs[len(inputs)-1]

import re
def clean_text(text):
    text = re.sub(r'[^A-Za-z0-9\s.,!?;:\'\"()\-\n]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

data = clean_text(data)

# --- SEKCJA 5: Generowanie tekstu ---
def sample(h, seed_ix, n):
    x = np.zeros((vocab_size, 1))
    x[seed_ix] = 1
    ixes = []
    for t in range(n):
        h = np.tanh(np.dot(Wxh, x) + np.dot(Whh, h) + bh)
        y = np.dot(Why, h) + by
        p = np.exp(y) / np.sum(np.exp(y))
        ix = np.random.choice(range(vocab_size), p=p.ravel())
        x = np.zeros((vocab_size, 1))
        x[ix] = 1
        ixes.append(ix)
    return ''.join(ix_to_char[ix] for ix in ixes)

# --- SEKCJA 6: Trening modelu ---
n, p = 0, 0
mWxh, mWhh, mWhy = np.zeros_like(Wxh), np.zeros_like(Whh), np.zeros_like(Why)
mbh, mby = np.zeros_like(bh), np.zeros_like(by)
smooth_loss = -np.log(1.0/vocab_size)*seq_length

num_iterations = 50000  # <- możesz zmieniać

for n in range(num_iterations):
    if p + seq_length + 1 >= len(data) or n == 0:
        hprev = np.zeros((hidden_size, 1))
        p = 0

    inputs = [char_to_ix[ch] for ch in data[p:p+seq_length]]
    targets = [char_to_ix[ch] for ch in data[p+1:p+seq_length+1]]

    if n % 1000 == 0:
        sample_text = sample(hprev, inputs[0], 200)
        print(f"---\nSample at iter {n}:\n{sample_text}\n---")

    loss, dWxh, dWhh, dWhy, dbh, dby, hprev = lossFun(inputs, targets, hprev)
    smooth_loss = smooth_loss * 0.999 + loss * 0.001

    if n % 1000 == 0:
        print(f"Iter {n}, Loss: {smooth_loss}")

    for param, dparam, mem in zip([Wxh, Whh, Why, bh, by],
                                  [dWxh, dWhh, dWhy, dbh, dby],
                                  [mWxh, mWhh, mWhy, mbh, mby]):
        mem += dparam * dparam
        param += -learning_rate * dparam / np.sqrt(mem + 1e-8)

    p += seq_length