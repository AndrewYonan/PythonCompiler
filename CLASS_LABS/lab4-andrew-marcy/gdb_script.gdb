# Set up to run with STDIN from file
set confirm off


break end39
run < tests/mytests/test1.in
info registers

quit
