echo "=============================================================="
echo "Status"
echo "=============================================================="
git status

echo "=============================================================="
echo "Add *"
echo "=============================================================="
git add *

echo "=============================================================="
echo "Status"
echo "=============================================================="
git status

echo "=============================================================="
echo "Commit"
echo "=============================================================="
git commit -m "update"

echo "=============================================================="
echo "Pull"
echo "=============================================================="
git pull --rebase

echo "=============================================================="
echo "Update Recent" # after pull to avoid conflicts in index.md
echo "=============================================================="
python update_recent.py
git add *
git commit -m "update recent"

echo "=============================================================="
echo "Push"
echo "=============================================================="
git push -u origin main

echo "=============================================================="
echo "Done!"
echo "=============================================================="