from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db
from sqlalchemy import cast, Integer

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)
  
    with app.app_context():
        db.create_all()
        
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    def formatted_categories(selection):
        if not selection:
            return {}
        formated_categories = {category.id: category.type for category in selection}

        return formated_categories
    
    @app.route("/categories")
    
    def retrieve_categories():
       
        categories=Category.query.all()
        categories = formatted_categories(categories)
    

            
        return jsonify(
            {
                "success": True,
                "categories":categories,
            }
        ) 
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    
    
    
    QUESTIONS_PER_QUERY = 10
    
    def paginate_questions(request, selection):
        if not selection:
            return []
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_QUERY
        end = start + QUESTIONS_PER_QUERY

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    
    @app.route("/questions", methods=["GET"])
    def retrieve_questions_with_categories():

        selection = Question.query.outerjoin(Category, Category.id == cast(Question.category, Integer)).all()
        current_questions = paginate_questions(request, selection)

        categories = formatted_categories(Category.query.all())
        
        return jsonify({
          "success": True,
          "questions": current_questions,
          "total_questions": len(selection),
          "categories": categories,
          "current_category": None
      })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions', methods=['POST'])
    def search_questions(category_id):
        body = request.get_json()
        
        if not body:
            abort(400, description="Missing JSON body")
        
        search_term = body.get("searchTerm", None)
        
        if search_term:
            data= Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
            current_questions = paginate_questions(request, data)
            
        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(data),
            "current_category": category_id
      })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def retrive_questions_from_category(category_id):
        questions_query = Question.query.outerjoin(Category, Category.id == cast(Question.category, Integer)).filter(Category.id == category_id).all()
        
        current_questions = paginate_questions(request, questions_query)
       
        return jsonify({
          "success": True,
          "questions": current_questions,
          "total_questions": len(questions_query),
          "current_category": category_id
      })
    
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": str(error.description)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        "success": False,
        "error": 404,
        "message":"Not Found"    
        }),404
    
    @app.errorhandler(422)
    def unprocesable(error):
        return jsonify({
        "success": False,
        "error": 422,
        "message":"Unprocessable Content"    
        }),422
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405
    return app

