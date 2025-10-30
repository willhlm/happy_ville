#!/bin/bash

# ==================================================
# setup-latest-only.sh
# 
# Purpose:
#   1. Add .DS_Store to .gitignore
#   2. Mark /art and /docs folders as "latest snapshot only"
#      (assume-unchanged) recursively
#run with $ bash scripts/setup-latest-only.sh
# ==================================================

echo "Setting up repository to treat /art and /docs as 'latest snapshot only'..."

# 1. Ensure .gitignore exists
if [ ! -f .gitignore ]; then
    touch .gitignore
    echo ".gitignore created."
fi

# 2. Add .DS_Store ignore rules (if not already present)
if ! grep -q ".DS_Store" .gitignore; then
    echo -e "\n# macOS system files\n.DS_Store\n**/.DS_Store" >> .gitignore
    echo ".DS_Store rules added to .gitignore."
else
    echo ".DS_Store already in .gitignore."
fi

# 3. Mark /art and /docs as assume-unchanged
for folder in art docs; do
    if [ -d "$folder" ]; then
        find "$folder" -type f ! -name ".DS_Store" -print0 | xargs -0 git update-index --assume-unchanged
        echo "Folder '$folder' marked as 'assume unchanged'."
    else
        echo "Folder '$folder' does not exist, skipping."
    fi
done

echo "Setup complete! Future changes in /art and /docs will not be tracked by Git."
