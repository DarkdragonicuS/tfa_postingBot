# Copyright (C) 2024 Nixiris Dartero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import csv

def tag_categories():

    # Initialize an empty dictionary to store tags by category
    species = []
    characters = []
    general = []
    general_mapping = {
        'young': 'cub',
        'male/male': 'gay',
        'male/female': 'straight',
        'female/female': 'lesbian',
        'solo': 'solo',
        'duo': 'duo',
        'group': 'group',
        'anthro': 'anthro',
        'feral': 'feral',
        'male': 'male',
        'female': 'female',
        'intersex': 'intersex',
        'herm': 'herm',
        'comic': 'comix',
        'domestic_dog': 'dog',
        'domestic_cat': 'cat',
        'digimon_species': 'digimon',
        'pokemon_(species)': 'pokemon',
        'urine': 'urine',
        'feces': 'feces'
    }
    tags_order = [
                  ('urine','feces'),
                  ('cub'),
                  ('human'),
                  ('gay','straight','lesbian'),
                  ('solo','duo','group'),
                  ('male','female','intersex','herm'),
                  ('anthro','feral'),
                ]
    # Read the CSV file
    with open('global_vars/tags.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        #rowNum = 0
        for row in reader:
        #    rowNum += 1
        #    print(rowNum)

            category = row['category']
            tag = row['name']
            
            # Add the tag to the corresponding category list
            if category == '5':
                species.append(tag)
            if category == '4':
                characters.append(tag)
            if category == '0':
                general.append(tag)
    return {"species": species, "characters": characters, "general": general, 'general_mapping': general_mapping}

def tag_synonyms():
    #TODO add more
    main_tags = ['pokemon','dog','cat','digimon','dragon']

    synonyms = {}
    with open('global_vars/tag_synonyms.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            consequent_name = row['consequent_name']
            antecedent_name = row['antecedent_name']
            if consequent_name in main_tags:
                if antecedent_name in synonyms:
                    synonyms[antecedent_name].append(consequent_name)
                else:
                    synonyms[antecedent_name] = [consequent_name]
    synonyms = dict(sorted(synonyms.items()))
    return synonyms

def tag_implications():
    #TODO add more
    main_tags = ['pokemon','dog','cat','digimon','dragon']

    implications = {}
    with open('global_vars/tag_implications.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            consequent_name = row['consequent_name']
            antecedent_name = row['antecedent_name']
            if consequent_name in main_tags:
                if antecedent_name in implications:
                    implications[antecedent_name].append(consequent_name)
                else:
                    implications[antecedent_name] = [consequent_name]
    implications = dict(sorted(implications.items()))
    return implications

tag_by_category = tag_categories()
TAG_SPECIES = tag_by_category['species']
TAG_CHARACTERS = tag_by_category['characters']
TAG_GENERAL = tag_by_category['general']
TAG_GENERAL_MAPPING = tag_by_category['general_mapping']
TAG_SYNONYMS = tag_synonyms()
TAG_IMPLICATIONS = tag_implications()
TAG_META = ['comix']
TAG_SPOILERED = ['urine','feces','cub','human']
TAGS_ORDER = TAG_SPOILERED + ['gay','straight','lesbian','solo','duo','group','male','female','intersex','herm','anthro','feral'] + TAG_SPECIES + TAG_CHARACTERS + TAG_META