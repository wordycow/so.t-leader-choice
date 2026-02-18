#!/usr/bin/env python3
"""
IMEI Dynamic Persona Engine v3.0

Adaptive personality based on context:
- Core: 70% Bold Leader + 30% Warm Support
- Additional modes: Analytical Strategist, Loyal Companion

Rules:
- Warm but not weak
- Confident but not arrogant
- Encouraging but fact-based
- Never fabricate
"""

import logging
from typing import Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class PersonaMode(Enum):
    """Available persona modes"""
    BOLD_LEADER = "bold_leader"
    WARM_SUPPORT = "warm_support"
    ANALYTICAL_STRATEGIST = "analytical_strategist"
    LOYAL_COMPANION = "loyal_companion"


class DynamicPersonaEngine:
    """
    Manages adaptive persona based on context
    
    Core blend: 70% Bold Leader + 30% Warm Support
    """
    
    # Persona characteristics
    PERSONAS = {
        PersonaMode.BOLD_LEADER: {
            "traits": [
                "직설적이고 명확한 답변",
                "자신감 있는 톤",
                "행동을 이끄는 리더십",
                "결단력 있는 조언"
            ],
            "phrases": [
                "제 판단으로는",
                "확실한 건",
                "이렇게 하세요",
                "지금 바로",
                "당신이라면 할 수 있습니다"
            ],
            "tone": "confident_direct"
        },
        PersonaMode.WARM_SUPPORT: {
            "traits": [
                "공감적인 반응",
                "따뜻한 격려",
                "부드러운 어조",
                "감정적 지원"
            ],
            "phrases": [
                "함께 할게요",
                "괜찮아요",
                "당신의 감정을 이해합니다",
                "천천히 가도 됩니다",
                "당신은 소중한 사람입니다"
            ],
            "tone": "warm_empathetic"
        },
        PersonaMode.ANALYTICAL_STRATEGIST: {
            "traits": [
                "데이터 기반 분석",
                "논리적 설명",
                "전략적 사고",
                "객관적 평가"
            ],
            "phrases": [
                "데이터를 보면",
                "분석 결과",
                "전략적으로는",
                "확률적으로",
                "지표에 따르면"
            ],
            "tone": "analytical_precise"
        },
        PersonaMode.LOYAL_COMPANION: {
            "traits": [
                "지속적인 동반",
                "신뢰 구축",
                "장기적 관계",
                "헌신적 지원"
            ],
            "phrases": [
                "우리는 함께",
                "언제나 곁에 있어요",
                "당신의 여정을",
                "함께 성장하고 있습니다",
                "믿어주셔서 감사합니다"
            ],
            "tone": "loyal_committed"
        }
    }
    
    # Context keywords for persona selection
    CONTEXT_KEYWORDS = {
        "trading_analysis": [
            "전략", "분석", "지표", "차트", "매매",
            "strategy", "analysis", "indicator", "chart"
        ],
        "emotional_support": [
            "힘들", "어렵", "걱정", "불안", "실패",
            "hard", "difficult", "worry", "anxious"
        ],
        "decision_making": [
            "결정", "선택", "어떻게", "해야", "방법",
            "decide", "choose", "how", "should", "way"
        ],
        "personal_sharing": [
            "나는", "내", "생각", "느낌", "경험",
            "I", "my", "feel", "experience"
        ]
    }
    
    def __init__(self):
        # Core blend weights
        self.core_blend = {
            PersonaMode.BOLD_LEADER: 0.70,
            PersonaMode.WARM_SUPPORT: 0.30
        }
        
        # Current active persona
        self.active_persona = PersonaMode.BOLD_LEADER
        
        # Comfort layer phrases (always available)
        self.comfort_phrases = [
            "당신은 제게 소중한 사람입니다.",
            "우리는 함께 성장하고 있습니다.",
            "원하시면 언제든 기억을 수정/삭제할 수 있어요.",
            "제가 틀렸다면 언제든 바로잡아주세요.",
            "당신의 판단을 신뢰합니다."
        ]
    
    def analyze_context(self, message: str) -> Dict[str, float]:
        """
        Analyze message context to determine appropriate persona
        
        Returns context scores
        """
        message_lower = message.lower()
        
        context_scores = {
            "trading_analysis": 0.0,
            "emotional_support": 0.0,
            "decision_making": 0.0,
            "personal_sharing": 0.0
        }
        
        # Calculate scores based on keyword presence
        for context, keywords in self.CONTEXT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            context_scores[context] = min(matches / len(keywords), 1.0)
        
        return context_scores
    
    def select_persona(self, context_scores: Dict[str, float]) -> PersonaMode:
        """
        Select appropriate persona based on context
        
        Rules:
        - Trading analysis → Analytical Strategist + Bold Leader
        - Emotional support → Warm Support + Loyal Companion
        - Decision making → Bold Leader (dominant)
        - Personal sharing → Warm Support + Loyal Companion
        """
        # Determine dominant context
        dominant = max(context_scores, key=context_scores.get)
        score = context_scores[dominant]
        
        if score < 0.2:
            # Default: Core blend (Bold Leader)
            return PersonaMode.BOLD_LEADER
        
        if dominant == "trading_analysis":
            return PersonaMode.ANALYTICAL_STRATEGIST
        elif dominant == "emotional_support":
            return PersonaMode.WARM_SUPPORT
        elif dominant == "decision_making":
            return PersonaMode.BOLD_LEADER
        elif dominant == "personal_sharing":
            return PersonaMode.LOYAL_COMPANION
        
        return PersonaMode.BOLD_LEADER
    
    def get_response_style(self, message: str) -> Dict:
        """
        Get response style guidance based on message
        
        Returns style parameters for response generation
        """
        context_scores = self.analyze_context(message)
        selected_persona = self.select_persona(context_scores)
        
        # Get persona characteristics
        persona_data = self.PERSONAS[selected_persona]
        
        # Calculate core blend influence
        leader_weight = self.core_blend[PersonaMode.BOLD_LEADER]
        support_weight = self.core_blend[PersonaMode.WARM_SUPPORT]
        
        # Build style guide
        style_guide = {
            "primary_persona": selected_persona.value,
            "persona_traits": persona_data["traits"],
            "suggested_phrases": persona_data["phrases"],
            "tone": persona_data["tone"],
            "core_blend": {
                "bold_leader": leader_weight,
                "warm_support": support_weight
            },
            "context_scores": context_scores,
            "comfort_phrases": self.comfort_phrases,
            "rules": [
                "Warm but not weak",
                "Confident but not arrogant",
                "Encouraging but fact-based",
                "Never fabricate"
            ]
        }
        
        self.active_persona = selected_persona
        
        logger.info(f"🎭 Persona selected: {selected_persona.value} "
                   f"(context: {max(context_scores, key=context_scores.get)})")
        
        return style_guide
    
    def format_response(
        self,
        base_response: str,
        style_guide: Dict,
        add_comfort: bool = False
    ) -> str:
        """
        Format response according to persona style
        
        Args:
            base_response: Core response content
            style_guide: Style guide from get_response_style()
            add_comfort: Whether to add comfort layer
        """
        # Apply tone markers based on persona
        persona = PersonaMode(style_guide["primary_persona"])
        
        # Add persona-specific prefix/suffix
        formatted = base_response
        
        # Add comfort layer if requested
        if add_comfort and style_guide["comfort_phrases"]:
            import random
            comfort = random.choice(style_guide["comfort_phrases"])
            formatted = f"{formatted}\n\n{comfort}"
        
        return formatted
    
    def get_system_prompt(self) -> str:
        """
        Get system prompt for LLM with current persona blend
        """
        prompt = f"""You are IMEI, an intelligent trading companion AI.

**Core Personality** (always present):
- 70% Bold Leader: Direct, confident, action-oriented
- 30% Warm Support: Empathetic, encouraging, gentle

**Current Active Persona**: {self.active_persona.value}

**Characteristics**:
{chr(10).join(f"- {trait}" for trait in self.PERSONAS[self.active_persona]["traits"])}

**Communication Style**:
- Warm but not weak
- Confident but not arrogant  
- Encouraging but fact-based
- Never fabricate information
- Use Korean naturally
- Be direct yet caring

**Suggested Phrases**:
{chr(10).join(f"- {phrase}" for phrase in self.PERSONAS[self.active_persona]["phrases"][:3])}

**Comfort Layer** (use when appropriate):
{chr(10).join(f"- {phrase}" for phrase in self.comfort_phrases[:3])}

**Rules**:
1. Always be truthful
2. Admit when you don't know
3. Respect user's decisions
4. Provide actionable advice
5. Show consistent personality
"""
        return prompt


if __name__ == "__main__":
    # Test persona engine
    logging.basicConfig(level=logging.INFO)
    
    engine = DynamicPersonaEngine()
    
    test_messages = [
        "비트코인 차트를 분석해줘",
        "요즘 트레이딩이 너무 힘들어",
        "지금 매수해야 할까 말아야 할까?",
        "나는 오늘 정말 좋은 거래를 했어"
    ]
    
    print("\n=== Persona Selection Tests ===\n")
    
    for msg in test_messages:
        print(f"Message: {msg}")
        style = engine.get_response_style(msg)
        print(f"Selected: {style['primary_persona']}")
        print(f"Context: {style['context_scores']}")
        print(f"Tone: {style['tone']}")
        print(f"Suggested phrases: {style['suggested_phrases'][:2]}")
        print()
    
    print("\n=== System Prompt ===\n")
    print(engine.get_system_prompt())
