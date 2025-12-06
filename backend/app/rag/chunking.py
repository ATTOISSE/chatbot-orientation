"""
COMMIT 8: Document Chunking Strategy for RAG
Stratégie de chunking intelligente pour les documents de formations

Techniques implémentées:
1. Semantic chunking - Split par contexte sémantique
2. Sliding window - Chevauchement pour contexte
3. Metadata preservation - Garder les métadonnées
4. Size optimization - Optimiser la taille des chunks
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class Chunk:
    """Représente un chunk de document"""
    
    content: str  # Contenu du chunk
    metadata: Dict  # Métadonnées (source, formation_id, etc.)
    start_pos: int  # Position de départ dans le document original
    end_pos: int  # Position de fin
    chunk_id: str  # ID unique du chunk
    
    def __repr__(self):
        return f"<Chunk(id={self.chunk_id}, size={len(self.content)}, source={self.metadata.get('source', 'unknown')})>"


class DocumentChunker:
    """
    Classe pour le chunking intelligent de documents de formations
    """
    
    def __init__(
        self,
        chunk_size: int = 512,  # Tokens équivalent (~2048 caractères)
        chunk_overlap: int = 128,  # Chevauchement (~512 caractères)
        min_chunk_size: int = 100,  # Taille minimale
        max_chunk_size: int = 1024,  # Taille maximale
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.chunk_counter = 0
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict,
        strategy: str = "semantic"
    ) -> List[Chunk]:
        """
        Chunk un document texte en plusieurs parties
        
        Args:
            text: Le texte à chunker
            metadata: Métadonnées du document
            strategy: 'semantic', 'paragraph', 'sentence', 'sliding_window'
        
        Returns:
            Liste de Chunk objects
        """
        
        if strategy == "semantic":
            return self._chunk_semantic(text, metadata)
        elif strategy == "paragraph":
            return self._chunk_paragraph(text, metadata)
        elif strategy == "sentence":
            return self._chunk_sentence(text, metadata)
        elif strategy == "sliding_window":
            return self._chunk_sliding_window(text, metadata)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    def _chunk_semantic(self, text: str, metadata: Dict) -> List[Chunk]:
        """
        Chunking sémantique - Split par sections logiques
        
        Détecte:
        - Les titres et sections
        - Les paragraphes
        - Les listes
        - Les énumérations
        """
        
        chunks = []
        sections = self._extract_sections(text)
        
        for section_title, section_content in sections:
            # Pour chaque section, créer des chunks
            if len(section_content) <= self.max_chunk_size:
                # Si la section est petite, créer un seul chunk
                chunk = self._create_chunk(
                    section_content,
                    metadata,
                    section_title=section_title,
                    text=text
                )
                chunks.append(chunk)
            else:
                # Si grande section, subdiviser
                sub_chunks = self._chunk_paragraph(section_content, metadata)
                for sub_chunk in sub_chunks:
                    sub_chunk.metadata["section"] = section_title
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _chunk_paragraph(self, text: str, metadata: Dict) -> List[Chunk]:
        """Chunking par paragraphe avec sliding window"""
        
        # Split par paragraphes (double newline)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        buffer = []
        buffer_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if buffer_size + para_size <= self.chunk_size:
                # Ajouter au buffer actuel
                buffer.append(para)
                buffer_size += para_size + 2  # +2 pour les newlines
            else:
                # Buffer est plein, créer un chunk
                if buffer:
                    chunk_text = "\n\n".join(buffer)
                    chunk = self._create_chunk(chunk_text, metadata, text=text)
                    chunks.append(chunk)
                
                # Commencer nouveau buffer avec chevauchement
                buffer = [para]
                buffer_size = para_size
        
        # Dernier chunk
        if buffer:
            chunk_text = "\n\n".join(buffer)
            chunk = self._create_chunk(chunk_text, metadata, text=text)
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_sentence(self, text: str, metadata: Dict) -> List[Chunk]:
        """Chunking par phrase"""
        
        # Split par phrases (simple regex)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        buffer = []
        buffer_size = 0
        
        for sentence in sentences:
            sent_size = len(sentence)
            
            if buffer_size + sent_size <= self.chunk_size:
                buffer.append(sentence)
                buffer_size += sent_size + 1
            else:
                if buffer:
                    chunk_text = " ".join(buffer)
                    chunk = self._create_chunk(chunk_text, metadata, text=text)
                    chunks.append(chunk)
                
                buffer = [sentence]
                buffer_size = sent_size
        
        if buffer:
            chunk_text = " ".join(buffer)
            chunk = self._create_chunk(chunk_text, metadata, text=text)
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_sliding_window(self, text: str, metadata: Dict) -> List[Chunk]:
        """Chunking avec sliding window pour maximum de contexte"""
        
        # Convertir en caractères pour simplifier
        text_len = len(text)
        chunks = []
        
        # Trouver les bonnes limites (word boundaries)
        start = 0
        while start < text_len:
            # Calculer la fin du chunk
            end = min(start + self.chunk_size, text_len)
            
            # Ajuster pour word boundary
            if end < text_len:
                # Chercher le dernier espace avant end
                space_pos = text.rfind(' ', start, end)
                if space_pos > start:
                    end = space_pos
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= self.min_chunk_size:
                chunk = self._create_chunk(
                    chunk_text,
                    metadata,
                    text=text,
                    start_pos=start,
                    end_pos=end
                )
                chunks.append(chunk)
            
            # Avancer avec chevauchement
            start = end - self.chunk_overlap
        
        return chunks
    
    def _extract_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Extraire les sections du texte
        
        Détecte les patterns:
        - # Titre
        - ## Sous-titre
        - - Listes
        """
        
        sections = []
        current_section = "Introduction"
        current_content = []
        
        for line in text.split('\n'):
            # Détect header (markdown style)
            if line.startswith('#'):
                # Sauvegarder la section précédente
                if current_content:
                    content = '\n'.join(current_content).strip()
                    if content:
                        sections.append((current_section, content))
                
                # Nouvelle section
                current_section = re.sub(r'^#+\s*', '', line).strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Dernière section
        if current_content:
            content = '\n'.join(current_content).strip()
            if content:
                sections.append((current_section, content))
        
        return sections if sections else [("Full Document", text)]
    
    def _create_chunk(
        self,
        content: str,
        metadata: Dict,
        section_title: Optional[str] = None,
        text: Optional[str] = None,
        start_pos: int = 0,
        end_pos: int = 0
    ) -> Chunk:
        """Créer un objet Chunk avec métadonnées"""
        
        self.chunk_counter += 1
        
        # Calculer positions si non fourni
        if text and start_pos == 0 and end_pos == 0:
            start_pos = text.find(content)
            end_pos = start_pos + len(content) if start_pos >= 0 else 0
        
        chunk_metadata = metadata.copy()
        if section_title:
            chunk_metadata["section"] = section_title
        
        chunk_metadata["chunk_size"] = len(content)
        chunk_metadata["word_count"] = len(content.split())
        
        return Chunk(
            content=content,
            metadata=chunk_metadata,
            start_pos=start_pos,
            end_pos=end_pos,
            chunk_id=f"{metadata.get('formation_id', 'unknown')}_{self.chunk_counter}"
        )
    
    def chunk_formation(
        self,
        formation_data: Dict,
        strategy: str = "semantic"
    ) -> List[Chunk]:
        """
        Chunk une formation complète avec toutes ses informations
        
        Args:
            formation_data: Dict avec intitule, description, objectifs, debouches, etc.
            strategy: Stratégie de chunking
        
        Returns:
            Liste de chunks
        """
        
        chunks = []
        
        # Métadonnées communes
        base_metadata = {
            "formation_id": formation_data.get("id"),
            "intitule": formation_data.get("intitule"),
            "etablissement": formation_data.get("etablissement"),
            "ville": formation_data.get("ville"),
            "domaine": formation_data.get("domaine"),
            "type": "formation_metadata"
        }
        
        # Chunker chaque field important
        fields_to_chunk = [
            ("intitule", formation_data.get("intitule")),
            ("description", formation_data.get("description")),
            ("objectifs", formation_data.get("objectifs")),
            ("conditions_admission", formation_data.get("conditions_admission")),
            ("debouches", formation_data.get("debouches")),
        ]
        
        for field_name, field_content in fields_to_chunk:
            if field_content and len(field_content.strip()) > 50:
                # Chunker ce field
                meta = base_metadata.copy()
                meta["field"] = field_name
                meta["source"] = f"formation_{field_name}"
                
                field_chunks = self.chunk_text(
                    field_content,
                    meta,
                    strategy=strategy
                )
                chunks.extend(field_chunks)
        
        return chunks


class TextPreprocessor:
    """Prétraitement du texte avant chunking"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Nettoyer le texte"""
        
        if not text:
            return ""
        
        # Normaliser les whitespaces
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les caractères spéciaux problématiques
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, n: int = 10) -> List[str]:
        """Extraire les keywords du texte"""
        
        # Mots vides français
        stopwords = {
            'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'des',
            'et', 'ou', 'mais', 'donc', 'car', 'par', 'pour', 'avec',
            'sans', 'sous', 'sur', 'entre', 'dans', 'vers', 'à', 'au',
            'en', 'est', 'son', 'ses', 'ce', 'cet', 'cette', 'ces',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'moi', 'toi', 'lui', 'elle', 'nous', 'vous', 'eux', 'elles'
        }
        
        # Extraire les mots
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # Filtrer les stopwords
        keywords = [w for w in words if w not in stopwords]
        
        # Compter et récupérer les top N
        from collections import Counter
        top_keywords = Counter(keywords).most_common(n)
        
        return [kw[0] for kw in top_keywords]
