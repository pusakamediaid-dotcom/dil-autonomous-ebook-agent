"""
DIL Autonomous Ebook Agent - API Client Module

Jembatan tunggal untuk memanggil berbagai provider AI API.
Mendukung OpenAI, Gemini, dan OpenRouter (OpenAI-compatible).
"""

import json
import time
from typing import Dict, Any, Optional, List

from .logger import get_logger

logger = get_logger(__name__)


class AIClient:
    """
    Klien unified untuk berbagai provider AI.
    Menyediakan interface tunggal untuk generate teks.
    """
    
    def __init__(self):
        """Inisialisasi AIClient."""
        self.last_response: Optional[Dict[str, Any]] = None
        self.last_error: Optional[str] = None
        self.request_count: int = 0
    
    def generate_text(
        self,
        prompt: str,
        provider_config: Dict[str, Any],
        api_key: str,
        model_type: str = "fast"
    ) -> Dict[str, Any]:
        """
        Generate teks menggunakan provider yang ditentukan.
        
        Args:
            prompt: Prompt untuk generate.
            provider_config: Konfigurasi provider dari model_pool.json.
            api_key: API key untuk provider.
            model_type: Tipe model ("fast" atau "strong").
        
        Returns:
            Dictionary dengan 'success', 'text', dan 'error'.
        """
        sdk_type = provider_config.get("sdk_type", "")
        
        if sdk_type == "openai":
            return self._call_openai(prompt, provider_config, api_key, model_type)
        elif sdk_type == "google-genai":
            return self._call_gemini(prompt, provider_config, api_key, model_type)
        elif sdk_type == "openai-compatible":
            return self._call_openai_compatible(prompt, provider_config, api_key, model_type)
        else:
            return self._safe_error(f"SDK type tidak didukung: {sdk_type}")
    
    def _call_openai(
        self,
        prompt: str,
        provider_config: Dict[str, Any],
        api_key: str,
        model_type: str
    ) -> Dict[str, Any]:
        """
        Memanggil OpenAI API.
        
        Args:
            prompt: Prompt teks.
            provider_config: Konfigurasi provider.
            api_key: API key OpenAI.
            model_type: "fast" atau "strong".
        
        Returns:
            Response dictionary.
        """
        try:
            import urllib.request
            import urllib.error
            
            model_id = (
                provider_config.get("model_strong") if model_type == "strong"
                else provider_config.get("model_fast", "gpt-4o-mini")
            )
            
            base_url = provider_config.get("base_url", "https://api.openai.com/v1")
            url = f"{base_url}/chat/completions"
            
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "Anda adalah penulis ebook teknis yang kompeten. Tulis dalam Bahasa Indonesia yang rapi dan profesional."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return self._extract_text_response(result, "openai")
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            logger.error(f"OpenAI HTTP Error: {e.code} - {error_body[:200]}")
            return self._safe_error(f"OpenAI HTTP Error: {e.code}")
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            return self._safe_error(f"OpenAI Error: {str(e)}")
    
    def _call_gemini(
        self,
        prompt: str,
        provider_config: Dict[str, Any],
        api_key: str,
        model_type: str
    ) -> Dict[str, Any]:
        """
        Memanggil Google Gemini API.
        
        Args:
            prompt: Prompt teks.
            provider_config: Konfigurasi provider.
            api_key: API key Gemini.
            model_type: "fast" atau "strong".
        
        Returns:
            Response dictionary.
        """
        try:
            import urllib.request
            import urllib.error
            
            model_id = (
                provider_config.get("model_strong") if model_type == "strong"
                else provider_config.get("model_fast", "gemini-1.5-flash")
            )
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2000
                }
            }
            
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return self._extract_gemini_response(result)
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            logger.error(f"Gemini HTTP Error: {e.code} - {error_body[:200]}")
            return self._safe_error(f"Gemini HTTP Error: {e.code}")
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return self._safe_error(f"Gemini Error: {str(e)}")
    
    def _call_openai_compatible(
        self,
        prompt: str,
        provider_config: Dict[str, Any],
        api_key: str,
        model_type: str
    ) -> Dict[str, Any]:
        """
        Memanggil OpenAI-compatible API (misalnya OpenRouter).
        
        Args:
            prompt: Prompt teks.
            provider_config: Konfigurasi provider.
            api_key: API key.
            model_type: "fast" atau "strong".
        
        Returns:
            Response dictionary.
        """
        try:
            import urllib.request
            import urllib.error
            
            model_id = (
                provider_config.get("model_strong") if model_type == "strong"
                else provider_config.get("model_fast", "openrouter/auto")
            )
            
            base_url = provider_config.get("base_url", "https://openrouter.ai/api/v1")
            url = f"{base_url}/chat/completions"
            
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "You are a competent technical ebook writer. Write in clean, professional Indonesian."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                    'HTTP-Referer': 'https://pusaka.media.id',
                    'X-Title': 'DIL Ebook Agent'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return self._extract_text_response(result, "openai-compatible")
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            logger.error(f"OpenRouter HTTP Error: {e.code} - {error_body[:200]}")
            return self._safe_error(f"OpenRouter HTTP Error: {e.code}")
        except Exception as e:
            logger.error(f"OpenRouter API Error: {e}")
            return self._safe_error(f"OpenRouter Error: {str(e)}")
    
    def _extract_text_response(self, result: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Mengekstrak teks dari response OpenAI-style.
        
        Args:
            result: Response dictionary.
            source: Sumber provider.
        
        Returns:
            Dictionary dengan text atau error.
        """
        try:
            choices = result.get("choices", [])
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                
                self.last_response = result
                self.request_count += 1
                
                logger.info(f"{source.upper()} response received ({len(content)} chars)")
                
                return {
                    "success": True,
                    "text": content,
                    "source": source,
                    "model": result.get("model", "unknown"),
                    "usage": result.get("usage", {})
                }
            else:
                return self._safe_error(f"Response tidak memiliki choices: {source}")
        except Exception as e:
            return self._safe_error(f"Error extracting response: {str(e)}")
    
    def _extract_gemini_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mengekstrak teks dari response Gemini.
        
        Args:
            result: Response dictionary.
        
        Returns:
            Dictionary dengan text atau error.
        """
        try:
            candidates = result.get("candidates", [])
            if candidates and len(candidates) > 0:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                
                if parts and len(parts) > 0:
                    text = parts[0].get("text", "")
                    
                    self.last_response = result
                    self.request_count += 1
                    
                    logger.info(f"Gemini response received ({len(text)} chars)")
                    
                    return {
                        "success": True,
                        "text": text,
                        "source": "gemini",
                        "model": result.get("model", "unknown"),
                        "usage": result.get("usageMetadata", {})
                    }
            
            return self._safe_error("Response tidak memiliki candidates")
        except Exception as e:
            return self._safe_error(f"Error extracting Gemini response: {str(e)}")
    
    def _safe_error(self, error_message: str) -> Dict[str, Any]:
        """
        Membuat response error yang aman (tidak mengandung data sensitif).
        
        Args:
            error_message: Pesan error.
        
        Returns:
            Dictionary error.
        """
        self.last_error = error_message
        logger.error(f"API Error: {error_message}")
        
        return {
            "success": False,
            "text": "",
            "error": error_message,
            "source": "unknown"
        }
    
    def safe_error_response(self, context: str) -> str:
        """
        Membuat pesan error yang aman untuk digunakan dalam ebook.
        
        Args:
            context: Konteks operasi yang gagal.
        
        Returns:
            Pesan error yang aman untuk ditampilkan.
        """
        return f"Konten untuk bagian ini sedang dalam pemrosesan. Silakan refresh nanti atau hubungi administrator jika masalah berlanjut."
    
    def get_stats(self) -> Dict[str, Any]:
        """Mendapatkan statistik request."""
        return {
            "request_count": self.request_count,
            "last_error": self.last_error,
            "has_last_response": self.last_response is not None
        }


def get_ai_client() -> AIClient:
    """Mendapatkan atau membuat instance AIClient global."""
    global _global_ai_client
    if '_global_ai_client' not in globals():
        _global_ai_client = AIClient()
    return _global_ai_client