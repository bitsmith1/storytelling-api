from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/storytelling"
mongo = PyMongo(app)


@app.route('/stories', methods=['POST'])
def create_story():
    # Retrieve the data from the request body
    data = request.get_json()

    # Extract the parameters from the data
    title = data.get('title')
    body = data.get('body')
    author = data.get('author')
    date_published = datetime.now()
    image_url = data.get('image_url')
    genre = data.get('genre')
    likes_count = data.get('likes_count')
    hashtags = data.get('hashtags')
    published = data.get('published')
    author_username = data.get('author_username')
    prompt = data.get('prompt')

    # Create a new story document
    story = {
        'title': title,
        'body': body,
        'author': author,
        'date_published': date_published,
        'image_url': image_url,
        'genre': genre,
        'likes_count': likes_count,
        'hashtags': hashtags,
        'published': published,
        'author_username': author_username,
        'prompt': prompt
    }

    # Insert the story into the database
    result = mongo.db.stories.insert_one(story)

    # Retrieve the created story object from the database
    inserted_story = mongo.db.stories.find_one({'_id': result.inserted_id})

    serialized_story = {
        'id': str(inserted_story['_id']),
        'title': inserted_story['title'],
        'body': inserted_story['body'],
        'author': inserted_story['author'],
        'date_published': inserted_story['date_published'].isoformat(),
        'image_url': inserted_story['image_url'],
        'genre': inserted_story['genre'],
        'likes_count': inserted_story['likes_count'],
        'hashtags': inserted_story['hashtags'],
        'published': inserted_story['published'],
        'author_username': inserted_story['author_username'],
        'prompt': inserted_story['prompt']
    }

    response = {
        'message': 'Story created successfully',
        'story': serialized_story,
        'mongodb_object_id': str(inserted_story['_id'])
    }

    return jsonify(response), 201


@app.route('/stories', methods=['GET'])
def get_all_stories():
    # Retrieve all stories from the database
    stories = mongo.db.stories.find()

    serialized_stories = []
    for story in stories:
        serialized_story = {
            'id': str(story['_id']),
            'title': story['title'],
            'body': story['body'],
            'author': story['author'],
            'date_published': story['date_published'].isoformat(),
            'image_url': story['image_url'],
            'genre': story['genre'],
            'likes_count': story['likes_count'],
            'hashtags': story['hashtags'],
            'published': story['published'],
            'author_username': story['author_username'],
            'prompt': story['prompt']
        }
        serialized_stories.append(serialized_story)

    return jsonify(serialized_stories)


@app.route('/stories/<string:story_id>', methods=['GET'])
def get_single_story(story_id):
    # Find the story by its ID
    story = mongo.db.stories.find_one({'_id': ObjectId(story_id)})

    if story:
        # Serialize the story
        serialized_story = {
            'id': str(story['_id']),
            'title': story['title'],
            'body': story['body'],
            'author': story['author'],
            'date_published': story['date_published'].isoformat(),
            'image_url': story['image_url'],
            'genre': story['genre'],
            'likes_count': story['likes_count'],
            'hashtags': story['hashtags'],
            'published': story['published'],
            'author_username': story['author_username'],
            'prompt': story['prompt']
        }

        return jsonify(serialized_story)
    else:
        return jsonify({'message': 'Story not found'}), 404


@app.route('/stories/genre/<string:genre>', methods=['GET'])
def get_stories_by_genre(genre):
    # Retrieve stories of the specified genre from the "stories" collection
    stories = mongo.db.stories.find({'genre': genre}).sort('likes_count', -1)

    # Create a list to store the serialized stories
    serialized_stories = []

    # Serialize each story and add it to the list
    for story in stories:
        serialized_story = {
            'id': str(story['_id']),
            'title': story['title'],
            'body': story['body'],
            'author': story['author'],
            'date_published': story['date_published'].isoformat(),
            'image_url': story['image_url'],
            'genre': story['genre'],
            'likes_count': story['likes_count'],
            'hashtags': story['hashtags'],
            'published': story['published'],
            'author_username': story['author_username'],
            'prompt': story['prompt']
        }
        serialized_stories.append(serialized_story)

    return jsonify(serialized_stories)


@app.route('/stories', methods=['DELETE'])
def delete_all_stories():
    # Delete all stories from the database
    result = mongo.db.stories.delete_many({})

    return jsonify({
        'message': 'All stories deleted successfully',
        'deleted_count': result.deleted_count
    })

@app.route('/stories/<string:story_id>', methods=['DELETE'])
def delete_story(story_id):
    # Find and delete the story by its ID
    result = mongo.db.stories.delete_one({'_id': ObjectId(story_id)})

    if result.deleted_count == 1:
        return jsonify({'message': 'Story deleted successfully'})
    else:
        return jsonify({'message': 'Story not found'}), 404


@app.route('/stories/like/<string:story_id>', methods=['POST'])
def like_story(story_id):
    # Find the story by its ID
    story = mongo.db.stories.find_one({'_id': ObjectId(story_id)})

    if story:
        # Update the likes count
        new_likes_count = story['likes_count'] + 1
        mongo.db.stories.update_one({'_id': ObjectId(story_id)}, {'$set': {'likes_count': new_likes_count}})

        return jsonify({'likes_count': new_likes_count, 'message': 'Story liked successfully'})
    else:
        return jsonify({'message': 'Story not found'}), 404


@app.route('/stories/trending', methods=['GET'])
def get_trending_stories():
    # Retrieve the top 3 stories based on highest likes count
    trending_stories = mongo.db.stories.find().sort('likes_count', -1).limit(3)

    serialized_stories = []
    for story in trending_stories:
        serialized_story = {
            'id': str(story['_id']),
            'title': story['title'],
            'body': story['body'],
            'author': story['author'],
            'date_published': story['date_published'].isoformat(),
            'image_url': story['image_url'],
            'genre': story['genre'],
            'likes_count': story['likes_count'],
            'hashtags': story['hashtags'],
            'published': story['published'],
            'author_username': story['author_username'],
            'prompt': story['prompt']
        }
        serialized_stories.append(serialized_story)

    return jsonify(serialized_stories)

if __name__ == '__main__':
    app.run(debug=True)
