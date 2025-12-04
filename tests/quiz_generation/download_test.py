import pytest
from unittest.mock import patch, mock_open, call
import gradio as gr

from src.phases.quizzes import Quiz

class TestQuizDownload:
    @pytest.fixture
    def quiz_instance(self):
        """Fixture providing a fresh Quiz instance for each test"""
        return Quiz()
    
    @pytest.fixture
    def sample_markdown_content(self):
        """Fixture providing sample markdown content"""
        return """
        # Generated Quiz (3 questions)

        ## Fill in the Blank Questions

        **Q1.** Python is a high-level _____ language.

        *Answer: programming*

        **Q2.** _____ created Python in 1991.

        *Answer: Guido van Rossum*

        **Q3.** Python is widely used for web development, _____, and artificial intelligence.

        *Answer: data science*
        """
    
    def test_download_creates_file_with_correct_name(self, quiz_instance, sample_markdown_content):
        """Test that download creates a file with the correct filename"""
        quiz_instance.markdown_result = sample_markdown_content
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            # Verify file was opened with correct name and mode
            mock_file.assert_called_once_with("generated_quiz.md", "w")
    
    def test_download_writes_markdown_content(self, quiz_instance, sample_markdown_content):
        """Test that download writes the markdown_result to the file"""
        quiz_instance.markdown_result = sample_markdown_content
        
        with patch('builtins.open', mock_open()) as mock_file:
            quiz_instance.download("md")
            
            # Get the file handle
            handle = mock_file()
            
            # Verify write was called with the markdown content
            handle.write.assert_called_once_with(sample_markdown_content)
    
    def test_download_returns_correct_tuple_format(self, quiz_instance, sample_markdown_content):
        """Test that download returns the correct tuple (filename, gr.Markdown)"""
        quiz_instance.markdown_result = sample_markdown_content
        
        with patch('builtins.open', mock_open()):
            result = quiz_instance.download("md")
        
        # Should return a tuple of (filename, gr.Markdown)
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        # First element should be the filename string
        filename = result[0]
        assert filename == "generated_quiz.md"
        assert isinstance(filename, str)
        
        # Second element should be a Gradio Markdown component
        markdown_output = result[1]
        assert isinstance(markdown_output, gr.Markdown)
    
    def test_download_markdown_contains_content(self, quiz_instance, sample_markdown_content):
        """Test that the returned Markdown component contains the correct content"""
        quiz_instance.markdown_result = sample_markdown_content
        
        with patch('builtins.open', mock_open()):
            result = quiz_instance.download("md")
        
        _, markdown_output = result
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        
        # Verify the markdown contains expected content
        assert "Generated Quiz" in markdown_text
        assert "Python is a high-level _____ language" in markdown_text
        assert "programming" in markdown_text
    
    def test_download_with_empty_markdown(self, quiz_instance):
        """Test download when markdown_result is empty"""
        quiz_instance.markdown_result = ""
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            # Should still create file and write empty string
            mock_file.assert_called_once_with("generated_quiz.md", "w")
            handle = mock_file()
            handle.write.assert_called_once_with("")
            
            # Should still return proper tuple
            assert isinstance(result, tuple)
            assert result[0] == "generated_quiz.md"
    
    def test_download_with_quiz_and_analysis(self, quiz_instance):
        """Test download with quiz that includes analysis section"""
        markdown_with_analysis = """
        # Generated Quiz (2 questions)

        ## Fill in the Blank Questions

        **Q1.** Test question _____?

        *Answer: answer*

        ---
        ## Analysis

        **Key Terms (TF-IDF):** python, programming, language

        **Named Entities (NER):** Python (PRODUCT), Google (ORG)

        **Topics (LDA):**
        Topic 1: python, code, syntax
        """
        quiz_instance.markdown_result = markdown_with_analysis
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            handle.write.assert_called_once_with(markdown_with_analysis)
            
            # Verify analysis is in returned markdown
            _, markdown_output = result
            markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
            assert "## Analysis" in markdown_text
            assert "Key Terms (TF-IDF)" in markdown_text
    
    def test_download_with_special_characters(self, quiz_instance):
        """Test download with special characters in markdown"""
        special_markdown = """
        # Generated Quiz

        **Q1.** Python's syntax uses "quotes" & special chars: <, >, *, /, %

        *Answer: special*
        """
        quiz_instance.markdown_result = special_markdown
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            handle.write.assert_called_once_with(special_markdown)
    
    def test_download_with_unicode_characters(self, quiz_instance):
        """Test download with unicode characters in markdown"""
        unicode_markdown = """
        # Generated Quiz

        **Q1.** Python supports Unicode: 你好, Привет, مرحبا 🐍

        *Answer: unicode*
        """
        quiz_instance.markdown_result = unicode_markdown
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            handle.write.assert_called_once_with(unicode_markdown)
    
    def test_download_multiple_times_overwrites(self, quiz_instance):
        """Test that downloading multiple times overwrites the same file"""
        first_markdown = "# First Quiz"
        second_markdown = "# Second Quiz"
        
        with patch('builtins.open', mock_open()) as mock_file:
            # First download
            quiz_instance.markdown_result = first_markdown
            quiz_instance.download("md")
            
            # Second download
            quiz_instance.markdown_result = second_markdown
            quiz_instance.download("md")
            
            # Verify file was opened twice with same filename
            assert mock_file.call_count == 2
            calls = [call("generated_quiz.md", "w"), call("generated_quiz.md", "w")]
            mock_file.assert_has_calls(calls)
    
    def test_download_after_generate(self, quiz_instance):
        """Test download after generate_from_text workflow"""
        sample_questions = [
            {'question': 'Test _____?', 'answer': 'question', 'type': 'fill_blank'}
        ]
        
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = sample_questions
            
            # Generate quiz
            quiz_instance.generate_from_text("Test input", 1, ['fill_blank'])
            
            # Download
            with patch('builtins.open', mock_open()) as mock_file:
                result = quiz_instance.download("md")
                
                # Verify file was created
                mock_file.assert_called_once()
                
                # Verify content includes generated quiz
                handle = mock_file()
                written_content = handle.write.call_args[0][0]
                assert "Test _____?" in written_content
    
    def test_download_after_shuffle(self, quiz_instance):
        """Test download after shuffle workflow"""
        quiz_instance.current_quiz_state['questions'] = [
            {'question': 'Q1 _____?', 'answer': 'A1', 'type': 'fill_blank'},
            {'question': 'Q2 _____?', 'answer': 'A2', 'type': 'fill_blank'}
        ]
        quiz_instance.current_quiz_state['num_questions'] = 2
        
        # Shuffle
        with patch('random.shuffle', side_effect=lambda x: x.reverse()):
            quiz_instance.shuffle()
        
        # Download
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            
            # Verify shuffled content is in download
            assert "Q1 _____?" in written_content
            assert "Q2 _____?" in written_content
    
    def test_download_after_analyze(self, quiz_instance):
        """Test download after analyze workflow"""
        quiz_instance.input_text = "Sample text for analysis"
        quiz_instance.markdown_result = "# Quiz\n\n"
        
        with patch('src.phases.quizzes.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.quizzes.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.quizzes.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = ['keyword1', 'keyword2']
            mock_entities.return_value = []
            mock_topics.return_value = []
            
            # Analyze
            quiz_instance.analyze()
        
        # Download
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            
            # Verify analysis is in download
            assert "## Analysis" in written_content
            assert "Key Terms (TF-IDF)" in written_content
    
    def test_download_file_handle_closed_properly(self, quiz_instance, sample_markdown_content):
        """Test that file handle is properly closed after writing"""
        quiz_instance.markdown_result = sample_markdown_content
        
        m = mock_open()
        with patch('builtins.open', m):
            quiz_instance.download("md")
            
            # Verify the context manager was used (file gets closed)
            handle = m()
            handle.__enter__.assert_called_once()
            handle.__exit__.assert_called_once()
    
    def test_download_with_very_long_content(self, quiz_instance):
        """Test download with very long markdown content"""
        # Create a large quiz with many questions
        long_markdown = "# Generated Quiz (100 questions)\n\n"
        for i in range(1, 101):
            long_markdown += f"**Q{i}.** Question {i} _____?\n\n*Answer: Answer {i}*\n\n"
        
        quiz_instance.markdown_result = long_markdown
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            handle.write.assert_called_once()
            
            # Verify the entire content was written
            written_content = handle.write.call_args[0][0]
            assert len(written_content) == len(long_markdown)
            assert "Q100" in written_content
    
    def test_download_preserves_markdown_formatting(self, quiz_instance):
        """Test that download preserves markdown formatting"""
        formatted_markdown = """
        # Generated Quiz (1 questions)

        ## Fill in the Blank Questions

        **Q1.** This is **bold** and *italic* text.

        *Answer: formatted*

        ---

        > This is a blockquote

        - List item 1
        - List item 2

        `code snippet`
        """
        quiz_instance.markdown_result = formatted_markdown
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            
            # Verify all markdown formatting is preserved
            assert "**bold**" in written_content
            assert "*italic*" in written_content
            assert "> This is a blockquote" in written_content
            assert "- List item 1" in written_content
            assert "`code snippet`" in written_content
    
    def test_download_handles_newlines_correctly(self, quiz_instance):
        """Test that download handles various newline formats"""
        markdown_with_newlines = "Line 1\nLine 2\n\nLine 3\r\nLine 4"
        quiz_instance.markdown_result = markdown_with_newlines
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            
            assert written_content == markdown_with_newlines
    
    def test_download_returns_same_content_as_stored(self, quiz_instance, sample_markdown_content):
        """Test that returned Markdown matches stored markdown_result"""
        quiz_instance.markdown_result = sample_markdown_content
        
        with patch('builtins.open', mock_open()):
            filename, markdown_output = quiz_instance.download("md")
        
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        
        # The returned markdown should match what's stored
        assert sample_markdown_content in markdown_text or markdown_text in sample_markdown_content
    
    def test_download_integration_complete_workflow(self, quiz_instance):
        """Test complete workflow: generate -> shuffle -> analyze -> download"""
        sample_text = "Python is a programming language. It was created by Guido."
        sample_questions = [
            {'question': 'Python is a _____ language.', 'answer': 'programming', 'type': 'fill_blank'}
        ]
        
        # Complete workflow
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = sample_questions
            quiz_instance.generate_from_text(sample_text, 1, ['fill_blank'])
        
        with patch('random.shuffle'):
            quiz_instance.shuffle()
        
        with patch('src.phases.quizzes.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.quizzes.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.quizzes.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = ['python']
            mock_entities.return_value = [{'text': 'Guido', 'label': 'PERSON'}]
            mock_topics.return_value = [['programming', 'language']]
            
            quiz_instance.analyze()
        
        # Download
        with patch('builtins.open', mock_open()) as mock_file:
            filename, markdown_output = quiz_instance.download("md")
            
            # Verify everything is in the download
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            
            assert "Python is a _____ language" in written_content
            assert "## Analysis" in written_content
            assert "python" in written_content
            assert "Guido" in written_content
    
    def test_download_without_prior_generation(self, quiz_instance):
        """Test download when no quiz has been generated yet"""
        # markdown_result should be empty initially
        assert quiz_instance.markdown_result == ""
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = quiz_instance.download("md")
            
            # Should still work, just with empty content
            mock_file.assert_called_once_with("generated_quiz.md", "w")
            handle = mock_file()
            handle.write.assert_called_once_with("")
            
            assert result[0] == "generated_quiz.md"
    
    @patch('builtins.open', side_effect=IOError("Disk full"))
    def test_download_handles_io_error(self, mock_file, quiz_instance, sample_markdown_content):
        """Test that download properly propagates IO errors"""
        quiz_instance.markdown_result = sample_markdown_content
        
        with pytest.raises(IOError, match="Disk full"):
            quiz_instance.download("md")
    
    @patch('builtins.open', side_effect=PermissionError("No write permission"))
    def test_download_handles_permission_error(self, mock_file, quiz_instance, sample_markdown_content):
        """Test that download properly propagates permission errors"""
        quiz_instance.markdown_result = sample_markdown_content
        
        with pytest.raises(PermissionError, match="No write permission"):
            quiz_instance.download("md")