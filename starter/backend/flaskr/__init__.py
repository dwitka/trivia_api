import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route
    # after completing the TODOs
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    def paginate_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        formatted_questions = [question.format() for question in questions]
        current_questions = formatted_questions[start:end]

        return current_questions

    # @TODO: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # @TODO: Create an endpoint to handle GET
    # requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def getCategories():
        category_list = []
        try:
            categories = Category.query.all()
            formatted_categories = [
              category.format() for category in categories]
            for item in formatted_categories:
                category_list.append(item['type'])
            return jsonify({'success': True, 'categories': category_list})
        except Exception:
            abort(422)

    # @TODO: Create an endpoint to handle GET requests for questions, including
    # pagination (every 10 questions). This endpoint should return a list of
    # questions, number of total questions, current category, categories. TEST:
    # At this point, when you start the application you should see questions
    # and categories generated, ten questions per page and pagination at the
    # bottom of the screen for three pages. Clicking on the page numbers should
    # update the questions.
    @app.route('/questions', methods=['GET'])
    def getQuestions(category_id=None):
        if category_id is None:
            category = None
            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            questions = formatted_questions[:]
        else:
            category = Category.query.get(category_id).type
            questions = Question.query.filter(
              Question.category == category_id).all()
            questions = paginate_questions(request, questions)
        return jsonify({'questions': questions,
                        'total_questions': len(questions),
                        'current_category': category,
                        'categories': getCategories().json['categories']})

    # @TODO: Create an endpoint to DELETE question using a question ID. TEST:
    # When you click the trash icon next to a question, the question will be
    # removed. This removal will persist in the database and when you refresh
    # the page.
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def deleteQuestion(question_id):
        question = Question.query.filter(
          Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            try:
                question.delete()
            except Exception:
                abort(422)
        return jsonify({'success': True})

    # @TODO: Create an endpoint to POST a new question, which will require the
    # question and answer text, category, and difficulty score. TEST: When you
    # submit a question on the "Add" tab, the form will clear and the question
    # will appear at the end of the last page of the questions list in the
    # "List" tab.
    @app.route('/add', methods=['POST'])
    def createQuestion():
        try:
            data = request.get_json()
            if len(data['question']) == 0 or len(data['answer']) == 0:
                abort(422)
            else:
                pass
            category = int(data['category']) + 1
            new_question = Question(data['question'],
                                    data['answer'],
                                    category,
                                    data['difficulty'])
            new_question.insert()
            return jsonify({'success': True})
        except Exception:
            abort(422)

    # @TODO: Create a POST endpoint to get questions based on a search term. It
    # should return any questions for whom the search term is a substring of
    # the question. TEST: Search by any phrase. The questions list will update
    # to include only questions that include that string within their question.
    # Try using the word "title" to start.
    @app.route('/questions', methods=['POST'])
    def search():
        question_list = []
        search = request.get_json()
        searchTerm = search['searchTerm']
        questions = getQuestions().json['questions']
        for item in questions:
            if str.lower(searchTerm) in str.lower(item['question']):
                question_list.append(item)
            else:
                pass
        return jsonify({'questions': question_list,
                        'total_questions': len(question_list),
                        'current_category': None})

    # @TODO: Create a GET endpoint to get questions based on category. TEST: In
    # the "List" tab / main screen, clicking on one of the categories in the
    # left column will cause only questions of that category to be shown.
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def getByCategory(category_id):
        try:
            questions = getQuestions(category_id).json['questions']
            category = Category.query.get(category_id).type
            return jsonify({'success': True,
                            'questions': questions,
                            'total_questions': len(questions),
                            'current_category': category})
        except Exception:
            abort(404)

    # @TODO: Create a POST endpoint to get questions to play the quiz. This
    # endpoint should take category and previous question parameters and return
    # a random questions within the given category, if provided, and that is
    # not one of the previous questions. TEST: In the "Play" tab, after a user
    # selects "All" or a category, one question at a time is displayed, the
    # user is allowed to answer and shown whether they were correct or not.
    @app.route('/quizzes', methods=['POST'])
    def play():
        try:
            data = request.get_json()
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']
            category = quiz_category['id']

            if quiz_category['type'] == 'click':
                questions = getQuestions().json['questions']
            else:
                questions = getByCategory(category).json['questions']

            if len(questions) == len(previous_questions):
                return jsonify({'forceEnd': True})
            else:
                question = random.choice(questions)

            while question['id'] in previous_questions:
                question = random.choice(questions)
            else:
                pass
            return jsonify({'question': question,
                            'guess': data['guess'],
                            'previousQuestions': previous_questions})
        except Exception:
            abort(500)

    # @TODO: Create error handlers for all expected
    # errors including 404 and 422.
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
            }), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "The method is not allowed for the requested URL."
            }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unable to process entity"
            }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
          "success": False,
          "error": 500,
          "message": "Server error"
          }), 500

    return app
