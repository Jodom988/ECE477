#!/bin/bash
echo "============================="
echo "|| Buidling C++ Program... ||"
echo "============================="

cd build; make; cd ../
mv build/ProcessFrame ./

echo "==========="
echo "|| Done! ||"
echo "==========="

python3 Main.py -p 9595