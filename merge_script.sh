if [ "$TRAVIS_BRANCH" != "staging" ]; then
    exit 0;
fi

export GIT_COMMITTER_EMAIL=maylis.baschet@icloud.com
export GIT_COMMITTER_NAME=MayBaMay

git checkout master || exit
git merge "$TRAVIS_COMMIT" || exit
git push https://github.com/MayBaMay/PB_P10.git master # here need some authorization and url
