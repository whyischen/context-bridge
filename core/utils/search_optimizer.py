"""
Advanced Search Relevance Optimizer

This module provides sophisticated ranking algorithms for search results,
including BM25, TF-IDF, and hybrid scoring strategies.
"""

import re
import math
import logging
from typing import List, Dict, Any, Set, Tuple
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


class QueryProcessor:
    """Advanced query processing with tokenization, stemming, and expansion"""
    
    # Common English stop words
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have'
    }
    
    # Simple stemming rules (Porter-like)
    STEMMING_RULES = [
        (r'ing$', ''),
        (r'ed$', ''),
        (r'es$', ''),
        (r's$', ''),
        (r'ies$', 'y'),
        (r'tion$', 'te'),
        (r'ness$', ''),
    ]
    
    @classmethod
    def tokenize(cls, text: str, remove_stop_words: bool = True) -> List[str]:
        """
        Tokenize text into words with optional stop word removal
        
        Args:
            text: Input text
            remove_stop_words: Whether to remove common stop words
            
        Returns:
            List of tokens
        """
        # Extract words (alphanumeric + underscores)
        tokens = re.findall(r'\w+', text.lower())
        
        if remove_stop_words:
            tokens = [t for t in tokens if t not in cls.STOP_WORDS and len(t) > 1]
        
        return tokens
    
    @classmethod
    def stem(cls, word: str) -> str:
        """
        Apply simple stemming to a word
        
        Args:
            word: Input word
            
        Returns:
            Stemmed word
        """
        for pattern, replacement in cls.STEMMING_RULES:
            stemmed = re.sub(pattern, replacement, word)
            if stemmed != word:
                return stemmed
        return word
    
    @classmethod
    def process_query(cls, query: str) -> Dict[str, Any]:
        """
        Process query into structured format
        
        Args:
            query: Raw query string
            
        Returns:
            Dictionary with processed query components
        """
        # Tokenize
        tokens = cls.tokenize(query, remove_stop_words=False)
        tokens_no_stop = cls.tokenize(query, remove_stop_words=True)
        
        # Stem tokens
        stemmed = [cls.stem(t) for t in tokens_no_stop]
        
        # Extract phrases (quoted text)
        phrases = re.findall(r'"([^"]+)"', query)
        
        return {
            'original': query,
            'tokens': tokens,
            'tokens_no_stop': tokens_no_stop,
            'stemmed': stemmed,
            'phrases': phrases,
            'unique_terms': set(tokens_no_stop),
            'unique_stems': set(stemmed)
        }


class BM25Scorer:
    """
    BM25 (Best Matching 25) ranking algorithm
    
    BM25 is a probabilistic ranking function that considers:
    - Term frequency (TF)
    - Inverse document frequency (IDF)
    - Document length normalization
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 scorer
        
        Args:
            k1: Term frequency saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
        """
        self.k1 = k1
        self.b = b
        self.avg_doc_length = 0
        self.doc_count = 0
        self.doc_freq = defaultdict(int)  # Number of docs containing each term
        
    def compute_idf(self, term: str, total_docs: int) -> float:
        """
        Compute IDF (Inverse Document Frequency) for a term
        
        IDF = log((N - df + 0.5) / (df + 0.5) + 1)
        where N = total documents, df = document frequency
        """
        df = self.doc_freq.get(term, 0)
        return math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
    
    def score_document(
        self,
        query_terms: List[str],
        doc_terms: List[str],
        doc_length: int,
        total_docs: int
    ) -> float:
        """
        Calculate BM25 score for a document
        
        Args:
            query_terms: List of query terms
            doc_terms: List of document terms
            doc_length: Length of document
            total_docs: Total number of documents in collection
            
        Returns:
            BM25 score
        """
        if not query_terms or not doc_terms:
            return 0.0
        
        # Count term frequencies in document
        doc_term_freq = Counter(doc_terms)
        
        score = 0.0
        for term in query_terms:
            if term not in doc_term_freq:
                continue
            
            # Term frequency in document
            tf = doc_term_freq[term]
            
            # IDF component
            idf = self.compute_idf(term, total_docs)
            
            # Length normalization
            norm = 1 - self.b + self.b * (doc_length / self.avg_doc_length if self.avg_doc_length > 0 else 1)
            
            # BM25 formula
            score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * norm)
        
        return score


class AdvancedReranker:
    """
    Advanced reranking with multiple signals and adaptive weighting
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize reranker with configuration
        
        Args:
            config: Configuration dictionary with weights and parameters
        """
        self.config = config or {}
        
        # Default weights (can be overridden by config)
        self.weights = {
            'semantic': self.config.get('semantic_weight', 0.40),
            'bm25': self.config.get('bm25_weight', 0.30),
            'keyword': self.config.get('keyword_weight', 0.15),
            'position': self.config.get('position_weight', 0.10),
            'title': self.config.get('title_weight', 0.05),
        }
        
        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}
        
        self.bm25 = BM25Scorer(
            k1=self.config.get('bm25_k1', 1.5),
            b=self.config.get('bm25_b', 0.75)
        )
        
        logger.debug(f"AdvancedReranker initialized with weights: {self.weights}")
    
    def _calculate_keyword_score(
        self,
        query_data: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Tuple[float, Dict[str, int]]:
        """
        Calculate keyword matching score with stemming
        
        Returns:
            Tuple of (score, matched_keywords_dict)
        """
        # Get content to search
        abstract = result.get('abstract', '').lower()
        excerpts = " ".join(result.get('relevant_excerpts', [])).lower()
        content = f"{abstract} {excerpts}"
        
        # Tokenize content
        content_tokens = QueryProcessor.tokenize(content, remove_stop_words=False)
        content_stems = set(QueryProcessor.stem(t) for t in content_tokens)
        
        # Match original terms
        matched_keywords = {}
        for term in query_data['tokens_no_stop']:
            count = content.count(term)
            if count > 0:
                matched_keywords[term] = count
        
        # Match stemmed terms (with lower weight)
        for stem in query_data['unique_stems']:
            if stem in content_stems and stem not in matched_keywords:
                matched_keywords[f"{stem}*"] = 1  # Mark as stemmed match
        
        # Calculate match ratio
        total_terms = len(query_data['unique_terms'])
        matched_count = len([k for k in matched_keywords.keys() if not k.endswith('*')])
        stemmed_count = len([k for k in matched_keywords.keys() if k.endswith('*')])
        
        # Score: full matches count more than stemmed matches
        score = (matched_count + 0.5 * stemmed_count) / total_terms if total_terms > 0 else 0
        
        return score, matched_keywords
    
    def _calculate_bm25_score(
        self,
        query_data: Dict[str, Any],
        result: Dict[str, Any],
        total_docs: int
    ) -> float:
        """Calculate BM25 score for result"""
        # Combine abstract and excerpts
        abstract = result.get('abstract', '')
        excerpts = " ".join(result.get('relevant_excerpts', []))
        content = f"{abstract} {excerpts}"
        
        # Tokenize document
        doc_tokens = QueryProcessor.tokenize(content, remove_stop_words=True)
        doc_length = len(doc_tokens)
        
        # Calculate BM25
        score = self.bm25.score_document(
            query_terms=query_data['tokens_no_stop'],
            doc_terms=doc_tokens,
            doc_length=doc_length,
            total_docs=total_docs
        )
        
        # Normalize to 0-1 range (approximate)
        normalized = 1 - math.exp(-score / 10)
        
        return normalized
    
    def _calculate_position_score(self, result: Dict[str, Any], position: int, total: int) -> float:
        """
        Calculate position-based score (earlier results get slight boost)
        
        Uses exponential decay: score = exp(-position / decay_factor)
        """
        decay_factor = total / 3  # Top 1/3 get significant boost
        return math.exp(-position / max(decay_factor, 1))
    
    def _calculate_title_score(
        self,
        query_data: Dict[str, Any],
        result: Dict[str, Any]
    ) -> float:
        """Calculate score boost for title/filename matches"""
        filename = result.get('filename', '').lower()
        uri = result.get('uri', '').lower()
        
        # Check if query terms appear in filename/URI
        matches = 0
        for term in query_data['tokens_no_stop']:
            if term in filename or term in uri:
                matches += 1
        
        return matches / len(query_data['tokens_no_stop']) if query_data['tokens_no_stop'] else 0
    
    def _calculate_phrase_bonus(
        self,
        query_data: Dict[str, Any],
        result: Dict[str, Any]
    ) -> float:
        """Calculate bonus for exact phrase matches"""
        if not query_data['phrases']:
            return 0.0
        
        content = f"{result.get('abstract', '')} {' '.join(result.get('relevant_excerpts', []))}".lower()
        
        matches = sum(1 for phrase in query_data['phrases'] if phrase.lower() in content)
        return matches / len(query_data['phrases'])
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        explain: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Rerank results using multiple signals
        
        Args:
            query: Original query string
            results: List of search results
            explain: Whether to add explanation metadata
            
        Returns:
            Reranked results with updated scores
        """
        if not results:
            return results
        
        # Process query
        query_data = QueryProcessor.process_query(query)
        total_docs = len(results)
        
        # Calculate average document length for BM25
        doc_lengths = []
        for result in results:
            content = f"{result.get('abstract', '')} {' '.join(result.get('relevant_excerpts', []))}"
            doc_lengths.append(len(QueryProcessor.tokenize(content)))
        self.bm25.avg_doc_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0
        
        # Score each result
        for idx, result in enumerate(results):
            # Get original semantic score
            semantic_score = result.get('original_score', result.get('score', 0.0))
            
            # Calculate component scores
            keyword_score, matched_kw = self._calculate_keyword_score(query_data, result)
            bm25_score = self._calculate_bm25_score(query_data, result, total_docs)
            position_score = self._calculate_position_score(result, idx, total_docs)
            title_score = self._calculate_title_score(query_data, result)
            phrase_bonus = self._calculate_phrase_bonus(query_data, result)
            
            # Combine scores with weights
            final_score = (
                self.weights['semantic'] * semantic_score +
                self.weights['bm25'] * bm25_score +
                self.weights['keyword'] * keyword_score +
                self.weights['position'] * position_score +
                self.weights['title'] * title_score +
                phrase_bonus * 0.1  # Phrase bonus is additive
            )
            
            # Update result
            result['score'] = final_score
            
            if explain:
                result['score_breakdown'] = {
                    'semantic': semantic_score,
                    'bm25': bm25_score,
                    'keyword': keyword_score,
                    'position': position_score,
                    'title': title_score,
                    'phrase_bonus': phrase_bonus,
                    'final': final_score
                }
                result['matched_keywords'] = matched_kw
                result['query_terms'] = query_data['tokens_no_stop']
        
        # Sort by final score
        results.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        
        return results


class SearchOptimizer:
    """
    Main search optimizer interface
    """
    
    @staticmethod
    def optimize_results(
        query: str,
        results: List[Dict[str, Any]],
        config: Dict[str, Any] = None,
        explain: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Optimize search results using advanced ranking
        
        Args:
            query: Search query
            results: Raw search results
            config: Optimizer configuration
            explain: Whether to include explanation metadata
            
        Returns:
            Optimized and reranked results
        """
        if not results:
            return results
        
        # Store original scores
        for result in results:
            if 'original_score' not in result:
                result['original_score'] = result.get('score', 0.0)
        
        # Apply advanced reranking
        reranker = AdvancedReranker(config)
        optimized = reranker.rerank(query, results, explain=explain)
        
        return optimized
