rm -rf dist/*
python3 setup.py sdist
if -f /volume1/homes/xirixiz/.local/bin/twine; then
  /volume1/homes/xirixiz/.local/bin/twine upload dist/*
else
  twine upload dist/*
fi
rm -rf dist/*
