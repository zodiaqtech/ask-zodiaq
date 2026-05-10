"""
Domain Registry - Auto-discovers and manages domain evaluators and prompts

This module provides a registry that automatically discovers all domain evaluators
and prompt builders, making it easy to add new domains/subtopics by simply creating
the appropriate files in the domains directory.
"""
import importlib
import logging
from typing import Dict, List, Any, Optional, Type, Tuple
from pathlib import Path

from app.domains.base import (
    BaseEvaluator, BasePromptBuilder, BaseTwoPersonEvaluator,
    Question, QueryMeta, EvaluationResult
)

logger = logging.getLogger(__name__)


class DomainRegistry:
    """
    Central registry for all domain evaluators and prompt builders.
    
    This registry automatically discovers evaluators and prompts from the
    domains directory structure.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._evaluators: Dict[str, Dict[str, BaseEvaluator]] = {}
        self._prompt_builders: Dict[str, Dict[str, BasePromptBuilder]] = {}
        self._compatibility_evaluators: Dict[str, BaseTwoPersonEvaluator] = {}
        self._domain_rules: Dict[str, Dict[str, Any]] = {}
        self._subtopic_aliases: Dict[str, Dict[str, str]] = {}
        
        # ✅ Domain-level aliases: Map UI names to folder-based names
        self._domain_aliases: Dict[str, str] = {
            # Child domain (UI has apostrophe, folder is "child")
            "Child's Development and Education": "Child",
            "Child'S_Development_And_Education": "Child",
            "child's development and education": "Child",
            "Child’s Development and Education": "Child",
            "Child's Development And Education": "Child",
            "child": "Child",
            
            # General Guidance
            "General Guidance": "General_Guidance",
            "general guidance": "General_Guidance",
            "general_guidance": "General_Guidance",
            
            # Love Relationship
            "Love Relationship": "Love_Relationship",
            "love relationship": "Love_Relationship",
            "love_relationship": "Love_Relationship",
            
            # Marriage
            "Marriage": "Marriage",
            "marriage": "Marriage",
            
            # Career and Profession
            "Career and Profession": "Career",
            "Career and Profession": "Career",
            "career and profession": "Career",
            "career": "Career",
            
            # Business and Entrepreneurship
            "Business and Entrepreneurship": "Business",
            "Business And Entrepreneurship": "Business",
            "business and entrepreneurship": "Business",
            "business": "Business",
            
            # Finance and Property
            "Finance and Property": "Finance",
            "Finance And Property": "Finance",
            "finance and property": "Finance",
            "finance": "Finance",
            
            # Physical and Mental Health
            "Physical and Mental Health": "Health",
            "Physical And Mental Health": "Health",
            "physical and mental health": "Health",
            "health": "Health",
            
            # Parenting
            "Parenting": "Parenting",
            "parenting": "Parenting",
            
            # Foreign Settlement
            "Foreign Settlement": "Foreign",
            "foreign settlement": "Foreign",
            "foreign": "Foreign",
        }
        
        self._initialized = True
        self._discover_domains()
    
    def _discover_domains(self):
        """Auto-discover all domain evaluators and prompts"""
        # This file is at app/domains/registry.py, so parent is app/domains/
        # We want to iterate over subdirectories like app/domains/marriage/
        domains_path = Path(__file__).parent
        
        if not domains_path.exists():
            logger.warning(f"Domains path does not exist: {domains_path}")
            return
        
        for domain_dir in domains_path.iterdir():
            if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
                continue
            
            # Skip non-domain directories like __pycache__
            if domain_dir.name in ("__pycache__", "base"):
                continue
            
            domain_name = self._normalize_domain_name(domain_dir.name)
            self._evaluators[domain_name] = {}
            self._prompt_builders[domain_name] = {}
            
            # Discover subtopics
            for subtopic_dir in domain_dir.iterdir():
                if not subtopic_dir.is_dir() or subtopic_dir.name.startswith("_"):
                    continue
                
                # Skip non-subtopic directories
                if subtopic_dir.name == "__pycache__":
                    continue
                
                subtopic_name = self._normalize_subtopic_name(subtopic_dir.name)
                
                # Try to load evaluator
                evaluator = self._load_evaluator(domain_dir.name, subtopic_dir.name)
                if evaluator:
                    self._evaluators[domain_name][subtopic_name] = evaluator
                    logger.info(
                        f"📌 REGISTERED evaluator | "
                        f"domain='{domain_name}' | subtopic='{subtopic_name}' | "
                        f"class={evaluator.__class__.__name__}"
                    )


                
                # Try to load prompt builder
                prompt_builder = self._load_prompt_builder(domain_dir.name, subtopic_dir.name)
                if prompt_builder:
                    self._prompt_builders[domain_name][subtopic_name] = prompt_builder
                    logger.debug(f"Loaded prompt builder: {domain_name}/{subtopic_name}")
            
            # Try to load domain-level compatibility evaluator
            compat_evaluator = self._load_compatibility_evaluator(domain_dir.name)
            if compat_evaluator:
                self._compatibility_evaluators[domain_name] = compat_evaluator
            
            # Load domain rules if available
            rules = self._load_domain_rules(domain_dir.name)
            if rules:
                self._domain_rules[domain_name] = rules
            
            # Load subtopic aliases
            aliases = self._load_subtopic_aliases(domain_dir.name)
            if aliases:
                self._subtopic_aliases[domain_name] = aliases
                logger.info(f"  Loaded {len(aliases)} subtopic aliases for {domain_name}")
        
        logger.info(f"Discovered domains: {list(self._evaluators.keys())}")
        for domain, subtopics in self._evaluators.items():
            logger.info(f"  {domain}: {list(subtopics.keys())}")
            if domain in self._subtopic_aliases:
                logger.info(f"    Aliases: {list(self._subtopic_aliases[domain].keys())}")
    
    def _normalize_domain_name(self, name: str) -> str:
        """Convert directory name to domain name (e.g., 'marriage' -> 'Marriage')"""
        return name.replace("_", " ").title().replace(" ", "_")
    
    def _normalize_subtopic_name(self, name: str) -> str:
        """Convert directory name to subtopic name"""
        return name.replace("_", " ").title()
    
    def resolve_domain(self, domain: str) -> str:
        """
        Resolve domain alias to canonical name.
        
        Maps UI domain names (like "Child's Development and Education") 
        to folder-based names (like "Child").
        """
        # First check if there's a direct alias
        if domain in self._domain_aliases:
            resolved = self._domain_aliases[domain]
            logger.info(f"✅ Domain alias found: '{domain}' -> '{resolved}'")
            return resolved
        
        # Try case-insensitive match
        domain_lower = domain.lower()
        for alias, canonical in self._domain_aliases.items():
            if alias.lower() == domain_lower:
                logger.info(f"✅ Domain alias (case-insensitive): '{domain}' -> '{canonical}'")
                return canonical
        
        # Fall back to normalization
        normalized = self._normalize_domain_name(domain)
        logger.info(f"⚠️ No domain alias, normalized: '{domain}' -> '{normalized}'")
        return normalized
    
    def _load_evaluator(self, domain_dir: str, subtopic_dir: str) -> Optional[BaseEvaluator]:
        """Load evaluator from a subtopic directory"""
        try:
            module_path = f"app.domains.{domain_dir}.{subtopic_dir}.evaluator"
            module = importlib.import_module(module_path)
            
            # Find the evaluator class (check both BaseEvaluator and BaseTwoPersonEvaluator)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    (issubclass(attr, BaseEvaluator) or issubclass(attr, BaseTwoPersonEvaluator)) and 
                    attr not in (BaseEvaluator, BaseTwoPersonEvaluator)):
                    return attr()
            
            return None
        except Exception as e:
            logger.exception(
                f"❌ Evaluator import failed for {domain_dir}/{subtopic_dir}, skipping"
            )
            return None

    
    def _load_prompt_builder(self, domain_dir: str, subtopic_dir: str) -> Optional[BasePromptBuilder]:
        """Load prompt builder from a subtopic directory"""
        try:
            module_path = f"app.domains.{domain_dir}.{subtopic_dir}.prompts"
            module = importlib.import_module(module_path)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePromptBuilder) and 
                    attr is not BasePromptBuilder):
                    return attr()
            
            return None
        except ImportError as e:
            logger.debug(f"No prompt builder found for {domain_dir}/{subtopic_dir}: {e}")
            return None
    
    def _load_compatibility_evaluator(self, domain_dir: str) -> Optional[BaseTwoPersonEvaluator]:
        """Load compatibility evaluator for a domain"""
        try:
            module_path = f"app.domains.{domain_dir}.compatibility_evaluator"
            module = importlib.import_module(module_path)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseTwoPersonEvaluator) and 
                    attr is not BaseTwoPersonEvaluator):
                    return attr()
            
            return None
        except ImportError:
            return None
    
    def _load_domain_rules(self, domain_dir: str) -> Optional[Dict[str, Any]]:
        """Load domain rules"""
        try:
            module_path = f"app.domains.{domain_dir}.rules"
            module = importlib.import_module(module_path)
            return getattr(module, "DOMAIN_RULES", None)
        except ImportError:
            return None
    
    def _load_subtopic_aliases(self, domain_dir: str) -> Optional[Dict[str, str]]:
        """Load subtopic aliases"""
        try:
            module_path = f"app.domains.{domain_dir}.rules"
            module = importlib.import_module(module_path)
            return getattr(module, "SUBTOPIC_ALIASES", None)
        except ImportError:
            return None
    
    def get_evaluator(self, domain: str, subtopic: str) -> Optional[BaseEvaluator]:
        """Get evaluator for a domain/subtopic"""
        domain = self.resolve_domain(domain)
        subtopic = self.resolve_subtopic(domain, subtopic)
        
        domain_evaluators = self._evaluators.get(domain, {})
        logger.info(f"🔍 get_evaluator: Looking for '{domain}'/'{subtopic}'")
        logger.info(f"🔍 Available subtopics for '{domain}': {list(domain_evaluators.keys())}")
        
        evaluator = domain_evaluators.get(subtopic)
        if evaluator:
            logger.info(f"✅ Found evaluator: {type(evaluator).__name__}")
        else:
            logger.warning(f"❌ No evaluator found for '{domain}'/'{subtopic}'")
        
        return evaluator
    
    def get_prompt_builder(self, domain: str, subtopic: str) -> Optional[BasePromptBuilder]:
        """Get prompt builder for a domain/subtopic"""
        domain = self.resolve_domain(domain)
        subtopic = self.resolve_subtopic(domain, subtopic)
        
        domain_builders = self._prompt_builders.get(domain, {})
        return domain_builders.get(subtopic)
    
    def get_compatibility_evaluator(self, domain: str) -> Optional[BaseTwoPersonEvaluator]:
        """Get compatibility evaluator for a domain"""
        domain = self.resolve_domain(domain)
        return self._compatibility_evaluators.get(domain)
    
    def resolve_subtopic(self, domain: str, subtopic: str) -> str:
        """Resolve subtopic alias to canonical name"""
        domain = self.resolve_domain(domain)
        aliases = self._subtopic_aliases.get(domain, {})
        
        logger.info(f"🔍 resolve_subtopic: domain='{domain}', subtopic='{subtopic}'")
        logger.info(f"🔍 Available aliases for {domain}: {list(aliases.keys())[:10]}...")  # Show first 10
        
        # Try exact match first
        if subtopic in aliases:
            result = aliases[subtopic]
            logger.info(f"✅ Exact match found: '{subtopic}' -> '{result}'")
            return result
        
        # Try case-insensitive match
        subtopic_lower = subtopic.lower()
        for alias, canonical in aliases.items():
            if alias.lower() == subtopic_lower:
                logger.info(f"✅ Case-insensitive match: '{subtopic}' -> '{canonical}'")
                return canonical
        
        # Return normalized version if no alias
        normalized = self._normalize_subtopic_name(subtopic)
        logger.info(f"⚠️ No alias found, normalized: '{subtopic}' -> '{normalized}'")
        return normalized
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domains"""
        return list(self._evaluators.keys())
    
    def get_available_subtopics(self, domain: str) -> List[str]:
        """Get list of available subtopics for a domain"""
        domain = self.resolve_domain(domain)
        return list(self._evaluators.get(domain, {}).keys())
    
    def get_domain_rules(self, domain: str) -> Dict[str, Any]:
        """Get domain rules for KP scoring"""
        domain = self.resolve_domain(domain)
        return self._domain_rules.get(domain, {
            "positive_houses": {2, 7, 11},
            "supportive_houses": {5},
            "supportive_score": 2
        })
    
    def get_questions(self, domain: str, subtopic: str) -> List[Question]:
        """Get questions for a domain/subtopic"""
        evaluator = self.get_evaluator(domain, subtopic)
        if evaluator:
            return evaluator.get_questions()
        return []
    
    def extract_all_questions(self, domain: str, subtopics: List[str]) -> List[Dict[str, Any]]:
        """Extract all questions for given domain and subtopics"""
        all_questions = []
        
        for subtopic in subtopics:
            questions = self.get_questions(domain, subtopic)
            for q in questions:
                all_questions.append(q.to_dict())
        
        return all_questions


# Singleton instance
domain_registry = DomainRegistry()


def get_evaluator(domain: str, subtopic: str) -> Optional[BaseEvaluator]:
    """Convenience function to get evaluator"""
    return domain_registry.get_evaluator(domain, subtopic)


def get_prompt_builder(domain: str, subtopic: str) -> Optional[BasePromptBuilder]:
    """Convenience function to get prompt builder"""
    return domain_registry.get_prompt_builder(domain, subtopic)


def get_compatibility_evaluator(domain: str) -> Optional[BaseTwoPersonEvaluator]:
    """Convenience function to get compatibility evaluator"""
    return domain_registry.get_compatibility_evaluator(domain)


def get_domain_rules(domain: str) -> Dict[str, Any]:
    """Convenience function to get domain rules"""
    return domain_registry.get_domain_rules(domain)


def extract_questions(domain: str, subtopic: str) -> List[Dict[str, Any]]:
    """Extract questions for backward compatibility"""
    questions = domain_registry.get_questions(domain, subtopic)
    return [q.to_dict() for q in questions]