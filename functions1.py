import requests
import urllib.parse, urllib.request, urllib.error, json
from flask import Flask

def get_recipe(query, time):
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch?number=5&maxReadyTime={}".format(time)

    query_string = {"query": query}
    headers = {
	            "X-RapidAPI-Key": "API KEY",
	             "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
                }
    response = requests.get(url, headers=headers, params=query_string)
    recipe = response.json()
    return (recipe)

def get_ingredients(query):
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{}/ingredientWidget.json".format(query)
    headers = {
	    "X-RapidAPI-Key": "API KEY",
	    "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    x = response.json()
    return (x)

def get_recipe_info_dict(id):
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{}/information".format(id)

    headers = {
	    "X-RapidAPI-Key": "API KEY",
	    "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    x = response.json()
    return(x)

def rrrecipe_info(input_dict):
    new_dict = {}
    new_dict["title"] = input_dict["title"]
    new_dict["servings"] = input_dict["servings"]
    new_dict["prepare"] = input_dict["readyInMinutes"]
    new_dict["image"] = input_dict["image"]
    new_dict["source"] = input_dict["sourceUrl"]
    return(new_dict)


def get_usuable_ingredient_dict(ingredient_dict):
    ingred_list = []
    usable_dict = {}
    ingreds = ingredient_dict["ingredients"]
    for item in ingreds:
        name = item["name"]
        value = item["amount"]["metric"]["value"]
        unit = item["amount"]["metric"]["unit"]
        item_string = str(value) + " " + unit + " " + name
        ingred_list.append(item_string)
    usable_dict["ingredients"] = ingred_list
    return (usable_dict)


def ingredient_amounts(ingred_list):
    url = "https://zestful.p.rapidapi.com/parseIngredients"

    headers = {
	    "content-type": "application/json",
	    "X-RapidAPI-Key": "API KEY",
	    "X-RapidAPI-Host": "zestful.p.rapidapi.com"
    }

    response = requests.post(url, json=ingred_list, headers=headers)

    return response.json()



def grocery_list(groceries,ingred_amounts):
    for item in ingred_amounts["results"]:
        specifics = item["ingredientParsed"]
        food_type = specifics["product"]
        quantity = specifics["quantity"]
        unit = specifics["unit"]
        condensed = conversion_check(round(quantity,2), unit)
        if food_type not in groceries.keys():
            amount = condensed
        else:
            current_quan = groceries[food_type][0]
            current_unit = groceries[food_type][1]
            amount = combining(current_quan, current_unit, condensed[0], condensed[1])
        groceries[food_type] = amount
    return groceries


def combining(quantity1, unit1, quantity2, unit2):
    if unit1 == unit2:
        total_quan = round(quantity1 + quantity2, 2)
        total_unit = unit1
        amount = [total_quan, total_unit]
    else:
        quan1 = round(quantity1, 2)
        quan2 = round(quantity2, 2)
        if unit1 not in size_chart or unit2 not in size_chart:
            amount = [quan1, unit1, quan2, unit2]
        else: 
            location_1 = size_chart.index(unit1)
            location_2 = size_chart.index(unit2)
            if location_1 < location_2:
                amount = [quan1, unit1, quan2, unit2]
            else:
                amount = [quan2, unit2, quan1, unit1]
    return amount


def conversion_check(quan, unit):
    if unit == "teaspoon":
        if quan >= 3:
            teas = quan % 3
            table = (quan - teas) / 3
            if teas == 0:
                return [table, "tablespoon"]
            else:
                return [table, "tablespoon", teas, unit]
        else:
            return [quan, unit]
    elif unit == "tablespoon":
        if quan >= 16:
            table = quan % 16
            cup = (quan - table) / 16
            if table == 0:
                return [cup, "cup"]
            elif table == 4:
                return [cup + .25, "cup"]
            elif table == 8:
                return [cup + .5, "cup"]
            elif table == 12:
                return [ cup + .75, "cup"]
            else:
                return [cup, "cup", table, unit]
        else:
            return [quan, unit]
    else:
        return [quan, unit]


size_chart = ["package", "serving", "cup", "milliliter", "tablespoon", "teaspoon"]


def final(total_ingred):
    total_groceries = []
    total_ingredients = {}
    for lst in total_ingred:
        ingred_amounts = ingredient_amounts(lst)
        groceries = grocery_list(total_ingredients,ingred_amounts)
        total_ingredients = groceries
    for item in total_ingredients.keys():
        length_units = len(total_ingredients[item])
        for units in range(1, length_units + 1, 2):
            if total_ingredients[item][units - 1] > 1:
                total_ingredients[item][units] = str(total_ingredients[item][units]) + "s"
            if total_ingredients[item][units - 1] < 1:
                total_ingredients[item][units] = str(total_ingredients[item][units]) + "s"
            label_amounts = ""
            if length_units == 2:
                if total_ingredients[item][1] is None or total_ingredients[item][1] == "Nones":
                    label_amounts = str(total_ingredients[item][0]) + " "
                else: 
                    label_amounts = str(total_ingredients[item][0]) + " " + str(total_ingredients[item][1]) + " "
            else:
                for num in range(0, length_units, 2):
                    if total_ingredients[item][num + 1] is None or total_ingredients[item][num + 1] == "Nones":
                        label_amounts = label_amounts + str(total_ingredients[item][num]) + " and "
                    else: 
                        label_amounts = label_amounts + str(total_ingredients[item][num]) + " " + total_ingredients[item][num + 1] + " "
            label = label_amounts + item
        total_groceries.append(label)
    return(total_groceries)

