"""
Tests for AI functionality in TimeToShopping_bot
Tests for OpenAI integration and Armenian text generation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from bot.ai.openai_client import OpenAIClient
from bot.ai.prompts import (
    get_system_prompt, get_user_prompt, get_all_formats,
    get_format_name, get_cta_examples, get_format_emojis,
    POST_FORMAT_PROMPTS, DEFAULT_CTA_BUTTONS
)
from bot.ai import is_armenian_text, get_text_language, validate_armenian_post


class TestPrompts:
    """Test prompt generation and format handling"""
    
    def test_get_system_prompt(self):
        """Test system prompt returns Armenian instructions"""
        prompt = get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "ShoppingTime" in prompt
        assert "Telegram" in prompt
        # Check for Armenian characters
        armenian_range = range(0x0530, 0x058F + 1)
        assert any(ord(char) in armenian_range for char in prompt)
    
    def test_get_user_prompt(self):
        """Test user prompt generation"""
        prompt = get_user_prompt("selling", "test keywords", "additional details")
        
        assert isinstance(prompt, str)
        assert "selling" in prompt
        assert "test keywords" in prompt
        assert "additional details" in prompt
        
        # Test without additional details
        prompt_simple = get_user_prompt("info", "simple keywords")
        assert isinstance(prompt_simple, str)
        assert "simple keywords" in prompt_simple
    
    def test_get_all_formats(self):
        """Test getting all post formats"""
        formats = get_all_formats()
        
        assert isinstance(formats, dict)
        assert len(formats) >= 4
        assert "selling" in formats
        assert "collection" in formats
        assert "info" in formats
        assert "promo" in formats
    
    def test_get_format_name(self):
        """Test format name translation"""
        assert get_format_name("selling") == "Վաճառող փոստ"
        assert get_format_name("collection") == "Ընտրանի"
        assert get_format_name("info") == "Տեղեկատվական"
        assert get_format_name("promo") == "Ակցիա/Զեղչ"
        
        # Test unknown format
        assert get_format_name("unknown") == "unknown"
    
    def test_get_cta_examples(self):
        """Test CTA examples for different formats"""
        selling_ctas = get_cta_examples("selling")
        assert isinstance(selling_ctas, list)
        assert len(selling_ctas) > 0
        
        collection_ctas = get_cta_examples("collection")
        assert isinstance(collection_ctas, list)
        
        # Test unknown format returns default
        unknown_ctas = get_cta_examples("unknown_format")
        assert isinstance(unknown_ctas, list)
    
    def test_get_format_emojis(self):
        """Test emoji sets for formats"""
        selling_emojis = get_format_emojis("selling")
        assert isinstance(selling_emojis, list)
        assert len(selling_emojis) > 0
        
        # Test that emojis are actually emoji characters
        for emoji in selling_emojis:
            assert len(emoji) >= 1
            # Check if it's likely an emoji (high Unicode range)
            assert any(ord(char) > 0x1F000 for char in emoji)
    
    def test_post_format_prompts_structure(self):
        """Test POST_FORMAT_PROMPTS data structure"""
        assert isinstance(POST_FORMAT_PROMPTS, dict)
        
        for format_key, format_data in POST_FORMAT_PROMPTS.items():
            assert "armenian" in format_data
            assert "cta_examples" in format_data
            assert isinstance(format_data["armenian"], str)
            assert isinstance(format_data["cta_examples"], list)
    
    def test_default_cta_buttons(self):
        """Test default CTA buttons are in Armenian"""
        assert isinstance(DEFAULT_CTA_BUTTONS, list)
        assert len(DEFAULT_CTA_BUTTONS) > 0
        
        # Check that buttons contain Armenian text
        armenian_range = range(0x0530, 0x058F + 1)
        for button in DEFAULT_CTA_BUTTONS:
            assert isinstance(button, str)
            assert any(ord(char) in armenian_range for char in button)


class TestArmenianTextUtils:
    """Test Armenian text processing utilities"""
    
    def test_is_armenian_text(self):
        """Test Armenian text detection"""
        # Armenian text
        assert is_armenian_text("Բարի գալուստ") == True
        assert is_armenian_text("Սա հայերեն տեքստ է") == True
        
        # Non-Armenian text
        assert is_armenian_text("Hello world") == False
        assert is_armenian_text("Привет мир") == False
        assert is_armenian_text("123456") == False
        
        # Mixed text (should return True if contains Armenian)
        assert is_armenian_text("Hello Բարի գալուստ") == True
        assert is_armenian_text("Test Սա հայերեն է") == True
    
    def test_get_text_language(self):
        """Test language detection"""
        assert get_text_language("Բարի գալուստ") == "hy"
        assert get_text_language("Hello world") == "en" 
        assert get_text_language("Привет мир") == "ru"
        assert get_text_language("123456 !@#") == "en"  # Default
        
        # Mixed text should detect Armenian if present
        assert get_text_language("Hello Բարի") == "hy"
    
    def test_validate_armenian_post(self):
        """Test Armenian post validation"""
        # Good Armenian post
        good_post = "🔥 Գնեք զեղչով! Սա լավ առաջարկություն է բոլոր գնորդների համար։ Մի բաց թողեք այս հատուկ առաջարկությունը։ Գնել հիմա!"
        result = validate_armenian_post(good_post)
        
        assert isinstance(result, dict)
        assert "score" in result
        assert "issues" in result  
        assert "word_count" in result
        assert "has_armenian" in result
        assert "has_cta" in result
        assert "emoji_count" in result
        
        assert result["has_armenian"] == True
        assert result["has_cta"] == True
        assert result["score"] >= 7
        
        # Poor post (too short, no Armenian, no CTA)
        poor_post = "Short text"
        poor_result = validate_armenian_post(poor_post)
        
        assert poor_result["score"] < 7
        assert len(poor_result["issues"]) > 0
        assert poor_result["has_armenian"] == False
        assert poor_result["has_cta"] == False


@pytest.mark.asyncio
class TestOpenAIClient:
    """Test OpenAI client functionality"""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        mock_choice = Mock()
        mock_choice.message.content = "🔥 Մոկ գեներացված տեքստ հայերեն լեզվով։ Այս տեքստը ստեղծվել է ստուգման նպատակով։ Գնել հիմա!"
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        return mock_response
    
    @pytest.fixture
    def openai_client(self):
        """Create OpenAI client for testing"""
        with patch('bot.ai.openai_client.config') as mock_config:
            mock_config.OPENAI_API_KEY = "test-key"
            mock_config.OPENAI_MODEL = "gpt-4o-mini"
            mock_config.OPENAI_MAX_TOKENS = 200
            mock_config.OPENAI_TEMPERATURE = 0.7
            
            return OpenAIClient()
    
    async def test_generate_post_text(self, openai_client, mock_openai_response):
        """Test post text generation"""
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await openai_client.generate_post_text(
                post_format="selling",
                keywords="test keywords",
                additional_details="test details"
            )
            
            assert isinstance(result, str)
            assert len(result) > 10
            assert is_armenian_text(result)
    
    async def test_generate_post_text_all_formats(self, openai_client, mock_openai_response):
        """Test text generation for all post formats"""
        formats = ["selling", "collection", "info", "promo"]
        
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            for post_format in formats:
                result = await openai_client.generate_post_text(
                    post_format=post_format,
                    keywords=f"test keywords for {post_format}"
                )
                
                assert isinstance(result, str)
                assert len(result) > 0
    
    async def test_improve_text(self, openai_client, mock_openai_response):
        """Test text improvement functionality"""
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            original_text = "Սա բնօրինակ տեքստ է"
            instructions = "Ավելացրու էմոջիներ"
            
            result = await openai_client.improve_text(original_text, instructions)
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    async def test_translate_text(self, openai_client):
        """Test text translation"""
        # Mock translation response
        mock_choice = Mock()
        mock_choice.message.content = "This is translated text"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
            result = await openai_client.translate_text(
                text="Սա հայերեն տեքստ է",
                target_language="en"
            )
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    async def test_check_content_quality(self, openai_client):
        """Test content quality checking"""
        # Mock quality response
        mock_choice = Mock()
        mock_choice.message.content = '''
        {
            "score": 8,
            "strengths": ["Լավ կառուցվածք", "Հստակ գործողության կոչ"],
            "weaknesses": ["Քիչ էմոջիներ"],
            "suggestions": ["Ավելացնել էմոջիներ", "Կրճատել տեքստը"]
        }
        '''
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
            result = await openai_client.check_content_quality("Սա ստուգման տեքստ է")
            
            assert isinstance(result, dict)
            assert "score" in result
            assert "strengths" in result
            assert "weaknesses" in result
            assert "suggestions" in result
    
    async def test_test_connection_success(self, openai_client, mock_openai_response):
        """Test successful connection test"""
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await openai_client.test_connection()
            assert result == True
    
    async def test_test_connection_failure(self, openai_client):
        """Test connection test failure"""
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(side_effect=Exception("Connection failed"))):
            result = await openai_client.test_connection()
            assert result == False
    
    async def test_generate_post_text_failure(self, openai_client):
        """Test handling of generation failures"""
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(side_effect=Exception("API Error"))):
            result = await openai_client.generate_post_text(
                post_format="selling",
                keywords="test"
            )
            
            assert result is None
    
    async def test_improve_text_failure(self, openai_client):
        """Test handling of text improvement failures"""
        with patch.object(openai_client.client.chat.completions, 'create', new=AsyncMock(side_effect=Exception("API Error"))):
            result = await openai_client.improve_text("original", "instructions")
            assert result is None


class TestPromptValidation:
    """Test prompt validation and structure"""
    
    def test_system_prompt_structure(self):
        """Test that system prompt has required elements"""
        prompt = get_system_prompt()
        
        # Check for key elements
        assert "ShoppingTime" in prompt
        assert "4 ձևաչափով" in prompt  # 4 formats in Armenian
        
        # Check for format mentions
        format_keywords = ["վաճառող", "ընտրանի", "տեղեկատվական", "ակցիա"]
        for keyword in format_keywords:
            assert keyword.lower() in prompt.lower()
    
    def test_user_prompt_structure(self):
        """Test user prompt includes all required elements"""
        prompt = get_user_prompt("selling", "test keywords", "additional details")
        
        # Check structure
        assert "ձևաչափ" in prompt.lower()  # Format
        assert "բանալի բառեր" in prompt.lower()  # Keywords
        assert "test keywords" in prompt
        assert "additional details" in prompt
    
    def test_format_specific_prompts(self):
        """Test that each format has specific instructions"""
        for format_key in POST_FORMAT_PROMPTS:
            format_data = POST_FORMAT_PROMPTS[format_key]
            
            # Check structure
            assert "armenian" in format_data
            assert "cta_examples" in format_data
            
            # Check Armenian prompt content
            armenian_prompt = format_data["armenian"]
            assert len(armenian_prompt) > 50
            assert is_armenian_text(armenian_prompt)
            
            # Check CTA examples
            cta_examples = format_data["cta_examples"]
            assert isinstance(cta_examples, list)
            assert len(cta_examples) > 0
            
            for cta in cta_examples:
                assert isinstance(cta, str)
                assert is_armenian_text(cta)


class TestErrorHandling:
    """Test error handling in AI components"""
    
    def test_invalid_post_format(self):
        """Test handling of invalid post format"""
        # Should not raise exception, should handle gracefully
        prompt = get_user_prompt("invalid_format", "keywords")
        assert isinstance(prompt, str)
        
        cta_examples = get_cta_examples("invalid_format")
        assert isinstance(cta_examples, list)
    
    def test_empty_keywords(self):
        """Test handling of empty keywords"""
        prompt = get_user_prompt("selling", "")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_none_values(self):
        """Test handling of None values"""
        prompt = get_user_prompt("selling", None, None)
        assert isinstance(prompt, str)
    
    def test_validate_armenian_post_edge_cases(self):
        """Test validation with edge cases"""
        # Empty text
        result = validate_armenian_post("")
        assert result["score"] < 5
        assert len(result["issues"]) > 0
        
        # Very long text
        long_text = "Բառ " * 200  # 200 words
        result = validate_armenian_post(long_text)
        assert "երկար" in " ".join(result["issues"]).lower() or result["score"] < 10
        
        # Only emojis
        result = validate_armenian_post("🔥🔥🔥")
        assert result["score"] < 5


class TestIntegration:
    """Integration tests for AI components"""
    
    @pytest.mark.asyncio
    async def test_full_post_generation_workflow(self):
        """Test complete post generation workflow"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_client.generate_post_text = AsyncMock(return_value="🔥 Գեներացված տեքստ հայերեն լեզվով։ Այս տեքստը ստեղծվել է ավտոմատ կերպով։ Գնել հիմա!")
        
        # Test workflow
        post_format = "selling"
        keywords = "փոստ, գեներացիա, ստուգում"
        
        # Generate text
        generated_text = await mock_client.generate_post_text(post_format, keywords)
        
        # Validate generated text
        validation = validate_armenian_post(generated_text)
        
        # Assertions
        assert generated_text is not None
        assert validation["has_armenian"] == True
        assert validation["word_count"] > 10
        assert validation["score"] >= 6
    
    def test_prompt_and_format_consistency(self):
        """Test consistency between prompts and format definitions"""
        all_formats = get_all_formats()
        
        # Check that all formats have prompts
        for format_key in all_formats:
            assert format_key in POST_FORMAT_PROMPTS
            
            # Check format name exists
            format_name = get_format_name(format_key)
            assert format_name != format_key  # Should be translated
            
            # Check CTA examples exist
            cta_examples = get_cta_examples(format_key)
            assert len(cta_examples) > 0
            
            # Check emojis exist
            emojis = get_format_emojis(format_key)
            assert len(emojis) > 0


if __name__ == "__main__":
    # Run specific test classes for debugging
    pytest.main([__file__ + "::TestPrompts", "-v"])
    pytest.main([__file__ + "::TestArmenianTextUtils", "-v"])
    pytest.main([__file__ + "::TestOpenAIClient", "-v"])