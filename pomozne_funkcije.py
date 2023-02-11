# vsebuje pomozne funkcije za analizo podatkov
import random
import numpy as np


def num_of_spaces(clanek):
    return clanek.count(" ")


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
            scores *= (1 / ((3 + n) * len(text)) + lookup_dict[seq]) ** (count / len(text))
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
    return test(probability_dicts, language_to_int, test_map, ns, test_sample_size)