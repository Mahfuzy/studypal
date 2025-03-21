from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import json
import os

class StudyAssistantViewsTest(APITestCase):
    """Test suite for study assistant views."""

    def setUp(self):
        """Set up test data."""
        self.query_url = '/api/study-assistant/query/'
        self.task_status_url = '/api/study-assistant/task-status/'

    @patch('study_assistant.views.genai.Client')
    def test_text_query(self, mock_client):
        """Test sending a text query to the AI assistant."""
        # Mock the AI response
        mock_response = MagicMock()
        mock_response.text = "This is a test response"
        mock_client.return_value.models.generate_content.return_value = mock_response

        data = {
            'query': 'What is photosynthesis?'
        }
        response = self.client.post(self.query_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], 'This is a test response')
        mock_client.return_value.models.generate_content.assert_called_once()

    @patch('study_assistant.views.process_uploaded_file.delay')
    def test_file_upload_docx(self, mock_process_file):
        """Test uploading a DOCX file for processing."""
        # Create a dummy DOCX file
        file_content = b'Test content'
        uploaded_file = SimpleUploadedFile(
            'test.docx',
            file_content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

        mock_process_file.return_value.id = 'test_task_id'

        data = {
            'query': 'Please analyze this document',
            'file': uploaded_file
        }
        response = self.client.post(self.query_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['task_id'], 'test_task_id')
        mock_process_file.assert_called_once()

    @patch('study_assistant.views.process_uploaded_file.delay')
    def test_file_upload_pdf(self, mock_process_file):
        """Test uploading a PDF file for processing."""
        # Create a dummy PDF file
        file_content = b'%PDF-1.4 Test content'
        uploaded_file = SimpleUploadedFile(
            'test.pdf',
            file_content,
            content_type='application/pdf'
        )

        mock_process_file.return_value.id = 'test_task_id'

        data = {
            'query': 'Please analyze this document',
            'file': uploaded_file
        }
        response = self.client.post(self.query_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['task_id'], 'test_task_id')
        mock_process_file.assert_called_once()

    def test_invalid_file_type(self):
        """Test uploading an unsupported file type."""
        file_content = b'Test content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )

        data = {
            'query': 'Please analyze this document',
            'file': uploaded_file
        }
        response = self.client.post(self.query_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_query(self):
        """Test request without a query."""
        response = self.client.post(self.query_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('study_assistant.views.AsyncResult')
    def test_task_status_pending(self, mock_async_result):
        """Test checking status of a pending task."""
        task_id = 'test_task_id'
        mock_async_result.return_value.state = 'PENDING'
        
        response = self.client.get(f'{self.task_status_url}{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], 'Processing')

    @patch('study_assistant.views.AsyncResult')
    def test_task_status_success(self, mock_async_result):
        """Test checking status of a completed task."""
        task_id = 'test_task_id'
        mock_async_result.return_value.state = 'SUCCESS'
        mock_async_result.return_value.result = {'response': 'Task completed successfully'}
        
        response = self.client.get(f'{self.task_status_url}{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Completed')
        self.assertEqual(response.data['response'], {'response': 'Task completed successfully'})

    @patch('study_assistant.views.AsyncResult')
    def test_task_status_failure(self, mock_async_result):
        """Test checking status of a failed task."""
        task_id = 'test_task_id'
        mock_async_result.return_value.state = 'FAILURE'
        mock_async_result.return_value.result = 'Task failed'
        
        response = self.client.get(f'{self.task_status_url}{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'Failed')
        self.assertEqual(response.data['error'], 'Task failed')

    @patch('study_assistant.views.genai.Client')
    def test_cache_hit(self, mock_client):
        """Test that responses are cached and reused."""
        # First request - should hit the AI
        mock_response = MagicMock()
        mock_response.text = "This is a test response"
        mock_client.return_value.models.generate_content.return_value = mock_response

        data = {
            'query': 'What is photosynthesis?'
        }
        response1 = self.client.post(self.query_url, data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['response'], 'This is a test response')
        mock_client.return_value.models.generate_content.assert_called_once()

        # Second request with same query - should hit cache
        mock_client.reset_mock()
        response2 = self.client.post(self.query_url, data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['response'], 'This is a test response')
        mock_client.return_value.models.generate_content.assert_not_called()

    @patch('study_assistant.views.genai.Client')
    def test_ai_error_handling(self, mock_client):
        """Test handling of AI service errors."""
        mock_client.return_value.models.generate_content.side_effect = Exception("AI service error")

        data = {
            'query': 'What is photosynthesis?'
        }
        response = self.client.post(self.query_url, data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'AI service error')
