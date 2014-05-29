#!/bin/bash
echo "Let's enumerate the pages of your pdf."
sleep 2

echo "Checking for dependencies"
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
                return
            else
                echo "pdftk successfully installed"
            fi
        else
            echo "Please install pdftk and try again"
            return
        fi
    else
        echo "Please install pdftk and try again"
        return
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
                return
            else
                echo "pdftk successfully installed"
            fi
        else
            echo "Please install pdflatex and try again"
            return
        fi
    else
        echo "Please install pdflatex and try again"
        return
    fi
fi

echo "Preparing System"
mkdir .temp

echo "Calculating Page Numbers"
#If you want to have some pages to not be numbered simply have this script move them to .temp at this point

PAGES=$(pdfinfo $1 | grep "Pages" | sed s/[^0-9]//g)

echo "Creating Page Number file for "$PAGES" pages"
(
printf '\\documentclass[12pt,a4]{article}\n'
printf '\\usepackage{multido}\n'
printf '\\usepackage[hmargin=.8cm,vmargin=.8cm,nohead,nofoot]{geometry}\n'
printf '\\begin{document}\n'
printf '\\multido{}{'$PAGES'}{\\vphantom{x}\\newpage}\n'
printf '\\end{document}'
) >.temp/numbers.tex

pdflatex -interaction=batchmode .temp/numbers.tex 1>/dev/null

echo "Bursting PDF's"
pdftk $1 burst output .temp/prenumb_burst_%03d.pdf
pdftk .temp/numbers.pdf burst output .temp/number_burst_%03d.pdf

echo "Adding Page Numbers"

for i in {001..$PAGES}; do \
pdftk .temp/prenumb_burst_$i.pdf background .temp/number_burst_$i.pdf output .temp/numbered-$i.pdf ; done

echo "Merging .pdf files"
cd .temp

pdftk .temp/numbered-{001..$PAGES}.pdf cat output .temp/book_bloat.pdf

echo "Optimizing PDF file"
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -dNOPAUSE \-dQUIET -dBATCH -sOutputFile=$2 .temp/book_bloat.pdf 2>/dev/null

echo "Cleaning Up"
rm -fr .temp
echo "The pages of PDF are enumerated."
