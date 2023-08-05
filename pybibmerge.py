import glob
import os
import re

bib_folder = './bibfiles/'

def parse_file(file_path):
    entries = {}
    with open(file_path, 'r') as file:
        content = file.read()

    pattern_entry = r"@(\w+)\{([\w\d]+),\s*([^@]+)\}"
    matches = re.findall(pattern_entry, content, re.MULTILINE)

    for match in matches:
        entry_type = match[0]
        entry_key = match[1]
        pattern_fields = r"(\w+)\s*=\s*{(.+)}"
        fields = re.findall(pattern_fields, match[2], re.MULTILINE)
        entry = {
            'type': entry_type,
        }
        for key, field in fields:
            entry[key.strip()] = field.strip()

        entries[entry_key] = entry

    return entries


def merge_dictlist(dicts, merge_values):
    merged_dict = {}
    for d in dicts:
        for key, value in d.items():
            if key in merged_dict:
                merged_dict[key] = merge_values(merged_dict[key], value)
            else:
                merged_dict[key] = value
    return merged_dict


def merge_entries(dict1, dict2):
    merged_dict = dict1.copy()
    # find dict priority in case of duplicate keys (choose most recent year)
    prioritize_dict2 = False
    if ('year' in dict1 and 'year' in dict2 and dict2['year'] > dict1['year']) or ('year' in dict2 and 'year' not in dict1):
        prioritize_dict2 = True
    # merge
    for key, value in dict2.items():
        if key in merged_dict:
            if prioritize_dict2:
                merged_dict[key] = value
        else:
            merged_dict[key] = value
    return merged_dict

def write_to_file(data, file_path):
    max_key_length = find_longest_key_length(data)
    with open(file_path, 'w') as f:
        for key, value in data.items():
            f.write(f"@{value['type']}" + '{' + f'{key},\n')
            for field_key, field_value in value.items():
                if field_key != 'type':
                    spaces = ' ' * (max_key_length - len(field_key))
                    f.write(f'  {field_key} {spaces}= {{{field_value}}},\n')
            f.write('}\n')
            f.write('\n')

def find_longest_key_length(d):
    max_length = 0
    for inner_dict in d.values():
        for key in inner_dict.keys():
            if len(key) > max_length:
                max_length = len(key)
    return max_length

if __name__ == '__main__':
    # get all bib files in folder
    file_names = glob.glob(bib_folder+'*.bib')

    # sort from newest to oldest
    file_names.sort(key=os.path.getmtime, reverse=True)

    # read bib files
    file_dicts = [parse_file(file_name) for file_name in file_names]

    # merge dictionnaries from all read files
    merged_dict = merge_dictlist(file_dicts, merge_entries)

    # write merged bibtex file
    write_to_file(merged_dict, './merged.bib')
