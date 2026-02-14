#!/usr/bin/env python3
"""
Enhanced Web Design Injection Script
Adds modern CSS enhancements to HTML files
"""

import os
import re

# CSS links to inject
CSS_INJECTION = '''
  <!-- Modern Design System (2026) -->
  <link rel="stylesheet" href="css/design-system.css">
  <link rel="stylesheet" href="css/enhancements.css">
'''

# Files to enhance
files = [
    "index.html",
    "the-unique-main.html",
    "the-unique-gate.html",
    "the-unique-promo.html",
    "market.html",
    "casino.html",
    "rank-hall.html",
]

print("🎨 Adding modern design enhancements to HTML files...\n")

enhanced_count = 0
skipped_count = 0

for filename in files:
    if not os.path.exists(filename):
        print(f"⚠️  File not found: {filename}")
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already enhanced
    if 'design-system.css' in content:
        print(f"✅ {filename} - Already enhanced")
        skipped_count += 1
        continue
    
    # Find </head> tag and inject CSS before it
    if '</head>' in content:
        content = content.replace('</head>', CSS_INJECTION + '\n</head>', 1)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {filename} - Enhanced successfully")
        enhanced_count += 1
    else:
        print(f"⚠️  {filename} - No </head> tag found")

print(f"\n✨ Complete!")
print(f"   Enhanced: {enhanced_count} files")
print(f"   Skipped: {skipped_count} files")
print(f"\n📋 What was added:")
print(f"  • Modern CSS Design System (300+ variables)")
print(f"  • Fluid Typography (clamp-based responsive fonts)")
print(f"  • Enhanced Micro-interactions")
print(f"  • Accessibility improvements (WCAG 2.1)")
print(f"  • Performance optimizations")
print(f"  • Reduced motion support")
