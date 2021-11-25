from typing import Dict, List

import json
import re
from time import time
from pprint import pprint

replace_words_setting: Dict[str, List[str]] = {
    # 'テスト': ['のことなんだけどほらニー'],
    # 'ありがとう☆': ['ありがとう'],
    "TohAri": ["とうあり"],
    # "Gatoh": ["がとう"],
    # 'thank': ['ありがとう'],
    # 'にーさ': ['あ'],
    # 'NISA': ['にーさ', 'ニーサ', 'にさ', 'にいさ', ],
    # 'VISA-CARD': ['ビザカード'],
    # 'CRM': ['池袋の展示会'],
    'エックス': ['XXXXX']
}


def marge_replace_words_setting(replace_words_setting: Dict[str, List[str]]) -> List[List[str]]:
    new_replace_words = []
    for word_to, words_from in replace_words_setting.items():
        for word_from in words_from:
            new_replace_words.append([word_from, word_to])

    # 文字の長さ順に処理するのをやめた
    # new_replace_words.sort(key=lambda x: len(x[0]), reverse=True)

    print('-' * 10, '変換テーブル', '-' * 10)
    for i, y in enumerate(new_replace_words):
        print(str((i + 1)) + '.', " ⇒ ".join(y))
    print('-' * 32)
    return new_replace_words


def replace_words():
    all_lattice = load_file()
    setting = marge_replace_words_setting(replace_words_setting)
    print_lattice(load_file(), '変換前')

    start_time = time()

    all_lattice = delete_nulls(all_lattice)

    for word_from, word_to in setting:
        # 大小文字を意識せずシンプルにReplace
        simple_replace(all_lattice, word_from, word_to)

        replace_position = replace_point_search(all_lattice, word_from)
        # 複数のLatticeにまたがる部分をReplace
        complex_replace(all_lattice, replace_position, word_to)

    # 「Replace済の単語は置き換えない」をやめた
    # for speaker, links in all_lattice.items():
    #     for link, data in links.items():
    #         if 'already_replaced' in all_lattice[speaker][link]:
    #             del all_lattice[speaker][link]['already_replaced']

    end_time = time()
    print_lattice(all_lattice, '変換後')
    print('-' * 10, '処理時間', '-' * 10)
    print(end_time - start_time, '秒')
    return all_lattice


def delete_nulls(all_lattice):
    delete_lattice = []
    for speaker, links in all_lattice.items():
        for link, data in links.items():
            if data['word'] in ["!NULL", "!ENTER", "!EXIT", "!LG_HANGUP", "!SILENCE", "!PAUSE-FILLER"]:
                delete_lattice.append([speaker, link])
    for speaker, link in delete_lattice:
        del all_lattice[speaker][link]
    return all_lattice


def simple_replace(all_lattice, word_from: str, word_to: str) -> None:
    for speaker, links in all_lattice.items():
        for link, data in links.items():
            # 「Replace済の単語は置き換えない」をやめた
            # if 'already_replaced' in data and data['already_replaced'] is True:
            #     continue
            word = all_lattice[speaker][link]['word']
            if re.search(word_from, word, flags=re.IGNORECASE):
                # 「Replace済の単語は置き換えない」をやめた
                # all_lattice[speaker][link].setdefault('already_replaced', True)
                all_lattice[speaker][link]['word'] = re.sub(word_from, word_to, word, flags=re.IGNORECASE)


def replace_point_search(all_lattice, word_from: str):
    replace_position = {}
    for speaker, links in sorted(all_lattice.items(), key=lambda x: int(x[0])):
        replace_position.setdefault(speaker, {})
        hit_links = []
        hit_position = 0
        lattice_first_half_position = 0
        for link, data in sorted(links.items(), key=lambda y: int(y[0])):
            # 「Replace済の単語は置き換えない」をやめた
            # if 'already_replaced' in data and data['already_replaced'] is True:
            #     hit_links = []
            #     hit_position = 0
            #     lattice_first_half_position = 0
            #     continue

            # 句読点は処理に含めない
            if data['word'] in ["、", "。", "!", "?"]:
                continue

            # 複数のLatticeにまたがる部分をReplaceするための処理なので、
            # １つの単語にReplace対象がある場合は処理しない
            if word_from in data['word']:
                hit_links = []
                hit_position = 0
                lattice_first_half_position = 0
                continue

            for i, word in enumerate(data['word']):
                if word == word_from[hit_position]:
                    if link not in hit_links:
                        hit_links.append(link)
                    if hit_position == 0:
                        lattice_first_half_position = i
                    hit_position += 1
                    if hit_position == len(word_from):
                        replace_position[speaker].setdefault(hit_links[0], {
                            'hit_links': hit_links,
                            'first_half': links[hit_links[0]]['word'][lattice_first_half_position:],
                            'second_half': links[hit_links[-1]]['word'][:i + 1]
                        })
                        hit_links = []
                        hit_position = 0
                        lattice_first_half_position = 0
                else:
                    hit_links = []
                    hit_position = 0
                    lattice_first_half_position = 0
    return replace_position


def complex_replace(all_lattice, replace_position, word_to):
    for speaker, replace_links in replace_position.items():
        if not replace_links:
            continue
        for replace_link, data in replace_links.items():
            word = all_lattice[speaker][data['hit_links'][0]]['word']
            all_lattice[speaker][data['hit_links'][0]]['word'] = word[:-len(data['first_half'])] + word_to
            # 「Replace済の単語は置き換えない」をやめた
            # all_lattice[speaker][data['hit_links'][0]].setdefault('already_replaced', True)

            for x in data['hit_links'][1:-1]:
                del all_lattice[speaker][x]

            # 置き換えた単語の間にある句読点を削除
            for x in range(int(data['hit_links'][0]) + 1, int(data['hit_links'][-1])):
                x = str(x)
                if x not in all_lattice[speaker]:
                    continue
                if all_lattice[speaker][x]["word"] in ["、", "。", "!", "?"]:
                    del all_lattice[speaker][x]

            word = all_lattice[speaker][data['hit_links'][-1]]['word']

            if word[len(data['second_half']):]:
                all_lattice[speaker][data['hit_links'][-1]]['word'] = word[len(data['second_half']):]
                # 「Replace済の単語は置き換えない」をやめた
                # all_lattice[speaker][data['hit_links'][-1]].setdefault('already_replaced', True)
            else:
                del all_lattice[speaker][data['hit_links'][-1]]
    return all_lattice


def print_lattice(all_lattice, title: str) -> None:
    print('-' * 10, title, '-' * 10)
    for speaker, links in sorted(all_lattice.items(), key=lambda x: int(x[0])):
        print('話者:', speaker)
        string = ''
        for link, data in sorted(links.items(), key=lambda y: int(y[0])):
            string += data['word'] + ' '
            print(link, data)
        print(string[:-1])


def load_file():
    # with open("lattice_2h.json", mode="r", encoding='utf_8_sig') as f:
    with open("lattice.json", mode="r", encoding='utf_8_sig') as f:
        all_lattice = json.loads(f.read())
    return all_lattice


if __name__ == '__main__':
    result = replace_words()
    # pprint(result)
