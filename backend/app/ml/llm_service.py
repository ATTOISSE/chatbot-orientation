"""
COMMIT 12: LLM Integration - Local LLM Service
Service pour intégrer des modèles LLM locaux (Ollama, LLaMA, etc.)

Sans dépendances externes obligatoires.
Fallback gracieux si LLM non disponible.
"""

import logging
import requests
import json
from typing import Optional, AsyncGenerator, List, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration du modèle LLM"""
    model_name: str = "llama2"
    api_url: str = "http://localhost:11434"
    temperature: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    max_tokens: int = 512
    timeout: int = 30


class LLMModel(ABC):
    """Interface abstraite pour les modèles LLM"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Générer du texte"""
        pass
    
    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Générer du texte en streaming"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Vérifier si le modèle est disponible"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict:
        """Obtenir les infos du modèle"""
        pass


class OllamaLLM(LLMModel):
    """
    Intégration avec Ollama (LLM local)
    Supporte tous les modèles Ollama: llama2, mistral, neural-chat, etc.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None, **kwargs):
        # Support pour les deux styles d'initialisation
        if config is None:
            config = LLMConfig(**kwargs)
        self.config = config
        self.model_name = config.model_name
        self.temperature = config.temperature
        self.available = False
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Vérifier que le serveur Ollama est actif"""
        try:
            response = requests.get(
                f"{self.config.api_url}/api/tags",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.available = True
                logger.info(f"Ollama available at {self.config.api_url}")
                
                # Vérifier que le modèle demandé existe
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                
                if self.config.model_name not in model_names:
                    logger.warning(
                        f"Model {self.config.model_name} not found. "
                        f"Available: {', '.join(model_names)}"
                    )
                    self.available = False
                
                return self.available
        
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self.available = False
            return False
    
    def is_available(self) -> bool:
        """Vérifier la disponibilité"""
        if not self.available:
            self._check_availability()
        return self.available
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Générer du texte avec Ollama
        
        Args:
            prompt: Texte d'entrée
            **kwargs: Options additionnelles (temperature, top_k, etc.)
        
        Returns:
            Texte généré
        """
        
        if not self.is_available():
            logger.error("Ollama not available")
            return ""
        
        try:
            # Merger les paramètres
            params = {
                "model": self.config.model_name,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_k": kwargs.get("top_k", self.config.top_k),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "num_predict": kwargs.get("num_predict", self.config.max_tokens),
                "stream": False
            }
            
            response = requests.post(
                f"{self.config.api_url}/api/generate",
                json=params,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return ""
        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return ""
    
    async def stream_generate(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Générer du texte en streaming avec Ollama
        
        Args:
            prompt: Texte d'entrée
            **kwargs: Options additionnelles
        
        Yields:
            Chunks de texte générés
        """
        
        if not self.is_available():
            logger.error("Ollama not available")
            return
        
        try:
            # Merger les paramètres
            params = {
                "model": self.config.model_name,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_k": kwargs.get("top_k", self.config.top_k),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "num_predict": kwargs.get("num_predict", self.config.max_tokens),
                "stream": True
            }
            
            response = requests.post(
                f"{self.config.api_url}/api/generate",
                json=params,
                timeout=self.config.timeout,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            text = chunk.get("response", "")
                            if text:
                                yield text
                        except json.JSONDecodeError:
                            pass
            else:
                logger.error(f"Ollama stream error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
    
    def get_model_info(self) -> Dict:
        """Obtenir les infos du modèle"""
        try:
            response = requests.post(
                f"{self.config.api_url}/api/show",
                json={"name": self.config.model_name},
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                return response.json()
        
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
        
        return {}


class MockLLM(LLMModel):
    """
    LLM mock pour développement/test
    Retourne des réponses synthétisées sans dépendances
    """
    
    def __init__(self, config: Optional[LLMConfig] = None, **kwargs):
        self.config = config or LLMConfig(model_name="mock-llm")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Générer une réponse mock"""
        
        # Réponses génériques basées sur des mots-clés
        if "formation" in prompt.lower() or "course" in prompt.lower():
            return (
                "Basé sur votre question, je recommande de chercher une formation "
                "dans un domaine qui vous intéresse. Vous pouvez consulter notre "
                "catalogue complet de formations disponibles dans différentes villes "
                "du Sénégal."
            )
        
        elif "domaine" in prompt.lower():
            return (
                "Il existe plusieurs domaines de formation disponibles. "
                "Les plus populaires sont l'informatique, la gestion, "
                "les sciences et l'ingénierie. Quel domaine vous intéresse?"
            )
        
        elif "prix" in prompt.lower() or "cost" in prompt.lower():
            return (
                "Le coût des formations varie selon l'établissement et le domaine. "
                "Vous pouvez filtrer les formations par prix dans notre système de recherche."
            )
        
        else:
            return (
                "Je suis prêt à vous aider dans votre recherche de formation. "
                "Pouvez-vous préciser votre question ou le domaine qui vous intéresse?"
            )
    
    # Alias pour la compatibilité
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Alias pour generate"""
        return self.generate(prompt, **kwargs)
    
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Générer une réponse mock en streaming"""
        
        response = self.generate(prompt, **kwargs)
        
        # Envoyer par chunks de 20 caractères
        for i in range(0, len(response), 20):
            yield response[i:i+20]
    
    # Alias pour la compatibilité
    async def stream_response(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Alias pour stream_generate"""
        async for chunk in self.stream_generate(prompt, **kwargs):
            yield chunk
    
    def is_available(self) -> bool:
        """Toujours disponible"""
        return True
    
    def get_model_info(self) -> Dict:
        """Infos du mock"""
        return {
            "name": "mock-llm",
            "type": "mock",
            "description": "Mock LLM for development"
        }


class LLMService:
    """Service pour gérer l'intégration LLM"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> LLMModel:
        """Initialiser le LLM avec fallback"""
        
        # Essayer Ollama d'abord
        ollama = OllamaLLM(self.config)
        if ollama.is_available():
            logger.info(f"Using Ollama LLM: {self.config.model_name}")
            return ollama
        
        # Fallback vers le mock
        logger.warning("Ollama not available, using mock LLM")
        return MockLLM(self.config)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Générer une réponse
        
        Args:
            prompt: Texte d'entrée
            **kwargs: Options LLM
        
        Returns:
            Texte généré
        """
        return self.llm.generate(prompt, **kwargs)
    
    async def stream_response(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Générer une réponse en streaming
        
        Args:
            prompt: Texte d'entrée
            **kwargs: Options LLM
        
        Yields:
            Chunks de texte
        """
        async for chunk in self.llm.stream_generate(prompt, **kwargs):
            yield chunk
    
    def is_available(self) -> bool:
        """Vérifier la disponibilité du LLM"""
        return self.llm.is_available()
    
    def get_model_name(self) -> str:
        """Récupérer le nom du modèle"""
        return self.config.model_name
    
    def get_info(self) -> Dict:
        """Obtenir les infos du service"""
        return {
            "model": self.config.model_name,
            "api_url": self.config.api_url,
            "available": self.is_available(),
            "model_info": self.llm.get_model_info(),
            "type": type(self.llm).__name__
        }


class PromptBuilder:
    """Constructeur de prompts pour le chatbot"""
    
    @staticmethod
    def build_system_prompt() -> str:
        """
        Construire un prompt système pour le chatbot éducatif
        
        Returns:
            Prompt système en français
        """
        return """Tu es un assistant éducatif spécialisé dans l'orientation académique au Sénégal.
Ton rôle est d'aider les étudiants à trouver les formations qui correspondent à leurs besoins.

Règles:
- Sois précis et utile
- Mentionne les informations clés (ville, domaine, prix, établissement)
- Reste professionnel et encourageant
- Réponds en français
"""
    
    @staticmethod
    def build_chat_prompt(
        user_message: str,
        context: Optional[str] = None,
        system_role: str = "educateur"
    ) -> str:
        """
        Construire un prompt pour le chat
        
        Args:
            user_message: Message de l'utilisateur
            context: Contexte additionnel (formations, etc.)
            system_role: Rôle du système
        
        Returns:
            Prompt formaté
        """
        
        prompt = f"""You are a helpful {system_role} assistant specialized in educational guidance.
Your role is to help students find appropriate training and educational programs.

"""
        
        if context:
            prompt += f"Context information:\n{context}\n\n"
        
        prompt += f"User question: {user_message}\n\nAnswer:"
        
        return prompt
    
    @staticmethod
    def build_context_prompt(
        formations: List[Dict],
        user_message: str
    ) -> str:
        """
        Construire un prompt avec contexte de formations
        
        Args:
            formations: List de formations trouvées
            user_message: Message de l'utilisateur
        
        Returns:
            Prompt avec contexte
        """
        
        context = "Based on the following training programs:\n\n"
        
        for idx, formation in enumerate(formations[:5], 1):
            context += (
                f"{idx}. {formation.get('intitule', 'Formation')}\n"
                f"   Institution: {formation.get('etablissement', 'N/A')}\n"
                f"   City: {formation.get('ville', 'N/A')}\n"
                f"   Field: {formation.get('domaine', 'N/A')}\n"
                f"   Relevance: {formation.get('similarity', 0)*100:.1f}%\n\n"
            )
        
        return PromptBuilder.build_chat_prompt(
            user_message,
            context=context
        )
