import os
# from tkinter.messagebox import NO
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {"question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?", "answer": "Maya Angelou", "category": 4,"difficulty":5}
        
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

        
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["categories"]))
    
    
    def test_get_paginated_question(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))
        
    def test_fail_paginated_question(self):
        res = self.client().get("/questions?page=1501")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        
        
    def test_delete_question(self):
        
        res = self.client().delete("/questions/4")
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 4).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 4)        
        self.assertEqual(question, None)
    
    def test_fail_delete_question(self):
        
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 10000).one_or_none()
        if question is None:
            self.assertEqual(res.status_code, 422)
            self.assertEqual(data["success"], False)
        
    
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        
    def test_create_question_with_no_data(self):
        """Test for ensuring data with empty fields are not processed."""
        request_data = {
            'question': '',
            'answer': '',
            'difficulty': '',
            'category':'',
        }

        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
    def test_post_questions_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "Tom Hanks"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        
        self.assertEqual(len(data["questions"]), 1)
        
    def test_post_questions_search_no_results(self):
        res = self.client().post("/questions", json={"searchTerm": "George Washington"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertFalse(data["totalQuestions"])
        self.assertEqual(len(data["questions"]), 0)
        
    def test_fail_search_term_response(self):
           
        request_data = {'searchTerm': ''}

        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data) 
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
        
    
    def test_get_category_questions(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))
        
       
    def test_post_quizz(self):
        res = self.client().post("/quizzes", json={
                                                'previous_questions': [1],
                                                'quiz_category': 'Entertainment'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        
    def test_fail_post_quizz(self):
        res = self.client().post("/quizzes", json={ })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        
         

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()