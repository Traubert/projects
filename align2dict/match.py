import sys
import logging
import argparse

parser = argparse.ArgumentParser(description='Build a dictionary from aligned translated lines.')
parser.add_argument('sourcefile')
parser.add_argument('targetfile')
parser.add_argument('--verbose', '-v', action='store_true')
args = parser.parse_args()

loglevel = 'DEBUG' if args.verbose else 'WARNING'
logging.basicConfig(format='%(message)s', level=getattr(logging, loglevel))

n_source_words_to_print = 100
n_target_sequences_to_print = 8

source_file = open(args.sourcefile)
target_file = open(args.targetfile)

spaced_dict = {}
freqdict = {}

def handle(source_word, target_sequence):
    sorted_target_sequence = list(map(lambda x: x[1],
                                      sorted(target_sequence, key = lambda x: x[0])))
    target_string = ''.join(sorted_target_sequence).replace('▁', ' ').strip(',.?! -"\'’')
    if target_string == '':
        logging.debug(f"SKIPPED empty target word for {current_source_word.replace('▁', '')}")
        return
    if source_word not in spaced_dict:
        spaced_dict[source_word] = {target_string: 1}
    else:
        spaced_dict[source_word][target_string] = spaced_dict[source_word].get(target_string, 0) + 1
    freqdict[source_word] = freqdict.get(source_word, 0) + 1
    logging.debug(f"{current_source_word.replace('▁', '')} | {target_string}")

while True:
    try:
        sourceline = source_file.readline().strip()
        targetline = target_file.readline().strip()
    except EOFError:
        break
    if sourceline == '':
        break
    align_idx = targetline.rindex(' ||| ')
    align_info = targetline[align_idx + 5:]
    targetline = targetline[:align_idx]
    source_spm_parts = sourceline.split('▁')
    source_part_pairs = list(map(lambda x: [x, []], sourceline.split(' ')))
    target_parts = targetline.split(' ')
    for alignment in align_info.split(' '):
        s, t = alignment.split('-')
        try:
            source_part_pairs[int(s)][1].append((int(t),
                                                 target_parts[int(t)].strip()))
        except IndexError:
            continue
    current_source_word = ''
    current_target_sequence = []
    for pair in source_part_pairs:
        if pair[0].startswith('▁'):
            if current_source_word != '':
                handle(current_source_word, current_target_sequence)
            current_source_word = pair[0]
            current_target_sequence = pair[1]
        else:
            current_source_word += pair[0]
            current_target_sequence += pair[1]
    if current_source_word != '':
        handle(current_source_word, current_target_sequence)

sorted_keys = sorted(freqdict.keys(), key = lambda x: len(spaced_dict[x]), reverse = True)
for key in sorted_keys[:n_source_words_to_print]:
    print(f'{key} ({freqdict[key]}):')
    sorted_target_keys = sorted(spaced_dict[key].keys(), key = lambda x: spaced_dict[key][x], reverse = True)
    for target_key in sorted_target_keys[:n_target_sequences_to_print]:
        count = spaced_dict[key][target_key]
        count_string = f' ({count})' if count > 1 else ''
        print(f'  {target_key.strip()}{count_string}')
