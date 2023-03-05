import json

with open('db.json') as js:
    f = json.load(js)
    for model in f:
        if model['model'] == 'food.ingredient':
            for field in ['protein_value', 'fats_value', 'carbohydrates_value', 'energy_value']:
                if type(model['fields'][field]) == str:
                    if not model['fields'][field]:
                        model['fields'][field] = 0.0
                    else:
                        model['fields'][field] = float(model['fields'][field].replace(',', '.'))

capitals_json = json.dumps(f)

with open("db1.json", "w") as my_file:
    my_file.write(capitals_json)

