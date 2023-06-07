from bson import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

def get_mongodb_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['cgp']
    return db

app = Flask(__name__)
db = get_mongodb_connection()
analytics_collection = db['analytics']
recipes_collection = db["recipes"]
arts_collection = db['arts']

def save_to_analytics_db(raw_prompt, additional_inputs, engineered_prompt, generated_content_id, content_type):

    document = {
        'raw_prompt': raw_prompt,
        'additional_inputs': additional_inputs,
        'engineered_prompt': engineered_prompt,
        'generated_content_id': generated_content_id,
        'content_type': content_type,
        'timestamp': datetime.now()
    }

    result = analytics_collection.insert_one(document)
    document_id = result.inserted_id

    return document_id


@app.route('/generate_art', methods=['POST'])
def generate_art():
    raw_prompt = request.json['raw_prompt']
    additional_inputs = request.json['additional_inputs']
    engineered_prompt = refine_art_prompt(raw_prompt, additional_inputs)
    art_id = generate_art_from_GAI(engineered_prompt)
    document_id = save_to_analytics_db(raw_prompt, additional_inputs, engineered_prompt, art_id, 'art')
    response = {
        'document_id': str(document_id),
        'generated_content_id': str(art_id)
    }
    return jsonify(response)


@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    raw_prompt = request.json['raw_prompt']
    additional_inputs = request.json['additional_inputs']
    engineered_prompt = refine_recipe_prompt(raw_prompt, additional_inputs)
    recipe_id = generate_recipe_from_GAI(engineered_prompt)
    document_id = save_to_analytics_db(raw_prompt, additional_inputs, engineered_prompt, recipe_id, 'recipe')
    response = {
         'document_id': str(document_id),
        'generated_content_id': str(recipe_id)
    }
    return jsonify(response)


def refine_recipe_prompt(raw_prompt,     additional_inputs):
    cuisine = additional_inputs.get('cuisine')
    dietary_restrictions = additional_inputs.get('dietary_restrictions')
    cooking_time = additional_inputs.get('cooking_time')
    skill_level = additional_inputs.get('skill_level')
    ingredients = additional_inputs.get('ingredients')
    flavors = additional_inputs.get('flavors')
    occasion = additional_inputs.get('occasion')
    serving_size = additional_inputs.get('serving_size')

    engineered_prompt = f"Generate a {cuisine} recipe"

    if dietary_restrictions:
        engineered_prompt += f" that is {dietary_restrictions}"

    if cooking_time:
        engineered_prompt += f" and can be prepared in {cooking_time}"

    if skill_level:
        engineered_prompt += f" suitable for {skill_level} cooks"

    if ingredients:
        engineered_prompt += f" using the following ingredients: {', '.join(ingredients)}"

    if flavors:
        engineered_prompt += f" with {flavors} flavors"

    if occasion:
        engineered_prompt += f" perfect for {occasion}"

    if serving_size:
        engineered_prompt += f" that serves {serving_size}"

    return engineered_prompt


def refine_art_prompt(raw_prompt, additional_inputs):
    # Extract the additional input parameters
    style = additional_inputs.get('style', '')
    color_palette = additional_inputs.get('color_palette', '')
    subject = additional_inputs.get('subject', '')
    composition = additional_inputs.get('composition', '')
    brushwork = additional_inputs.get('brushwork', '')
    medium = additional_inputs.get('medium', '')
    emotion = additional_inputs.get('emotion', '')

    # Construct the engineered prompt using the additional input parameters
    engineered_prompt = f"Art Prompt: {raw_prompt}\n\nAdditional Inputs:\n"
    engineered_prompt += f"- Style: {style}\n"
    engineered_prompt += f"- Color Palette: {color_palette}\n"
    engineered_prompt += f"- Subject: {subject}\n"
    engineered_prompt += f"- Composition: {composition}\n"
    engineered_prompt += f"- Brushwork: {brushwork}\n"
    engineered_prompt += f"- Medium: {medium}\n"
    engineered_prompt += f"- Emotion: {emotion}\n"

    return engineered_prompt


def generate_recipe_from_GAI(engineered_prompt):
    recipe_name = "Delicious Recipe"
    ingredients = ["Ingredient 1", "Ingredient 2", "Ingredient 3"]
    steps = ["Step 1", "Step 2", "Step 3"]

    # Save the generated recipe in the "recipes" collection
    recipe = {
        'recipe_name': recipe_name,
        'ingredients': ingredients,
        'steps': steps,
        'timestamp': datetime.now()
    }
    recipe_id = recipes_collection.insert_one(recipe).inserted_id
    return recipe_id


def generate_art_from_GAI(engineered_prompt):
    # Implement your logic to call the generative AI service/API and generate an image
    # This can involve making HTTP requests, authenticating, and handling the response
    # Modify this function according to your specific requirements
    # Assuming the generative AI service returns the URL of the generated image
    image_urls = ['generated_image_url1', 'generated_image_url2']  # Example array of image URLs
    art = {
        'image_urls': image_urls,
        'timestamp': datetime.now()
    }
    art_id = arts_collection.insert_one(art).inserted_id
    return art_id

@app.route('/analytics/<content_type>', methods=['GET'])
def get_documents_by_content_type(content_type):
    documents = analytics_collection.find({"content_type": content_type})
    results = []
    for document in documents:
        result = {
            'document_id': str(document['_id']),
            'raw_prompt': document['raw_prompt'],
            'additional_inputs': document['additional_inputs'],
            'engineered_prompt': document['engineered_prompt'],
            'generated_content_id': str(document['generated_content_id']),
            'content_type': document['content_type'],
            'timestamp': document['timestamp']
        }

        if 'feedback' in document:
            result['feedback'] = document['feedback']

        results.append(result)

    return jsonify(results)

@app.route('/analytics/<content_type>', methods=['DELETE'])
def delete_documents_by_content_type(content_type):
    result = analytics_collection.delete_many({"content_type": content_type})
    deleted_count = result.deleted_count
    response = {
        "message": f"Deleted {deleted_count} documents with content type '{content_type}'",
        "deleted_count": deleted_count
    }
    return jsonify(response)

@app.route('/analytics/feedback', methods=['POST'])
def add_feedback():
    generated_content_id = request.json['generated_content_id']
    relevance = request.json['relevance']
    emotions = request.json['emotions']
    additional_comment = request.json['additional_comment']

    result = analytics_collection.update_one(
        {"generated_content_id": ObjectId(generated_content_id)},
        {"$set": {
            "feedback": {
                "relevance": relevance,
                "emotions": emotions,
                "additional_comment": additional_comment
            }
        }}
    )

    if result.modified_count > 0:
        response = {"message": "Feedback added successfully"}
    else:
        response = {"message": "Failed to add feedback"}

    return jsonify(response)

@app.route('/analytics', methods=['DELETE'])
def delete_all_documents():
    result = analytics_collection.delete_many({})
    deleted_count = result.deleted_count

    response = {
        'message': f'Deleted {deleted_count} documents from the "analytics" collection'
    }

    return jsonify(response)

@app.route('/arts', methods=['GET'])
def get_all_arts():
    arts = list(arts_collection.find({}))
    results = []
    for art in arts:
        result = {
            'art_id': str(art['_id']),
            'image_urls': art['image_urls'],
            'timestamp': art['timestamp']
        }
        results.append(result)

    return jsonify(results)


@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    recipes = recipes_collection.find()

    # Create a list to store the recipe data
    recipe_list = []

    # Iterate over the recipes and extract the relevant information
    for recipe in recipes:
        recipe_data = {
            'recipe_id': str(recipe['_id']),
            'recipe_name': recipe['recipe_name'],
            'ingredients': recipe['ingredients'],
            'steps': recipe['steps']
        }
        recipe_list.append(recipe_data)

    return jsonify(recipe_list)

if __name__ == '__main__':
    app.run(debug=True)
