#!/usr/bin/env python3
"""
Apply Medieval Magic Theme to HTML files
중세 마법 테마 적용 스크립트
"""

import os
import re

print("🏰 중세 마법 테마 적용 중...\n")

files = [
    "index.html",
    "the-unique-main.html",
    "the-unique-gate.html",
    "the-unique-promo.html",
    "market.html",
    "casino.html",
    "rank-hall.html",
]

# 새로운 CSS 링크
new_css = '''
  <!-- Medieval Magic Theme (골드 + 딥블루) -->
  <link rel="stylesheet" href="css/medieval-magic.css">
  <link rel="stylesheet" href="css/medieval-override.css">
'''

# 기존 개선 CSS 제거 패턴
old_css_patterns = [
    r'<link rel="stylesheet" href="css/design-system\.css">',
    r'<link rel="stylesheet" href="css/enhancements\.css">',
    r'<!-- Modern Design System.*?-->',
]

updated_count = 0

for filename in files:
    if not os.path.exists(filename):
        print(f"⚠️  {filename} - 파일 없음")
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 기존 CSS 제거
    for pattern in old_css_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 이미 적용되어 있는지 확인
    if 'medieval-magic.css' in content:
        print(f"✅ {filename} - 이미 적용됨")
        continue
    
    # </head> 전에 새 CSS 추가
    if '</head>' in content:
        content = content.replace('</head>', new_css + '\n</head>', 1)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {filename} - 중세 마법 테마 적용 완료")
        updated_count += 1
    else:
        print(f"⚠️  {filename} - </head> 태그 없음")

print(f"\n{'='*60}")
print(f"✨ 테마 적용 완료!")
print(f"   업데이트: {updated_count}개 파일")
print(f"{'='*60}")
print(f"\n🎨 적용된 테마:")
print(f"  • 중세 마법 세계 (딥블루 + 골드)")
print(f"  • 반투명 효과 완전 제거")
print(f"  • 불투명 배경")
print(f"  • 골드 빛나는 효과")
print(f"  • 일부 버튼만 현대적 스타일")
