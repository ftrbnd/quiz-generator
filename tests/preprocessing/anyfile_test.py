# As a professor, I want to upload my materials in whatever file format I have (PDF, text, images) so that the system can create quizzes from any source
import pytest
from unittest.mock import patch
import gradio as gr
from src.phases.quizzes import Quiz

class TestAnyFileValidation:
  
  @pytest.fixture
  def FileTypesAcceptedTest(x):  
    x = "Testing"
    print("Testing")
    return x == "Testing"
