import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
import random



from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cros =CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # @app.after_request
    # def after_request(response):
    #     response.headers.add(
    #         "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    #     )
    #     response.headers.add(
    #         "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    #     )
    #     return response

    QUESTIONS_PER_PAGE=10

    def paginate_question(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        
        current_question = questions[start:end]

        return current_question

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """''
    
    @app.route("/categories")
    def retrieve_categories():
        categories_dict={}
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)
        for category in categories:
            categories_dict[category.id]= category.type

        return jsonify(
            {
                "success": True,
                "categories": categories_dict,
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
    {
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 2
    }
  ],
  "totalQuestions": 100,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": "History"
}
    """
    @app.route("/questions")
    def retrieve_question():
        categories_dict = {}
        selection = Question.query.order_by(Question.id).all()
        current_question = paginate_question(request, selection)
        categories = Category.query.order_by(Category.id).all()
        for category in categories:
            categories_dict[category.id]= category.type
        
        
        if len(current_question) == 0:
            abort(404,"resource not found")

        return jsonify({
                "success": True,
                "questions": current_question,
                "category":categories_dict,
                "totalQuestions": len(selection),
                "currentCategory": None
            }
        )
        


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404,"resource not found")

            question.delete()
            # selection = Question.query.order_by(Question.id).all()
            # current_question = paginate_question(request, selection)

            return jsonify(
                { "success": True,
                "deleted": question_id,}
            )
        except:
            abort(422,"unprocessable")

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        
        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)
        
        try:
            if search:
                
                selection = Question.query.filter(
                    Question.question.ilike("%{}%".format(search))
                ).all()
                
                questions = paginate_question(request, selection)
                
                return jsonify(
                    {
                        "success": True,
                        "questions": questions,
                        "totalQuestions": len(selection),
                        "currentCategory": None
                    }
                )
            else:
                question = Question(question=question, answer=answer, category=category,difficulty=difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_question = paginate_question(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,         
                    }
                )
        except:
            abort(422,"unprocessable")
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    
    
    @app.route("/categories/<int:category_id>/questions")
    def retrieve_questions_cat(category_id):
        
        selection = Question.query.order_by(Question.id).filter_by(category=category_id).all()
        current_category = Category.query.filter_by(id=category_id).first()
        current_questions = paginate_question(request, selection)
       
        try:
            if len(current_questions) == 0:
                abort(404,"resource not found")
        
            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions":len(Question.query.all()),
                    "currentCategory":current_category.type,
                }
            )
        except:
            abort (404,"resource not found")

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
 
    @app.route("/quizzes", methods=["POST"])
    def retrieve_quizzes_question():
        body = request.get_json()
        
        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)
        
        print(quiz_category)
        category = Category.query.filter(Category.type == quiz_category).one_or_none()
        if category is None:
            abort(404,"The category does not exist")
        print(category.type)
        if previous_questions is None:
            previous_questions = []
        questions_category =  Question.query.filter(Question.category== category.id).all()
        print(questions_category)
        questions_category_id = [qc.id for qc in questions_category if qc.id not in previous_questions]
        print(questions_category_id)
        selection = Question.query.filter(Question.id ==random.choice(questions_category_id)).first()
        if selection is None:
            abort(404,"no question found")
        print(selection)
        try:
            if selection:
                
                return jsonify(
                    {    "success": True,
                         "question": {
                                    "id": selection.id,
                                    "question": selection.question,
                                    "answer": selection.answer,
                                    "difficulty": selection.difficulty,
                                    "category": selection.category
                                    }
                    }
                )
            else:
               abort(404,"problem")

        except:
   

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(HTTPException)
    def http_exception_handler(error):
        """
        HTTP error handler for all endpoints
        :param error: HTTPException containing code and description
        :return: error: HTTP status code, message: Error description
        """
        return jsonify({
            'success': False,
            'error': error.code,
            'message': error.description
        }), error.code

    @app.errorhandler(Exception)
    def exception_handler(error):
        """
        Generic error handler for all endpoints
        :param error: Any exception
        :return: error: HTTP status code, message: Error description
        """
        return jsonify({
            'success': False,
            'error': 500,
            'message': f'Something went wrong: {error}'
        }), 500

    return app

