from flask import Flask, render_template, request
from functions1 import get_recipe, get_ingredients, get_usuable_ingredient_dict, final, get_recipe_info_dict, rrrecipe_info 

# Create an instance of Flask
app = Flask(__name__)



# Create a view function for /
@app.route("/")
def recipe_search():
    return render_template("index.html")


# Create a view function for /results
@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    if request.method == "POST":
        time = request.form["cook-time"]
        query = request.form["type"]
        recipes = get_recipe(query, time)
        results = recipes["results"]
        return render_template("recipes.html", query=query, results=results)
    else:
        return "Error: was expecting a POST request", 400


@app.route("/groceries", methods=["GET", "POST"])
def grocery_results():
    if request.method == "POST":
        total_ingredients = []
        for num in range(5):
            key = str(num)
            if key in request.form:
                id = request.form[key]
                ingredients = get_ingredients(id)
                usable_ingreds= get_usuable_ingredient_dict(ingredients)
                total_ingredients.append(usable_ingreds)
        groceries = final(total_ingredients)
        return render_template("groceries.html", groceries=groceries)
    else:
        return "Error: was expecting a POST request", 400
    
@app.route("/info", methods=["GET", "POST"])
def recipe_info():
    if request.method == "POST":
        id = request.form["id"]
        ingredients = get_ingredients(id)
        usable = get_usuable_ingredient_dict(ingredients)
        info_dict = get_recipe_info_dict(id)
        info = rrrecipe_info(info_dict)
        return render_template("info.html", usable=usable, info=info)
    else:
        return "Error: was expecting a POST request", 400
