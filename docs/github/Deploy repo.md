# Create a new github repository

Create a new repository

```
echo "# notes" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:{MyName}/{RepoName}.git
git push -u origin main
```

Push an existing repo with command lines

```
git remote add origin git@github.com:{MyName}/{RepoName}.git
git branch -M main
git push -u origin main
```


