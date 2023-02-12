# vsebuje pomozne funkcije za analizo podatkov
import random
import numpy as np
import pandas as pd
from math import gcd
from functools import reduce

def lcm(a, b):
    return a * b // gcd(a, b)

def lcmm(*args):
    return reduce(lcm, args)


def num_of_spaces(text):
    return text.count(" ") + text.count("\n")

def avg_word_len(text):
    chars = 0
    words = 1
    empty = True
    for i in text:
        if i.isalnum():
            empty = False
            chars += 1
        else:
            if not empty:
                empty = True
                words += 1
    return (chars / words)



def extract(df):
    return list(zip(df["jezik"], df["besedilo"]))


def map_languages_to_ints(text_and_lang_list):
    language_to_int = {}
    next_int = -1
    for lang, text in text_and_lang_list:
        if lang not in language_to_int:
            next_int += 1
            language_to_int[lang] = next_int
    return language_to_int


def add_sequence_to_lookup_dict(lookup_dict, language_to_int, text, lang, n):
    table = [0] * 40
    for i in range(len(text) - n + 1):
        seq = text[i: i + n]
        if seq not in lookup_dict:
            lookup_dict[seq] = table.copy()
        lookup_dict[seq][language_to_int[lang]] += 1


def create_probability_dicts(extracted, ns):
    language_to_int = map_languages_to_ints(extracted)
    re = []
    for n in ns:
        lookup_dict = {}
        for lang, text in extracted:
            add_sequence_to_lookup_dict(lookup_dict, language_to_int, text, lang, n)

        for lang in language_to_int.keys():
            lang_idx = language_to_int[lang]
            lang_total = sum(seq[lang_idx] for seq in lookup_dict.values())
            for seq in lookup_dict.keys():
                lookup_dict[seq][lang_idx] /= lang_total

        for seq in lookup_dict.keys():
            lookup_dict[seq] = np.array(lookup_dict[seq])
        re.append(lookup_dict)

    return re, language_to_int


def scores_array(lookup_dict, n, text):
    seen_dict = {}
    for i in range(len(text) - n + 1):
        seq = text[i: i + n]
        if seq in seen_dict:
            seen_dict[seq] += 1
        else:
            seen_dict[seq] = 1

    scores = np.ones(40)
    for seq, count in seen_dict.items():
        if seq in lookup_dict:
            # tu bi bilo bolj smiselno *= kot += vendar += daje boljše rezulate
            scores += (1 / ((3 + n) * len(text)) + lookup_dict[seq]) ** (count / len(text))
    return scores


def classify_language(lookup_dicts, lang_to_int, n_list, text):
    final_score = np.ones(40)
    for lookup_dict, n in zip(lookup_dicts, n_list):
        final_score *= scores_array(lookup_dict, n, text)
    best_lang = max(lang_to_int, key=lambda x: final_score[lang_to_int[x]])
    return best_lang


def grup_by_lang(lang_text_list):
    map_lang_to_texts = {}
    for lang, text in lang_text_list:
        if lang in map_lang_to_texts:
            map_lang_to_texts[lang].append(text)
        else:
            map_lang_to_texts[lang] = [text]
    return map_lang_to_texts


def shuffle_map(map_to_shuffle):
    for key in map_to_shuffle.keys():
        random.shuffle(map_to_shuffle[key])


def split_off(map_to_split, sample_size):
    sample = []
    for lang in map_to_split.keys():
        sample += [(lang, i) for i in map_to_split[lang][:sample_size]]
        map_to_split[lang] = [i for i in map_to_split[lang][sample_size:]]
    return sample, map_to_split


def test(probability_dicts, lang_to_int, test_map, n_list, test_sample_size):
    successful = [0] * 40
    for lang in lang_to_int.keys():
        for i, text in enumerate(test_map[lang]):
            if i == test_sample_size: break
            successful[lang_to_int[lang]] += (lang == classify_language(probability_dicts, lang_to_int, n_list, text))

    return [i / test_sample_size for i in successful]


def wrap_testing(df, ns, look_up_sample_size, test_sample_size):
    extracted = extract(df)
    map_lang_to_texts = grup_by_lang(extracted)
    shuffle_map(map_lang_to_texts)
    sample, test_map = split_off(map_lang_to_texts, sample_size=look_up_sample_size)
    probability_dicts, language_to_int = create_probability_dicts(sample, ns=ns)
    success = test(probability_dicts, language_to_int, test_map, ns, test_sample_size)
    return pd.DataFrame([(lang, success[index]) for lang, index in language_to_int.items()], columns=["Jezik", "Delež pravilno klasificiranih"])

# __________________________________________________________________


def letter_frequency(texts):
    frequency = {}
    total_letters = 0
    for text in texts:
        for letter in text:
            if letter.isalpha():
                total_letters += 1
                if letter in frequency:
                    frequency[letter] += 1
                else:
                    frequency[letter] = 1
    for letter in frequency:
        frequency[letter] /= total_letters
    return frequency


def word_frequency(text_list):
    word_counts = {}
    for text in text_list:
        words = text.split()
        for word in words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
    return word_counts


def frequency_dict_to_list(frequency):
    frequency_list = []
    for letter, count in frequency.items():
        frequency_list.append(count)
    return frequency_list

def calculate_difference(list1, list2):
    length = lcmm(len(list1), len(list2))
    new_list1 = np.array([list1[i % len(list1)] for i in range(length)])
    new_list2 = np.array([list2[i % len(list2)] for i in range(length)])
    area = np.trapz(np.abs(new_list2 - new_list1), np.array(range(length)))
    return area


def resample_list(lst, n):
    m = len(lst)
    step = m / n
    new_lst = []
    for i in range(n):
        x = i * step
        start = int(np.floor(x))
        end = int(np.ceil(x + step))
        values = lst[start:end]
        avg = sum(values) / len(values)
        new_lst.append(avg)
    return new_lst


def append_lists(a, b):
    if b:
        len_a = len(a)
        len_b = len(b[0])
        max_len = max(len_a, len_b)
        a += [0] * (max_len - len_a)
        b = [item + [0] * (max_len - len_b) for item in b]
    return [a] + b


def letter_frequency_destribution(df):
    acc = []
    extracted = extract(df)
    lang_to_int = grup_by_lang(extracted)
    for lang, texts in lang_to_int.items():
        acc = append_lists(sorted(frequency_dict_to_list(letter_frequency(texts)), reverse=True), acc)

    re = []
    for i, (lang, texts) in enumerate(lang_to_int.items()):
        re.append((lang, acc[i]))
    return re


def improved_letter_frequency(texts):
    frequency = {}
    total_letters = 0
    for text in texts:
        for letter in text.lower():
            if letter.isalpha():
                total_letters += 1
                if letter in frequency:
                    frequency[letter] += 1
                else:
                    frequency[letter] = 1
    for letter in frequency:
        frequency[letter] /= total_letters
    return frequency


def improved_letter_frequency_destribution(df):
    acc = []
    extracted = extract(df)
    lang_to_int = grup_by_lang(extracted)
    for lang, texts in lang_to_int.items():
        acc = append_lists(sorted(frequency_dict_to_list(improved_letter_frequency(texts)), reverse=True)[:40], acc)

    re = []
    for i, (lang, texts) in enumerate(lang_to_int.items()):
        re.append((lang, acc[i]))
    return re


def improved_word_frequency_destribution(df):
    acc = []
    extracted = extract(df)
    lang_to_int = grup_by_lang(extracted)
    for lang, texts in lang_to_int.items():
        acc = append_lists(sorted(frequency_dict_to_list(word_frequency(texts)), reverse=True)[:1000], acc)

    re = []
    for i, (lang, texts) in enumerate(lang_to_int.items()):
        re.append((lang, acc[i]))
    return re