import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import sys

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        #self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:postGres*44@localhost:5432/trivia_test'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        try:
            res = self.client().get('/questions')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['total_questions'])
            self.assertTrue(len(data['questions']))

            print('test_get_paginated_questions(): PASS')
        except:
            print('test_get_paginated_questions(): FAIL')
            print(sys.exc_info())
    
    def test_404_if_question_does_not_exist(self):
        try:
            res = self.client().delete('/question/1')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)

            print('test_404_if_question_does_not_exist(): PASS')
        except:
            print('test_404_if_question_does_not_exist(): FAIL')
            print(sys.exc_info())
        

    def test_delete_question(self):
        try:
            res = self.client().delete('/questions/23')
            data = json.loads(res.data)

            question = Question.query.filter(Question.id == 23).one_or_none()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(question, None)

            print('test_delete_question(): PASS')
        except:
            print('test_delete_question(): FAIL')
            print(sys.exc_info())

    def test_create_new_question(self):
        try:
            res = self.client().post('/add', json={'question':'fake question',
                                'answer':'fake answer',
                                'category':'1',
                                'difficulty':'1'})
            data = json.loads(res.data)

            question = Question.query.filter(Question.id == 24).one_or_none()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertIsNotNone(question)

            print('test_create_new_question(): PASS')
        except:
            print('test_create_new_question(): FAIL')
            print(sys.exc_info())

    def test_422_if_question_creation_fails(self):
        try:
            #note: key is questions not question
            res = self.client().post('/add', json={'questions':'fake question',
                                'answer':'fake answer',
                                'category':'1',
                                'difficulty':'1'})
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 422)
            self.assertEqual(data['success'], False)
            print('test_422_if_question_creation_fails(): PASS')
        except:
            print('test_422_if_question_creation_fails(): FAIL')
            print(sys.exc_info())


    def test_get_categories(self):
        try:
            res = self.client().get('/categories')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['categories'])
            self.assertTrue(len(data['categories']))

            print('test_get_categories(): PASS')
        except:
            print('test_get_categories(): FAIL')
            print(sys.exc_info())

    def test_questions_search(self):
        try:
            res = self.client().post('/questions', json={'searchTerm':'What'})
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['total_questions'], 8)

            print('test_questions_search(): PASS')
        except:
            print('test_questions_search(): FAIL')
            print(sys.exc_info())

    def test_get_by_category(self):
        try:
            res = self.client().get('/categories/1/questions')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            self.assertTrue(len(data['questions']))
            self.assertEqual(len(data['questions']), 3)

            print('test_get_by_category(): PASS')
        except:
            print('test_get_by_category(): FAIL')
            print(sys.exc_info())

    def test_404_if_category_does_not_exist(self):
        try:
            res = self.client().get('/categories/99/questions')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)

            print('test_404_if_category_does_not_exist(): PASS')
        except:
            print('test_404_if_category_does_not_exist(): FAIL')
            print(sys.exc_info())


    def test_play(self):
        json_data ={'previous_questions':[{'question':'fake question', 'answer':'fake answer',
                    'category':'1', 'difficulty':'1'}],
                    'quiz_category':{'id':'1', 'type':'Science'},
                    'guess':'fake'}
        try:
            res = self.client().post('/quizzes', json=json_data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['question'])

            print('test_play(): PASS')
        except:
            print('test_play(): FAIL')
            print(sys.exc_info())

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()