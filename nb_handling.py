#!/usr/bin/env python

import os
import fire
import json

def nbmerge(load='', cleansing=None, transform=None, train=None, output="nbmerge.ipynb"):
    if os.path.isfile(load):
        nb_list = []
        make_nb_list(cleansing, load, nb_list, train, transform)
        combined_nb = generated_combined_nb(nb_list)
        with open(output, mode='w', encoding='utf-8') as f:
            json.dump(combined_nb, f)
    else:
        print("load is a required parameter")


def generated_combined_nb(nb_list):
    for i, notebook in enumerate(nb_list):
        with open(notebook, mode='r', encoding='utf-8') as nb:
            sub_nb = json.load(nb)
            if i == 0:
                combined_nb = sub_nb
            else:
                ## start to combine stages
                current_output_variable = extract_variable(combined_nb['cells'][-1])
                next_input_variable = extract_variable(sub_nb['cells'][1])
                if variable_matched(current_output_variable, next_input_variable):
                    combined_nb['cells'].extend(sub_nb['cells'])
                else:
                    next_stage_name = sub_nb['cells'][0]['source'][0]
                    raise Exception(f"Mismatch  at {next_stage_name}")
    return combined_nb

def extract_variable(nb_cell):
    return [ x.strip() for x in nb_cell['source'][0].split(":")[-1].strip().split(",")]

def variable_matched(output_variable, input_variable):
    return set(output_variable) == set(input_variable)


def make_nb_list(cleansing, load, nb_list, train, transform):
    for stage in [load, cleansing, transform, train]:
        if stage:
            nb_list.append(stage)
        else:
            break


def decompose_nb_stages(file_name='', output_folder='', markdown_header='# Stage'):
    current_path = os.getcwd()
    with open(file_name, mode = 'r', encoding='utf-8') as f:
        source_nb = json.load(f)
    first_stage = source_nb['cells'][0]
    nb = initiate_nb(first_stage, source_nb)
    decomposed_nb_file_name = first_stage['source'][0][2:].split(' ')[-1] + '.ipynb'
    output_path = os.path.join(current_path, output_folder, decomposed_nb_file_name)
    for cell in source_nb['cells'][1:]:
        if cell['cell_type'] == 'markdown' and cell['source'][0].startswith(f'{markdown_header}'):
            with open(output_path, mode = 'w', encoding='utf-8') as f:
                print(output_path)
                json.dump(nb, f)
            ## initail nb stage
            decomposed_nb_file_name = cell['source'][0][2:].split(' ')[-1] + '.ipynb'
            output_path = os.path.join(current_path, output_folder, decomposed_nb_file_name)
            nb['cells'] = [cell]
        else:
            nb['cells'].extend([cell])
    with open(output_path, mode = 'w', encoding='utf-8') as f:
        json.dump(nb, f)
    print(output_path)


def initiate_nb(first_stage, source_nb):
    nb = {}
    nb['cells'] = [first_stage]
    nb['metadata'] = source_nb['metadata']
    nb['nbformat'] = 4
    nb['nbformat_minor'] = 2
    return nb


class Cli():

    def __init__(self):
        self.nbmerge = nbmerge
        self.nbdecompose = decompose_nb_stages

if __name__ == '__main__':
    fire.Fire(Cli)