import pytest
from unittest.mock import patch
import gradio as gr
from src.phases.quizzes import Quiz  

class TestInputValidation:
      @pytest.fixture
    def file_input(self):
        """Fixture providing a fresh Quiz instance for each test"""
        return Quiz()
