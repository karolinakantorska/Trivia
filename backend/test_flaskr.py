import os
import unittest

from flask import json

from flaskr import create_app
from models import db, Question, Category
from settings import DB_TEST_NAME, DB_TEST_USER, DB_TEST_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = DB_TEST_NAME
        self.database_user = DB_TEST_USER
        self.database_password = DB_TEST_PASSWORD
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.app.testing = True
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()
        

            # Ensure categories exist before tests run
            if not Category.query.all():
                categories = [
                    Category(type="Science"),
                    Category(type="Art"),
                    Category(type="Geography"),
                    Category(type="History"),
                    Category(type="Entertainment"),
                    Category(type="Sports"),
                ]
                db.session.bulk_save_objects(categories)
                db.session.commit()


    def tearDown(self):
        """Executed after each test"""
        """with self.app.app_context():
            db.session.remove()
            #db.drop_all()
            db.session.execute(text("DROP SCHEMA public CASCADE;"))
            db.session.execute(text("CREATE SCHEMA public;"))
            db.session.commit()"""
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client.get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsInstance(data["categories"], dict)

    def test_get_categories_empty_db(self):
        # Remove all categories
        with self.app.app_context():
            db.session.query(Category).delete()
            db.session.commit()

        res = self.client.get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data["categories"], dict)
        self.assertEqual(len(data["categories"]), 0)

    def test_get_paginated_questions(self):

        res = self.client.get("/questions")
        print(res)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsInstance(data["categories"], dict)
        self.assertTrue(data["total_questions"])
        self.assertIsInstance(data["questions"], list)

    def test_post_questions_method_not_allowed(self):

        res = self.client.put("/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 405)
        self.assertFalse(data["success"])
        self.assertIn("Method Not Allowed", data["message"])

    def test_get_questions_from_valid_category(self):
        #Use an existing category dynamically
        with self.app.app_context():
            category = Category.query.first()
            category_id = category.id if category else 1

        #Request the same category we just fetched
        res = self.client.get(f"/categories/{category_id}/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["questions"], list)
        self.assertEqual(data["current_category"], category_id)
        self.assertIsInstance(data["total_questions"], int)

    def test_get_questions_from_invalid_category_id(self):

        res = self.client.get("/categories/abc/questions")
        self.assertEqual(res.status_code, 404)

    def test_search_questions(self):

        res = self.client.post("/questions", json={"searchTerm": "title"})
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["questions"], list)
        self.assertIsInstance(data["total_questions"], int)

    def test_search_questions_invalid_missing_field(self):

        res = self.client.post("/questions", json={})
        self.assertEqual(res.status_code, 400)

    def test_add_questions(self):
        # ensure category exists (was hardcoded to 1)
        with self.app.app_context():
            category = Category.query.first()
            category_id = category.id if category else 1
            
        res = self.client.post("/questions", json={
            "question": "Who sees better humar or cat?",
            "answer": "cat",
            "difficulty": 1,
            "category": category_id
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_add_questions_invalid_missing_field(self):

        res = self.client.post("/questions", json={
            "question": "",
            "answer": "",
            "difficulty": 1,
            "category": 1
        })
        self.assertEqual(res.status_code, 400)

    def test_delete_question(self):
        
        with self.app.app_context():
            # use existing category id (avoid FK violation)
            category = Category.query.first()
            category_id = category.id if category else 1

            new_question = Question(
                question="test question",
                answer="test answer",
                difficulty=1,
                category=str(category_id)
            )
            db.session.add(new_question)
            db.session.commit()
            question_to_delete = Question.query.filter(
                Question.question.ilike(f"%test question%")).first()
            id = question_to_delete.id
        res = self.client.delete("/questions/" + str(id))
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["id"], int)

    def test_delete_not_existing_question(self):

        res = self.client.delete("/questions/9999")
        self.assertEqual(res.status_code, 404)

    def test_get_quizz_questions(self):
        # ensure quiz_category uses existing category
        with self.app.app_context():
            category = Category.query.first()
            category_id = category.id if category else 1
            
        res = self.client.post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": str(category_id)
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_get_quizz_questions_missing_body(self):

        res = self.client.post("/quizzes", json={})
        self.assertEqual(res.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
