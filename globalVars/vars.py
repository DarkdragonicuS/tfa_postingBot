import csv

def tag_categories():

    # Initialize an empty dictionary to store tags by category
    species = []

    # Read the CSV file
    with open('globalvars/tags.csv', 'r', encoding='utf-8') as csvfile:
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
    return {"species": species}

tag_by_category = tag_categories()
TAG_SPECIES = tag_by_category['species']