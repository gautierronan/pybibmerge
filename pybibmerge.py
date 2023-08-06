import glob
import os
import re

bib_folder = './bibfiles/'

def parse_file(file_path):
    """Parses a BibTeX file and returns a dictionary of its entries.

    Args:
        file_path (str): The path to the BibTeX file.

    Returns:
        dict: A dictionary of the BibTeX file's entries, where each key is the entry's
            key and each value is a dictionary of the entry's fields.
    """
    entries = {}
    with open(file_path, 'r') as file:
        content = file.read()

    # parse entries with a key
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

    # parse entries without a key
    pattern_entry = r"@(\w+)\{[^\w]+\s*([^@]+)\}"
    matches = re.findall(pattern_entry, content, re.MULTILINE)

    for match in matches:
        entry_type = match[0]
        pattern_fields = r"(\w+)\s*=\s*{(.+)}"
        fields = re.findall(pattern_fields, match[1], re.MULTILINE)
        entry = {
            'type': entry_type,
        }
        for key, field in fields:
            entry[key.strip()] = field.strip()

        # generate key if possible
        entry_key = ''
        if 'author' in entry:
            entry_key += entry['author'].split(',')[0].split(' ')[0].lower()
        if 'year' in entry:
            entry_key += entry['year']
        if 'title' in entry:
            entry_key += entry['title'].split(' ')[0].lower()
        if 'author' not in entry and 'title' not in entry:
            raise Exception('A key cannot be generated for an entry because it does not have an author nor a title.')

        entries[entry_key] = entry

    return entries


def merge_dict_list(dicts, merge_values):
    """Merges a list of dictionaries into a single dictionary.

    Args:
        dicts (list): A list of dictionaries to merge.
        merge_values (function): A function that takes two values and returns the
            merged value.

    Returns:
        dict: A dictionary that is the result of merging all the input dictionaries.
    """
    merged_dict = {}
    for d in dicts:
        for key, value in d.items():
            if key in merged_dict:
                merged_dict[key] = merge_values(merged_dict[key], value)
            else:
                merged_dict[key] = value
    return merged_dict


def merge_entries(dict1, dict2):
    """Merges two BibTeX entries into a single entry.

    Args:
        dict1 (dict): The first BibTeX entry to merge.
        dict2 (dict): The second BibTeX entry to merge.

    Returns:
        dict: A dictionary that is the result of merging the two input BibTeX entries.
    """
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
    """Writes a dictionary of BibTeX entries to a file.

    Args:
        data (dict): A dictionary of BibTeX entries to write to the file.
        file_path (str): The path to the file to write to.
    """
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
    """Finds the length of the longest key in a dictionary of BibTeX entries.

    Args:
        d (dict): A dictionary of BibTeX entries.

    Returns:
        int: The length of the longest key in the input dictionary.
    """
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
    merged_dict = merge_dict_list(file_dicts, merge_entries)

    # write merged bibtex file
    write_to_file(merged_dict, './merged.bib')
