#!/bin/bash

# Checking for dependencies
OS=$(lsb_release -si)
if ! which pdftk > /dev/null; then
    echo "Dependencies not met: pdftk not found"
    if [ "$OS" = "Ubuntu" ] || [ "$OS" = "Debian" ]; then
        echo "You appear to be running ubuntu or debian do you want me to attempt to install automatically? (y/n)"
        read ANSWER
        if [ "$ANSWER" = "y" ] || [ "$ANSWER" = "Y" ] || [ $ANSWER = "yes" ]; then
            sudo apt-get install pdftk
            if ! which pdftk > /dev/null; then
                echo "Problem with automatic installation, please install manually and try again"
                exit 1
            else
                echo "pdftk successfully installed"
            fi
        else
            echo "Please install pdftk and try again"
            exit 1
        fi
    else
        echo "Please install pdftk and try again"
        exit 1
    fi
fi

if ! which pdflatex > /dev/null; then
    echo "Dependencies not met: pdflatex not found"
    if [ "$OS" = "Ubuntu" ] || [ "$OS" = "Debian" ]; then
        echo "You appear to be running ubuntu or debian do you want me to attempt to install automatically? (y/n)"
        read ANSWER
        if [ "$ANSWER" = "y" ] || [ "$ANSWER" = "Y" ] || [ $ANSWER = "yes" ]; then
            sudo apt-get install texlive
            if ! which pdflatex > /dev/null; then
                echo "Problem with automatic installation, please install manually and try again"
                exit 1
            else
                echo "pdftk successfully installed"
            fi
        else
            echo "Please install pdflatex and try again"
            exit 1
        fi
    else
        echo "Please install pdflatex and try again"
        exit 1
    fi
fi

INPUT_FILE=$(readlink -f "$1")
OUTPUT_FILE=$(readlink -f "$2")
START_PAGE=${3:-1}

test -z $INPUT_FILE && exit 1
if [ -z $OUTPUT_FILE ]
then
    OUTPUT_FILE=${INPUT_FILE%.pdf}-numbered.pdf
fi
echo 'Input file:'  $INPUT_FILE
echo 'Output file:' $OUTPUT_FILE

# Preparing System
TEMPDIR=.temp-ZsD2hqRRu
mkdir -p $TEMPDIR
cd $TEMPDIR

# Calculating Page Numbers
PAGES=$(pdfinfo "$INPUT_FILE" | grep "Pages" | sed s/[^0-9]//g)

# Creating Page Number file for "$PAGES" pages
cat >numbers.tex <<EOF
\documentclass[12pt,a4]{article}
\usepackage{multido}
\usepackage[hmargin=.8cm,vmargin=0cm,nohead,nofoot]{geometry}
\pagestyle{myheadings}
\setcounter{page}{$START_PAGE}
\begin{document}
\multido{}{$PAGES}{\vphantom{x}\newpage}
\end{document}
EOF

echo
echo Bursting original PDF
pdftk "$INPUT_FILE" burst output orig_burst_%0${#PAGES}d.pdf 2>/dev/null

echo Generating PDF with page numbers on blank pages
pdflatex -interaction=batchmode numbers.tex >/dev/null

echo Bursting blank PDF
pdftk numbers.pdf burst output number_burst_%0${#PAGES}d.pdf

# Adding Page Numbers
echo Merging pages with text and blank pages with numbers
for i in $(seq -w $PAGES)
do
    pdftk orig_burst_$i.pdf \
        background number_burst_$i.pdf \
        output numbered_$i.pdf
done

echo Concatenating pages into single PDF
pdftk $(for i in $(seq -w $PAGES); do echo numbered_$i.pdf;
        done) cat output book_bloat.pdf

echo Optimizing PDF file
gs 2>/dev/null \
    -sDEVICE=pdfwrite \
    -dCompatibilityLevel=1.4 \
    -dPDFSETTINGS=/printer \
    -dUseCIEColor \
    -dNOPAUSE \
    -dQUIET \
    -dBATCH \
    -sOutputFile="$OUTPUT_FILE" book_bloat.pdf
#mv book_bloat.pdf "$OUTPUT_FILE"

cd ..
# Cleaning Up
rm -fr $TEMPDIR

echo Done.
# The pages of PDF are enumerated.
exit 0
