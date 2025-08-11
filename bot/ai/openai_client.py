"""
OpenAI API client for TimeToShopping_bot
Handles text generation using GPT-4o-mini
"""

import asyncio
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from config import config  # ИСПРАВЛЕНО: убрал bot.
from bot.ai.prompts import get_system_prompt, get_user_prompt
from logging_config import logger  # ИСПРАВЛЕНО: убрал bot.

class OpenAIClient:
    """OpenAI API client for text generation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        self.max_tokens = config.OPENAI_MAX_TOKENS
        self.temperature = config.OPENAI_TEMPERATURE
    
    async def generate_post_text(
        self, 
        post_format: str, 
        keywords: str, 
        additional_details: str = ""
    ) -> Optional[str]:
        """
        Generate post text using OpenAI API
        
        Args:
            post_format: Type of post (selling, collection, info, promo)
            keywords: Keywords for the post
            additional_details: Additional context or requirements
            
        Returns:
            Generated text or None if failed
        """
        try:
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(post_format, keywords, additional_details)
            
            logger.info(f"Generating text for format: {post_format}")
            logger.debug(f"Keywords: {keywords}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            logger.info("Text generated successfully")
            logger.debug(f"Generated text length: {len(generated_text)} characters")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            return None
    
    async def improve_text(
        self, 
        original_text: str, 
        improvement_instructions: str
    ) -> Optional[str]:
        """
        Improve existing text based on instructions
        
        Args:
            original_text: Original text to improve
            improvement_instructions: Instructions in Armenian
            
        Returns:
            Improved text or None if failed
        """
        try:
            system_prompt = """
            Դու ShoppingTime ալիքի տեքստերի խմբագրիչն ես։ 
            Բարելավիր տրված տեքստը ըստ հրահանգների։
            Պահպանիր բնական ոճը և հայերեն լեզուն։
            Տեքստի երկարությունը թող մնա 50-90 բառ սահմաններում։
            """
            
            user_prompt = f"""
            Բնօրինակ տեքստ:
            {original_text}
            
            Բարելավման հրահանգներ:
            {improvement_instructions}
            
            Գրիր բարելավված տարբերակը:
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.5  # Lower temperature for editing
            )
            
            improved_text = response.choices[0].message.content.strip()
            
            logger.info("Text improved successfully")
            return improved_text
            
        except Exception as e:
            logger.error(f"Failed to improve text: {e}")
            return None
    
    async def translate_text(self, text: str, target_language: str = "ru") -> Optional[str]:
        """
        Translate text to another language
        
        Args:
            text: Text to translate
            target_language: Target language code (ru, en)
            
        Returns:
            Translated text or None if failed
        """
        try:
            lang_names = {"ru": "русский", "en": "английский"}
            target_lang_name = lang_names.get(target_language, target_language)
            
            system_prompt = f"""
            Դու թարգմանիչ ես։ Թարգմանիր տրված տեքստը {target_lang_name} լեզու։
            Պահպանիր բնօրինակ ոճն ու տոնը։ 
            Եթե տեքստում կան էմոջիներ, պահպանիր դրանք։
            """
            
            user_prompt = f"Թարգմանիր այս տեքստը:\n\n{text}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Low temperature for translation
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            logger.info(f"Text translated to {target_language}")
            return translated_text
            
        except Exception as e:
            logger.error(f"Failed to translate text: {e}")
            return None
    
    async def check_content_quality(self, text: str) -> Dict[str, Any]:
        """
        Check content quality and provide suggestions
        
        Args:
            text: Text to analyze
            
        Returns:
            Quality analysis dictionary
        """
        try:
            system_prompt = """
            Դու ShoppingTime ալիքի տեքստերի որակի գնահատող ես։
            Գնահատիր տրված տեքստի որակը և տուր առաջարկություններ։
            Պատասխանիր JSON ձևաչափով:
            {
                "score": 1-10,
                "strengths": ["դրական կողմեր"],
                "weaknesses": ["թույլ կողմեր"], 
                "suggestions": ["բարելավման առաջարկություններ"]
            }
            """
            
            user_prompt = f"Գնահատիր այս տեքստը:\n\n{text}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Try to parse JSON response
            import json
            try:
                quality_analysis = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                quality_analysis = {
                    "score": 7,
                    "strengths": ["Տեքստը գրված է"],
                    "weaknesses": ["Չհաջողվեց վերլուծել"],
                    "suggestions": ["Կրկին փորձել"]
                }
            
            logger.info("Content quality checked")
            return quality_analysis
            
        except Exception as e:
            logger.error(f"Failed to check content quality: {e}")
            return {
                "score": 5,
                "strengths": [],
                "weaknesses": ["Տեխնիկական սխալ"],
                "suggestions": ["Կրկին փորձել"]
            }
    
    async def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Ծրագրավորում"}],
                max_tokens=10
            )
            
            logger.info("OpenAI API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {e}")
            return False

# Global OpenAI client instance
openai_client = OpenAIClient()