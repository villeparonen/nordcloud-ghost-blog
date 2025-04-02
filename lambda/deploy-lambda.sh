rm -rf build delete-all-posts.zip
mkdir -p build
cp delete-all-posts.py build/
cd build
zip -r ../delete-all-posts.zip . > /dev/null
cd ..
