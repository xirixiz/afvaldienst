rm -rf dist/*
python3 setup.py sdist
twine upload dist/*
#/volume1/homes/xirixiz/.local/bin/twine upload dist/*
