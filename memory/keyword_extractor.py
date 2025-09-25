from collections import Counter
from typing import List, Dict
import re
import structlog

logger = structlog.get_logger()

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
    'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
    'it', 'we', 'they', 'them', 'their', 'what', 'which', 'who', 'when',
    'where', 'why', 'how', 'all', 'many', 'some', 'much', 'most', 'other',
    'another', 'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'my', 'your', 'our', 'his', 'her', 'its'
}

class KeywordExtractor:
    def __init__(self):
        self.user_keyword_history = {}
        
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        text_lower = text.lower()
        
        words = re.findall(r'\b[a-z]+\b', text_lower)
        
        filtered_words = [
            word for word in words 
            if len(word) >= min_length and word not in STOP_WORDS
        ]
        
        bigrams = []
        for i in range(len(words) - 1):
            if words[i] not in STOP_WORDS and words[i+1] not in STOP_WORDS:
                bigram = f"{words[i]} {words[i+1]}"
                bigrams.append(bigram)
        
        all_terms = filtered_words + bigrams
        
        term_counts = Counter(all_terms)
        
        keywords = [term for term, count in term_counts.most_common(10)]
        
        logger.debug("keywords_extracted", keywords=keywords[:5])
        
        return keywords
        
    def track_user_keywords(self, user_id: str, message: str) -> Dict[str, int]:
        keywords = self.extract_keywords(message)
        
        if user_id not in self.user_keyword_history:
            self.user_keyword_history[user_id] = Counter()
            
        self.user_keyword_history[user_id].update(keywords)
        
        keywords_with_3_plus = {
            keyword: count 
            for keyword, count in self.user_keyword_history[user_id].items()
            if count >= 3
        }
        
        if keywords_with_3_plus:
            logger.info(
                "keywords_threshold_reached",
                user_id=user_id,
                keywords=list(keywords_with_3_plus.keys())[:5]
            )
            
        return keywords_with_3_plus
        
    def get_user_top_keywords(self, user_id: str, limit: int = 10) -> List[tuple]:
        if user_id not in self.user_keyword_history:
            return []
            
        return self.user_keyword_history[user_id].most_common(limit)