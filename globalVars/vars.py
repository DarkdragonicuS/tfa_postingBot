import csv

def tagCategories():

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

tagByCategory = tagCategories()
TAG_SPECIES = tagByCategory['species']