import pandas as pd
import re
import csv
from collections import defaultdict

input_file = 'companie_data.csv'
output_file = 'generated_keywords.csv'

min_companies_return = 2
max_keyword_len = 25
stopwords = {'and', 'the', 'of', 'in', 'de', 'van', 'pt', 'cv', 'ltd', 'int', 'inc'}


def get_words(name):

    if not isinstance(name, str):
        return []

    name = re.sub(r'^(PT|CV|UD|FA|TB|PD|PN)\s+', '', name, flags=re.IGNORECASE) # remove prefix from company name (compamy type)
    name = name.lower().strip()
    words = re.findall(r'[a-z]+', name)

    return [w for w in words if w not in stopwords and len(w) >= 3]


def build_word_index(df):
    # map each word from company name against the indices it appears 
    # for example the word solar from company name = PT Solar Aaaa Energi appears on index 0 and 1513 index so it woud be solar: {0, 1513}

    word_to_companies = defaultdict(set)
    for idx, name in enumerate(df['company_name']):
        for word in get_words(name):
            word_to_companies[word].add(idx)

    return word_to_companies


def filter_valid_keywords(word_to_companies):
    # keep only thos keywrods where the length of companies/index is > 2 means if it appear more than 2 times and the length of keyword is < 25 character

    return {
        word: companies
        for word, companies in word_to_companies.items()
        if len(companies) >= min_companies_return and len(word) <= max_keyword_len
    }


def greedy_set_cover(valid_keywords, total_companies):

    # pic a word that cover the most uncovered companies/indices
    # add this to the selected keyword, mark those companies/indices as covered
    # repeat the same process until no word cover >= 2 companies becaue we need to skip the singletons

    covered = set()
    selected = []
    remaining = dict(valid_keywords)
    step = 0

    while remaining:
        step += 1

        # find keyword that covers the most uncovered companies
        best_kw = None
        best_new_coverage = set()

        for keyword, companies in remaining.items():
            new_companies = companies - covered

            if len(new_companies) > len(best_new_coverage):
                best_kw = keyword
                best_new_coverage = new_companies

        # stop if the best keyword doesn't cover >= 2 companies
        if len(best_new_coverage) < min_companies_return:
            break

        # add best keyword to selected list
        selected.append({
            'keyword': best_kw,
            'new_companies_covered': len(best_new_coverage),
            'total_hits': len(remaining[best_kw]),
        })

        # combines new companies/indices becasuse these are covered
        covered = covered | best_new_coverage

        # remove selected keyword from remaining
        del remaining[best_kw]

    return selected, covered



def save_keywords(selected, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['keyword', 'new_companies_covered', 'total_hits'])
        writer.writeheader()
        writer.writerows(selected)


def main():
    df = pd.read_csv(input_file)
    total = len(df)
    print(f"{total} companies")

    word_to_companies = build_word_index(df)
    print(f"unique:{len(word_to_companies)}")

    valid_keywords = filter_valid_keywords(word_to_companies)
    print(f"valid:{len(valid_keywords)}")

    selected, covered = greedy_set_cover(valid_keywords, total)

    uncovered = total - len(covered)
    print(f"uncovered:{uncovered}")

    save_keywords(selected, output_file)


if __name__ == "__main__":
    main()