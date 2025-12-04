# As an instructor, I want to be able to specify the question types so that students demonstrate their knowledge in different ways
import pytest
from unittest.mock import patch
import gradio as gr
from src.phases.quizzes import Quiz

class TestQuestTypesValidation:
  @pytest.fixture
  def num_of_files(self):
    "Number of files detected"
    return Quiz()
  
  @pytest.fixture
  def question_type(self):
    """Common number of questions fixture."""
    return Quiz()


  @pytest.fixture
  def sample_questions(sample_topic, sample_num_questions):
    """
    Fixture that returns a small generated quiz.
    This uses the real generator (so it's a sort of integration-level fixture).
    """
    return Quiz(
        topic=sample_topic,
        num_questions=sample_num_questions,
    )


# -------------------------
# Core behavior tests
# -------------------------

def test_supported_question_types_contains_multiple_choice():
    assert "multiple_choice" in Quiz


def test_llm_generate_mc_question_structure(sample_topic):
    q = Quiz(sample_topic, 1)

    assert isinstance(q, Quiz)
    assert sample_topic in q.prompt
    assert len(q.options) == 4
    assert q.correct_index == 0


def test_generate_multiple_choice_questions_count_and_type(sample_topic, sample_num_questions):
    questions = Quiz(sample_topic, sample_num_questions)

    assert len(questions) == sample_num_questions
    assert all(isinstance(q, Quiz) for q in questions)


def test_generate_multiple_choice_questions_raises_for_non_positive_num():
    with pytest.raises(ValueError):
        Quiz(topic="anything", num_questions=0)


def test_generate_quiz_rejects_unsupported_type(sample_topic):
    with pytest.raises(ValueError):
        Quiz(question_type="short_answer", topic=sample_topic, num_questions=3)


def test_build_quiz_respects_number_of_questions(sample_topic, sample_num_questions):
    markdown_quiz = Quiz(
        question_type="multiple_choice",
        topic=sample_topic,
        num_questions=sample_num_questions,
    )

    # Each question line starts with Q1., Q2., etc.
    question_lines = [line for line in markdown_quiz.splitlines() if line.startswith("Q")]
    assert len(question_lines) == sample_num_questions


def test_build_quiz_output_contains_mc_options(sample_topic):
    markdown_quiz = Quiz(
        question_type="multiple_choice",
        topic=sample_topic,
        num_questions=1,
    )

    for letter in ["A.", "B.", "C.", "D."]:
        assert f"{letter} " in markdown_quiz


def test_format_quiz_as_markdown_structure(sample_questions):
    # Use the fixture's first question to validate formatting.
    q = sample_questions[0]
    md = Quiz([q])
    lines = md.splitlines()

    # Basic structure: prompt then A., B., ...
    assert lines[0].startswith("Q1.")
    assert lines[1].strip().startswith("A.")
    assert lines[2].strip().startswith("B.")


def test_gradio_demo_is_defined():
    # Simple smoke test that the Gradio UI object exists.
    assert isinstance(Quiz, gr.Blocks)


# -------------------------
# Tests using unittest.mock.patch
# -------------------------

@patch("quiz_app.llm_generate_mc_question")
def test_generate_multiple_choice_questions_uses_llm(mock_llm, sample_topic, sample_num_questions):
    """
    Ensure that generate_multiple_choice_questions delegates
    to llm_generate_mc_question once per question.
    """
    # Configure the mock to return predictable Question objects.
    def fake_llm(topic_arg, index_arg):
        return Quiz(
            prompt=f"Fake Q{index_arg} about {topic_arg}",
            options=[f"Option {i}" for i in range(4)],
            correct_index=1,
        )

    mock_llm.side_effect = fake_llm

    questions = Quiz(sample_topic, sample_num_questions)

    # Ensure the LLM function was called exactly num times
    assert mock_llm.call_count == sample_num_questions

    # Ensure the returned questions match the fake_llm logic
    assert questions[0].prompt == f"Fake Q1 about {sample_topic}"
    assert questions[1].prompt == f"Fake Q2 about {sample_topic}"
    assert questions[2].prompt == f"Fake Q3 about {sample_topic}"


@patch("quiz_app.generate_quiz")
def test_build_quiz_calls_generate_quiz(mock_generate_quiz, sample_topic, sample_num_questions):
    """
    Ensure build_quiz uses generate_quiz internally, so the instructor's
    selected question_type is respected.
    """
    # Prepare fake questions returned by generate_quiz
    fake_questions = [
        Quiz(
            prompt="Q1. Fake geometry?",
            options=["A", "B", "C", "D"],
            correct_index=0,
        ),
        Quiz(
            prompt="Q2. Fake geometry again?",
            options=["A", "B", "C", "D"],
            correct_index=1,
        ),
    ]
    mock_generate_quiz.return_value = fake_questions

    result_markdown = Quiz(
        question_type="multiple_choice",
        topic=sample_topic,
        num_questions=sample_num_questions,
    )

    # Check that generate_quiz was invoked with the instructor's inputs.
    mock_generate_quiz.assert_called_once_with(
        question_type="multiple_choice",
        topic=sample_topic,
        num_questions=sample_num_questions,
    )

    result_markdown = Quiz(
        question_type="multiple_choice",
        topic=sample_topic,
        num_questions=sample_num_questions,
    )

    # And the output contains both fake prompts
    assert "Q1. Fake geometry?" in result_markdown
    assert "Q2. Fake geometry again?" in result_markdown
