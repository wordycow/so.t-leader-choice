#!/usr/bin/env python3
"""
Image Optimization Script
Adds lazy loading and improves image accessibility
"""

import os
import re

print("🖼️  Optimizing images in HTML files...\n")

files = [
    "index.html",
    "the-unique-main.html",
    "the-unique-gate.html",
    "the-unique-promo.html",
    "market.html",
    "casino.html",
    "rank-hall.html",
]

optimized_count = 0
total_images = 0

for filename in files:
    if not os.path.exists(filename):
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    file_images_count = [0]  # Use list to avoid nonlocal issues
    
    # Pattern 1: <img src="..." without loading attribute
    # Add loading="lazy" and decoding="async"
    def add_lazy_loading(match):
        img_tag = match.group(0)
        
        # Skip if already has loading attribute
        if 'loading=' in img_tag:
            return img_tag
        
        # Skip if it's above the fold (background, logo, hero images)
        if any(keyword in img_tag.lower() for keyword in ['logo', 'hero', 'banner', 'og-']):
            return img_tag
        
        file_images_count[0] += 1
        
        # Add loading="lazy" and decoding="async"
        if '>' in img_tag:
            img_tag = img_tag.replace('>', ' loading="lazy" decoding="async">', 1)
        
        return img_tag
    
    # Apply lazy loading
    content = re.sub(r'<img[^>]+>', add_lazy_loading, content)
    
    # Pattern 2: Ensure all images have alt attributes
    def ensure_alt(match):
        img_tag = match.group(0)
        
        # Skip if already has alt
        if 'alt=' in img_tag:
            return img_tag
        
        # Extract src for context
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
        if src_match:
            src = src_match.group(1)
            # Create descriptive alt from filename
            alt_text = os.path.splitext(os.path.basename(src))[0].replace('-', ' ').replace('_', ' ').title()
            img_tag = img_tag.replace('>', f' alt="{alt_text}">', 1)
        
        return img_tag
    
    content = re.sub(r'<img[^>]+>', ensure_alt, content)
    
    if content != original_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {filename} - Optimized {file_images_count[0]} images")
        optimized_count += 1
        total_images += file_images_count[0]
    else:
        print(f"ℹ️  {filename} - No images to optimize")

print(f"\n✨ Image optimization complete!")
print(f"   Files processed: {optimized_count}")
print(f"   Images optimized: {total_images}")
print(f"\n📋 Optimizations applied:")
print(f"  • Lazy loading (loading='lazy')")
print(f"  • Async decoding (decoding='async')")
print(f"  • Alt text validation")
print(f"\n💡 Benefits:")
print(f"  • Faster initial page load")
print(f"  • Reduced bandwidth usage")
print(f"  • Better accessibility")
print(f"  • Improved SEO")
