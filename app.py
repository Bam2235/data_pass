import numpy as np
import pandas as pd
from scipy.optimize import linprog
from pandas.io.stata import StataMissingValue
from flask import Flask, render_template, request, jsonify
from opt import parseInputInventory, parseInputRecipe, parseScoreInput, calculate

app = Flask(__name__, template_folder='template')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def get_value():
    #ambil data ingredient, unit cost dan supply
    #Pi = unit cost -> total price dibagi supply yang ada, Ai = total supply
    ingredientList = request.form.getlist('ingredient[]')
    supplyList = request.form.getlist('supply[]')
    priceList = request.form.getlist('price[]')
    df_inventory = parseInputInventory(ingredientList, supplyList, priceList)
    print('===== DF INVENTORY =====')
    
    print(df_inventory)


    #dapatkan semua ingredient product names dari setiap row yang tidak kosong
    ingredientProductNames = []
    totalIngredientRows = int(request.form.get('totalIngredientRows'))

    for i in range(totalIngredientRows):
        currentProductNames = request.form.getlist('ingredientProductName[ingredient-' + str((i+1)) + ']')
        if len(currentProductNames) > 0:
            ingredientProductNames.append(currentProductNames)

    ingredientProductUnits = []
    for i in range(totalIngredientRows):
        currentProductUnit = request.form.getlist('ingredientProductUnit[ingredient-' + str((i+1)) + ']')
        if len(currentProductUnit) > 0:
            ingredientProductUnits.append(currentProductUnit)

    df_recipe = parseInputRecipe(ingredientProductNames, ingredientProductUnits, totalIngredientRows)
    allProductName = list(df_recipe) ## atau df.columns.values.tolist()
    productDictionaryNames = {}
    for i in range(len(allProductName)):
        productDictionaryNames[allProductName[i]] = 0
    print('===== DF RECIPE =====')
    print(df_recipe)

    productScoreList = request.form.getlist('scoreListName[]')
    demandScoreList = request.form.getlist('demand[]')
    minSalesList = request.form.getlist('minimum[]')
    maxSalesList = request.form.getlist('maximum[]')
    
    df_score = parseScoreInput(productScoreList, demandScoreList, minSalesList, maxSalesList);
    print('==== DF SCORE ====')
    print(df_score)
    
    # TODO: 
    result = calculate(df_recipe, df_inventory, df_score)

    for i in range(len(allProductName)):
        productDictionaryNames[i].update(result[i])

    print(productDictionaryNames)


    # 
    # ubah value setiap key dari productDictionaryNames sesuai hasil calculate(result)

    return jsonify(productDictionaryNames)

if __name__ == "__main__":
    app.run()

 