echo "git auto push start ..."
echo "git pull ..."
git pull
echo "git add . ..."
git add .
echo "git commit message : $1 ..."
git commit -m $1
echo "git push ..."
git push
echo "git auto push end ..."
