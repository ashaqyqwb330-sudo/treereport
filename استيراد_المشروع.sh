
```bash
PROJECT_URL="https://github.com/ashaqyqwb330-sudo/treereport.git"   # ⚠️ استبدل الرابط بمستودعك
PROJECT_NAME=$(basename "$PROJECT_URL" .git)
cd /storage/4403-B0CA/
rm -rf "$PROJECT_NAME"
git clone "$PROJECT_URL"
git config --global --add safe.directory "/storage/4403-B0CA/$PROJECT_NAME"
cd "$PROJECT_NAME"
git pull origin main
echo "✅ تم الاستيراد إلى /storage/4403-B0CA/$PROJECT_NAME"
```
