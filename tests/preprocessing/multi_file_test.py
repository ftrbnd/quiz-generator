import pytest
from unittest.mock import patch
import gradio as gr
from src.phases.quizzes import Quiz  

class TestMultiFileValidation:
      @pytest.fixture
          def file_input(Quiz):
              """Fixture providing a fresh Quiz instance for each test"""
              return Quiz()
