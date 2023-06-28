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
stories_collection = db['stories']

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
        'documenqt_id': str(document_id),
        'generated_content_id': str(art_id)
    }
    return jsonify(response)

@app.route('/generate_story', methods=['POST'])
def generate_story():
    raw_prompt = request.json['raw_prompt']
    additional_inputs = request.json['additional_inputs']
    engineered_prompt = refine_story_prompt(raw_prompt, additional_inputs)
    story_id = generate_story_from_GAI(engineered_prompt)
    document_id = save_to_analytics_db(raw_prompt, additional_inputs, engineered_prompt, story_id, 'story')
    response = {
        'document_id': str(document_id),
        'generated_content_id': str(story_id)
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

def refine_story_prompt(raw_prompt, additional_inputs):
    genre = additional_inputs.get('genre')
    protagonist = additional_inputs.get('protagonist')
    setting = additional_inputs.get('setting')
    plot_points = additional_inputs.get('plot_points')
    theme = additional_inputs.get('theme')

    engineered_prompt = f"Write a {genre} story"

    if protagonist:
        engineered_prompt += f" with a {protagonist} as the main character"

    if setting:
        engineered_prompt += f" set in {setting}"

    if plot_points:
        engineered_prompt += f" that includes the following plot points: {', '.join(plot_points)}"

    if theme:
        engineered_prompt += f" with the theme of {theme}"

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

def update_story_with_image_url(story_id, image_url):
    # Retrieve the story document from the database based on the story_id
    story = stories_collection.find_one({'_id': story_id})

    if story:
        # Update the image_url field in the story document
        story['image_url'] = image_url

        # Save the updated story document back to the database
        stories_collection.replace_one({'_id': story_id}, story)

        return True  # Return True to indicate successful update

    return False  # Return False if the story document was not found


def generate_engineered_prompt_for_image(story_data):
    title = story_data.get('title')
    genre = story_data.get('genre')
    setting = story_data.get('setting')
    characters = story_data.get('characters')
    key_elements = story_data.get('key_elements')

    engineered_prompt = f"Generate an image for a {genre} story"
    if title:
        engineered_prompt += f" titled '{title}'"

    if setting:
        engineered_prompt += f" set in {setting}"

    if characters:
        engineered_prompt += f" featuring {', '.join(characters)}"

    if key_elements:
        engineered_prompt += f" with key elements: {', '.join(key_elements)}"

    return engineered_prompt


def generate_image_from_GAI(engineered_prompt):
    # Placeholder code for generating an image using the engineered prompt
    # Your implementation for generating the image URL based on the engineered prompt goes here
    image_url = "https://example.com/image.jpg"
    return image_url


def generate_story_from_GAI(engineered_prompt):
    story_content = "Once upon a time, in a land far away..."
    author = "John Doe"
    genre = "Fantasy"
    likes_count = 0
    hashtags = ["storytelling", "fantasy"]
    published = True
    author_username = "johndoe123"
    timestamp = datetime.now()

    engineered_prompt = generate_engineered_prompt_for_image()
    image_url = generate_image_from_GAI(engineered_prompt)

    # Save the generated story in the "stories" collection
    story = {
        'story_content': story_content,
        'author': author,
        'image_url': image_url,
        'genre': genre,
        'likes_count': likes_count,
        'hashtags': hashtags,
        'published': published,
        'author_username': author_username,
        'timestamp': timestamp
    }
    story_id = stories_collection.insert_one(story).inserted_id
    return story_id, image_url


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

from flask import Flask, jsonify, request
import os
import sys
import subprocess

app = Flask(__name__)

@app.route('/api/environment', methods=['GET', 'PUT'])
def switch_environment():
    if request.method == 'GET':
        return jsonify({'environment': os.environ.get('FLASK_ENV', 'unknown')})

    if request.method == 'PUT':
        new_environment = request.json.get('environment')

        if new_environment:
            os.environ['FLASK_ENV'] = new_environment

            # Restart the Flask app
            args = [sys.executable] + sys.argv
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sys.exit()

        return jsonify({'error': 'Invalid request'}), 400

@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
