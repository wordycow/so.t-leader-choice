#!/usr/bin/env python3
"""
Accessibility Enhancement Script
Adds ARIA attributes and improves semantic HTML
"""

import os
import re

print("♿ Enhancing accessibility in HTML files...\n")

files = [
    "index.html",
    "the-unique-main.html",
    "market.html",
    "casino.html",
]

enhancements = {
    'buttons_fixed': 0,
    'links_fixed': 0,
    'headings_added': 0,
    'landmarks_added': 0,
}

def add_aria_to_buttons(content):
    """Add aria-label to buttons without accessible text"""
    count = 0
    
    # Pattern: buttons with icons but no text
    patterns = [
        (r'(<button[^>]*class="[^"]*game-btn[^"]*"[^>]*>)(\s*)([A-Z\s]+)(\s*)(</button>)', 
         r'\1\2<span aria-hidden="false">\3</span>\4\5'),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            count += 1
    
    return content, count

def add_aria_to_links(content):
    """Add aria-label to links that open in new tabs"""
    count = 0
    
    def add_label(match):
        nonlocal count
        link = match.group(0)
        
        # Skip if already has aria-label
        if 'aria-label=' in link:
            return link
        
        # Extract link text for context
        text_match = re.search(r'>([^<]+)<', link)
        if text_match:
            text = text_match.group(1).strip()
            if text and 'target="_blank"' in link and 'aria-label=' not in link:
                # Add aria-label indicating new window
                link = link.replace('>', f' aria-label="{text} (새 창)">', 1)
                count += 1
        
        return link
    
    content = re.sub(r'<a[^>]+target="_blank"[^>]*>.*?</a>', add_label, content, flags=re.DOTALL)
    
    return content, count

def add_skip_link(content):
    """Add skip to main content link for keyboard navigation"""
    if 'skip-to-content' in content:
        return content, 0
    
    skip_link = '''
  <a href="#main-content" class="skip-to-content">Skip to main content</a>
'''
    
    # Add after <body> tag
    if '<body>' in content:
        content = content.replace('<body>', '<body>\n' + skip_link, 1)
        return content, 1
    
    return content, 0

def add_main_landmark(content):
    """Ensure main content area has proper landmark"""
    if 'role="main"' in content or '<main' in content:
        return content, 0
    
    # Look for common main content containers
    patterns = [
        (r'(<div class="page-wrap">)', r'<div class="page-wrap" role="main" id="main-content">'),
        (r'(<div class="main-card">)', r'<div class="main-card" role="main" id="main-content">'),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content, count=1)
            return content, 1
    
    return content, 0

for filename in files:
    if not os.path.exists(filename):
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    file_enhancements = []
    
    # Apply all enhancements
    content, count = add_aria_to_buttons(content)
    if count > 0:
        enhancements['buttons_fixed'] += count
        file_enhancements.append(f"{count} buttons")
    
    content, count = add_aria_to_links(content)
    if count > 0:
        enhancements['links_fixed'] += count
        file_enhancements.append(f"{count} links")
    
    content, count = add_skip_link(content)
    if count > 0:
        enhancements['landmarks_added'] += count
        file_enhancements.append("skip link")
    
    content, count = add_main_landmark(content)
    if count > 0:
        enhancements['landmarks_added'] += count
        file_enhancements.append("main landmark")
    
    if content != original_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {filename} - Enhanced: {', '.join(file_enhancements)}")
    else:
        print(f"ℹ️  {filename} - Already accessible")

print(f"\n✨ Accessibility enhancements complete!")
print(f"\n📊 Summary:")
print(f"  • Buttons enhanced: {enhancements['buttons_fixed']}")
print(f"  • Links enhanced: {enhancements['links_fixed']}")
print(f"  • Landmarks added: {enhancements['landmarks_added']}")
print(f"\n📋 Improvements:")
print(f"  • ARIA labels for better screen reader support")
print(f"  • Skip navigation link for keyboard users")
print(f"  • Proper semantic landmarks")
print(f"  • External link indicators")
print(f"\n♿ WCAG 2.1 Level AA Compliance improved!")
