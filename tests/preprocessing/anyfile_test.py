# As a professor, I want to upload my materials in whatever file format I have (PDF, text, images) so that the system can create quizzes from any source
import pytest
from unittest.mock import patch
import gradio as gr
from src.phases.quizzes import Quiz
class TestAnyFileValidation:


# ---------------------- Gradio stubs ---------------------- #
  @pytest.fixture(autouse=True)
  def stub_gradio(monkeypatch):
    """
    Replace gradio.update and gradio.Markdown with simple stubs so tests
    don't depend on real Gradio internals.
    """

    class DummyUpdate:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class DummyMarkdown:
        def __init__(self, value=""):
            self.value = value

        def __repr__(self):
            return f"DummyMarkdown({self.value!r})"

    monkeypatch.setattr(Quiz.gr, "update", lambda **kw: DummyUpdate(**kw))
    monkeypatch.setattr(Quiz.gr, "Markdown", DummyMarkdown)

    return DummyUpdate, DummyMarkdown


@pytest.fixture
def quiz():
    return Quiz()


# ---------------------- Basic validation ---------------------- #

def test_generate_from_text_empty_input_hides_components_and_shows_message(quiz):
    updates1, updates2, message = quiz.generate_from_text(
        input="   ",
        num_questions=5,
        question_types=["fill_blank"],
    )

    assert isinstance(message, str)
    assert "Please provide text" in message

    assert updates1.kwargs.get("visible") is False
    assert updates2.kwargs.get("visible") is False


def test_generate_from_text_no_question_types_hides_components_and_shows_message(quiz):
    updates1, updates2, message = quiz.generate_from_text(
        input="Some course text",
        num_questions=5,
        question_types=[],
    )

    assert isinstance(message, str)
    assert "Please select at least one question type" in message

    assert updates1.kwargs.get("visible") is False
    assert updates2.kwargs.get("visible") is False


# ---------------------- User story: any source (PDF / image / text) ---------------------- #

def test_generate_from_text_accepts_pdf_extracted_text(quiz, monkeypatch):
    """
    As a professor, I can upload a PDF; upstream code extracts text.
    Once the PDF is converted to text, Quiz should treat it like any other text.
    """
    pdf_text = "PDF: Introduction to Quantum Mechanics."

    dummy_questions = [
        {
            "type": "fill_blank",
            "question": "PDF: Introduction to _____ Mechanics.",
            "answer": "Quantum",
        },
        {
            "type": "fill_blank",
            "question": "Quantum mechanics deals with _____.",
            "answer": "microscopic systems",
        },
    ]

    def fake_generate_fill_blank_questions(input_text, count):
        assert input_text == pdf_text
        assert count == 2
        return dummy_questions

    monkeypatch.setattr(
        Quiz.q_types,
        "generate_fill_blank_questions",
        fake_generate_fill_blank_questions,
    )

    u1, u2, markdown = quiz.generate_from_text(
        input=pdf_text,
        num_questions=2,
        question_types=["fill_blank"],
    )

    assert u1.kwargs.get("visible") is True
    assert u2.kwargs.get("visible") is True

    assert quiz.input_text == pdf_text
    assert quiz.current_quiz_state["num_questions"] == 2
    assert quiz.current_quiz_state["questions"] == dummy_questions
    assert quiz.current_quiz_state["question_types"] == ["fill_blank"]

    text = markdown.value
    assert "# Generated Quiz (2 questions)" in text
    assert "PDF: Introduction to _____ Mechanics." in text


def test_generate_from_text_accepts_image_ocr_text(quiz, monkeypatch):
    """
    As a professor, I can upload an image; upstream OCR extracts text.
    Quiz should still work normally with that text.
    """
    image_ocr_text = "IMAGE: The mitochondrion is the powerhouse of the cell."

    dummy_questions = [
        {
            "type": "mcq",
            "question": "IMAGE: The mitochondrion is the _____ of the cell.",
            "answer": "powerhouse",
            "options": ["nucleus", "powerhouse", "membrane", "ribosome"],
        }
    ]

    def fake_generate_mcq_questions(input_text, count):
        assert input_text == image_ocr_text
        assert count == 1
        return dummy_questions

    monkeypatch.setattr(
        Quiz.q_types,
        "generate_mcq_questions",
        fake_generate_mcq_questions,
    )

    _, _, markdown = quiz.generate_from_text(
        input=image_ocr_text,
        num_questions=1,
        question_types=["mcq"],
    )

    assert quiz.input_text == image_ocr_text
    assert quiz.current_quiz_state["num_questions"] == 1
    assert quiz.current_quiz_state["questions"] == dummy_questions

    text = markdown.value
    # Group header for MCQs (based on 'mcq' type)
    assert "## Multiple Choice Questions" in text
    assert "IMAGE: The mitochondrion is the _____ of the cell." in text


def test_generate_from_text_accepts_combined_text_from_multiple_sources(quiz, monkeypatch):
    """
    Simulate a professor uploading *multiple* materials (PDF + images + text).
    Upstream, all text is combined; Quiz should handle the combined text and
    generate questions across multiple types.
    """
    combined_text = (
        "PDF: Intro to machine learning.\n"
        "IMAGE: Diagram of a neural network.\n"
        "TEXT: Homework instructions and examples."
    )

    calls = {"fill_blank": None, "mcq": None, "topic": None}

    def fake_generate_fill_blank_questions(input_text, count):
        calls["fill_blank"] = (input_text, count)
        return [
            {
                "type": "fill_blank",
                "question": "From PDF content ____.",
                "answer": "machine learning",
            }
            for _ in range(count)
        ]

    def fake_generate_mcq_questions(input_text, count):
        calls["mcq"] = (input_text, count)
        return [
            {
                "type": "mcq",
                "question": "From IMAGE content ____.",
                "answer": "neural network",
                "options": ["tree", "regression", "neural network", "svm"],
            }
            for _ in range(count)
        ]

    def fake_generate_topic_questions(input_text, count):
        calls["topic"] = (input_text, count)
        return [
            {
                "type": "topic",
                "question": "From TEXT content ____.",
                "answer": "homework",
            }
            for _ in range(count)
        ]

    monkeypatch.setattr(
        Quiz.q_types,
        "generate_fill_blank_questions",
        fake_generate_fill_blank_questions,
    )
    monkeypatch.setattr(
        Quiz.q_types,
        "generate_mcq_questions",
        fake_generate_mcq_questions,
    )
    monkeypatch.setattr(
        Quiz.q_types,
        "generate_topic_questions",
        fake_generate_topic_questions,
    )

    # 6 questions split evenly between 3 types → each gets 2
    question_types = ["fill_blank", "mcq", "topic"]
    _, _, markdown = quiz.generate_from_text(
        input=combined_text,
        num_questions=6,
        question_types=question_types,
    )

    # All generators see the full combined text
    assert calls["fill_blank"] == (combined_text, 2)
    assert calls["mcq"] == (combined_text, 2)
    assert calls["topic"] == (combined_text, 2)

    assert quiz.input_text == combined_text
    assert quiz.current_quiz_state["num_questions"] == 6
    assert quiz.current_quiz_state["question_types"] == question_types
    assert len(quiz.current_quiz_state["questions"]) == 6

    text = markdown.value
    # Headers for all three question type groups
    assert "## Fill in the Blank Questions" in text
    assert "## Multiple Choice Questions" in text
    assert "## Topic Questions" in text


def test_generate_from_text_distributes_remainder_questions_across_types(quiz, monkeypatch):
    """
    If num_questions is not divisible by the number of types, extra questions
    are assigned to earlier types.
    """
    input_text = "Some generic course text."

    calls = {"fill_blank": None, "mcq": None, "topic": None}

    def fb(input_text_, count):
        calls["fill_blank"] = count
        return [{"type": "fill_blank", "question": "FB", "answer": "A"}] * count

    def mcq(input_text_, count):
        calls["mcq"] = count
        return [{"type": "mcq", "question": "MCQ", "answer": "B"}] * count

    def topic(input_text_, count):
        calls["topic"] = count
        return [{"type": "topic", "question": "TOPIC", "answer": "C"}] * count

    monkeypatch.setattr(Quiz.q_types, "generate_fill_blank_questions", fb)
    monkeypatch.setattr(Quiz.q_types, "generate_mcq_questions", mcq)
    monkeypatch.setattr(Quiz.q_types, "generate_topic_questions", topic)

    # 5 questions across 3 types → base=1 each, remainder=2
    # So counts should be: fill_blank=2, mcq=2, topic=1
    quiz.generate_from_text(
        input=input_text,
        num_questions=5,
        question_types=["fill_blank", "mcq", "topic"],
    )

    assert calls["fill_blank"] == 2
    assert calls["mcq"] == 2
    assert calls["topic"] == 1
    assert quiz.current_quiz_state["num_questions"] == 5


# ---------------------- Shuffle behaviour ---------------------- #

def test_shuffle_without_questions_hides_components_and_message(quiz):
    u1, u2, msg = quiz.shuffle()

    assert "Please generate a quiz first before shuffling" in msg
    assert u1.kwargs.get("visible") is False
    assert u2.kwargs.get("visible") is False


def test_shuffle_uses_copy_and_randomizes_order(quiz, monkeypatch):
    original_questions = [
        {"type": "fill_blank", "question": "Q1", "answer": "A1"},
        {"type": "mcq", "question": "Q2", "answer": "A2"},
        {"type": "topic", "question": "Q3", "answer": "A3"},
    ]

