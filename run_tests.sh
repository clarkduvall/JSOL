#!/bin/sh

echo 'Running JSOL tests:'
echo
jsol.py test_data/jsol/*_test.jsol

echo
echo 'Running PSOL tests:'
echo
parser.py test_data/psol/*_test.psol
