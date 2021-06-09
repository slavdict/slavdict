# Удалять старые дампы базы,
# когда их в общей сложности накапливается более 90 шт. (~ 3 мес.)
FILENAME_PATTERN=/var/www/slavdict/.dumps/dictionary--*.xml.gz

for filename in $(ls -1t $FILENAME_PATTERN | sed -n '90,$p')
do
    rm $filename
done
