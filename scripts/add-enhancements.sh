#!/bin/bash

# Enhanced Web Design Injection Script
# Adds modern CSS enhancements to HTML files

echo "🎨 Adding modern design enhancements to HTML files..."

# CSS links to inject
CSS_LINKS='
  <!-- Modern Design System -->
  <link rel="stylesheet" href="css/design-system.css">
  <link rel="stylesheet" href="css/enhancements.css">
'

# Files to enhance
files=(
  "index.html"
  "the-unique-main.html"
  "the-unique-gate.html"
  "the-unique-promo.html"
  "market.html"
  "casino.html"
  "rank-hall.html"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    # Check if CSS is already added
    if grep -q "design-system.css" "$file"; then
      echo "✅ $file already enhanced"
    else
      # Add CSS links before </head>
      sed -i 's|</head>|'"$CSS_LINKS"'\n</head>|' "$file"
      echo "✅ Enhanced: $file"
    fi
  else
    echo "⚠️  File not found: $file"
  fi
done

echo ""
echo "✨ Design enhancements complete!"
echo ""
echo "📋 What was added:"
echo "  • Modern CSS Design System (variables, colors, spacing)"
echo "  • Fluid Typography (responsive font sizes)"
echo "  • Enhanced Micro-interactions (smooth animations)"
echo "  • Accessibility improvements (focus-visible)"
echo "  • Performance optimizations (GPU acceleration)"
echo "  • Reduced motion support"
echo ""
