#!/bin/bash
./deletePlot.sh $1
# # Base command
# base_cmd="python customPlot.py"

# # Directory pattern
# dir_pattern="$1/*/*/"

# # Find all matching directories and execute the Python script
# for dir in $dir_pattern; do
#     if [ -d "$dir" ]; then
#         echo "Executing in directory: $dir"
#         $base_cmd "$dir"
#         echo "------------------------"
#     fi
# done

base_cmd2="python customGraphs.py"

dir_pat="$1/*"

for dir in $dir_pat; do
    if [ -d "$dir" ]; then
        echo "executing dir $dir" 
        $base_cmd2 "$dir/*"
        echo "------------------------"
    fi
done

python customHistograms.py $1

python generateLatex.py $1