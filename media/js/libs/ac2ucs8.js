function antconc_ucs8(antconc_text, isAffix){
    var ucs8_text = antconc_text;

    var A = [
        [/\{/g,    ' (('], // \{  ((
        [/\}/g,    '))'],  // \} ))
        [/@/g,      '\u00b0'], // @ °
        [/([\u047f\u0444\u0471])~/g,   '$1\\'], // (?<=[ѿфѱ])~ \\
        [/\u0482/g,  '\xa4'] // ҂ ¤
    ];

    var B = [ // Правила создания придыханий
        [/((^[\u0430\u0435\u0454\u0438\u0456\u043e\ua64b\u0479\u0443\u0461\u044b\u0463\u044e\ua657\u0467\u0475\u047b])|([^\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436'`\^~\u042a\u0427\u0414\u0413\u041d\u041e\u0420\u0421\u0412\u0425\u0417\u0416~#$%\u0410\u0411\u0427\u0426U\u0414\u042a\u042c\u042b\u0415\u0424F\u0413@I\u0418VM\u042f\u042d\u042eZ\u041aX\u041b\u0423\u041c\u041dQW\u041eT_\u041fP\u0420\u0428\u0429\u0421C&\u0422\u0412O\u0425\u0405\u0417\u0416\?dg\\\=b>c1345\u0430\u0431\u04476\u0446u\u0434\u044a\u044c\u044b\u0435\u0444f\u04332i\u0438vm\u044f\u044d\u044ez\u043ax\u043b\u0443\u043c\u043dqw\u043et8\u043fp\u0440\u0448\u0449\u04417\u0442\xb5\u0432\u0454o\u0445\u0455\u0437\u0436\+<\u20ac\u2022][\u0430\u0435\u0454\u0438\u0456\u043e\ua64b\u0479\u0443\u0461\u044b\u0463\u044e\ua657\u0467\u0475\u047b]))(?!['`\^])/g, '$13'], // ((?<=^[аеєиіоꙋѹуѡыѣюꙗѧѵѻ])|(?<=[^АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖабчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж'`\^~ЪЧДГНОРСВХЗЖ~#$%АБЧ\^ЦUДЪЬЫЕФFГ@IИVMЯЭЮZКXЛУМНQWОT_ПPРШЩСC&ТВOХЅЗЖ\?dg\\=b>c1345абч6цuдъьыефfг2iиvmяэюzкxлумнqwоt8пpршщс7тµвєoхѕзж\+<€•][аеєиіоꙋѹуѡыѣюꙗѧѵѻ]))(?!['`\^]) 3
        [/((^[\u0430\u0435\u0454\u0438\u0456\u043e\ua64b\u0479\u0443\u0461\u044b\u0463\u044e\ua657\u0467\u0475\u047b])|([^\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436'`\^~\u042a\u0427\u0414\u0413\u041d\u041e\u0420\u0421\u0412\u0425\u0417\u0416~#$%\u0410\u0411\u0427\u0426U\u0414\u042a\u042c\u042b\u0415\u0424F\u0413@I\u0418VM\u042f\u042d\u042eZ\u041aX\u041b\u0423\u041c\u041dQW\u041eT_\u041fP\u0420\u0428\u0429\u0421C&\u0422\u0412O\u0425\u0405\u0417\u0416\?dg\\\=b>c1345\u0430\u0431\u04476\u0446u\u0434\u044a\u044c\u044b\u0435\u0444f\u04332i\u0438vm\u044f\u044d\u044ez\u043ax\u043b\u0443\u043c\u043dqw\u043et8\u043fp\u0440\u0448\u0449\u04417\u0442\xb5\u0432\u0454o\u0445\u0455\u0437\u0436\+<\u20ac\u2022][\u0430\u0435\u0454\u0438\u0456\u043e\ua64b\u0479\u0443\u0461\u044b\u0463\u044e\ua657\u0467\u0475\u047b]))'/g, '$14'], // ((?<=^[аеєиіоꙋѹуѡыѣюꙗѧѵѻ])|(?<=[^АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖабчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж'`\^~ЪЧДГНОРСВХЗЖ~#$%АБЧ\^ЦUДЪЬЫЕФFГ@IИVMЯЭЮZКXЛУМНQWОT_ПPРШЩСC&ТВOХЅЗЖ\?dg\\=b>c1345абч6цuдъьыефfг2iиvmяэюzкxлумнqwоt8пpршщс7тµвєoхѕзж\+<€•][аеєиіоꙋѹуѡыѣюꙗѧѵѻ]))' 4
        [/((^[\u0430\u0435\u0454\u0438\u0456\u043e\ua64b\u0479\u0443\u0461\u044b\u0463\u044e\ua657\u0467\u0475\u047b])|([^\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436'`\^~\u042a\u0427\u0414\u0413\u041d\u041e\u0420\u0421\u0412\u0425\u0417\u0416~#$%\u0410\u0411\u0427\u0426U\u0414\u042a\u042c\u042b\u0415\u0424F\u0413@I\u0418VM\u042f\u042d\u042eZ\u041aX\u041b\u0423\u041c\u041dQW\u041eT_\u041fP\u0420\u0428\u0429\u0421C&\u0422\u0412O\u0425\u0405\u0417\u0416\?dg\\\=b>c1345\u0430\u0431\u04476\u0446u\u0434\u044a\u044c\u044b\u0435\u0444f\u04332i\u0438vm\u044f\u044d\u044ez\u043ax\u043b\u0443\u043c\u043dqw\u043et8\u043fp\u0440\u0448\u0449\u04417\u0442\xb5\u0432\u0454o\u0445\u0455\u0437\u0436\+<\u20ac\u2022][\u0430\u0435\u0454\u0438\u0456\u043e\ua64b\u0479\u0443\u0461\u044b\u0463\u044e\ua657\u0467\u0475\u047b]))`/g, '$15'], // ((?<=^[аеєиіоꙋѹуѡыѣюꙗѧѵѻ])|(?<=[^АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖабчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж'`\^~ЪЧДГНОРСВХЗЖ~#$%АБЧ\^ЦUДЪЬЫЕФFГ@IИVMЯЭЮZКXЛУМНQWОT_ПPРШЩСC&ТВOХЅЗЖ\?dg\\=b>c1345абч6цuдъьыефfг2iиvmяэюzкxлумнqwоt8пpршщс7тµвєoхѕзж\+<€•][аеєиіоꙋѹуѡыѣюꙗѧѵѻ]))` 5
        [/((^[\u0410\u0415\u0418\u0406\u041e\ua64a\u0478\u0460\u042b\u0462\u042e\ua656\u0466\u0474\u047a])|([^\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436'`\^~\u042a\u0427\u0414\u0413\u041d\u041e\u0420\u0421\u0412\u0425\u0417\u0416~#$%\u0410\u0411\u0427\u0426U\u0414\u042a\u042c\u042b\u0415\u0424F\u0413@I\u0418VM\u042f\u042d\u042eZ\u041aX\u041b\u0423\u041c\u041dQW\u041eT_\u041fP\u0420\u0428\u0429\u0421C&\u0422\u0412O\u0425\u0405\u0417\u0416\?dg\\\=b>c1345\u0430\u0431\u04476\u0446u\u0434\u044a\u044c\u044b\u0435\u0444f\u04332i\u0438vm\u044f\u044d\u044ez\u043ax\u043b\u0443\u043c\u043dqw\u043et8\u043fp\u0440\u0448\u0449\u04417\u0442\xb5\u0432\u0454o\u0445\u0455\u0437\u0436\+<\u20ac\u2022][\u0410\u0415\u0418\u0406\u041e\ua64a\u0478\u0460\u042b\u0462\u042e\ua656\u0466\u0474\u047a]))(?!['`\^])/g,   '$1#'], // ((?<=^[АЕИІОꙊѸѠЫѢЮꙖѦѴѺ])|(?<=[^АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖабчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж'`\^~ЪЧДГНОРСВХЗЖ~#$%АБЧ\^ЦUДЪЬЫЕФFГ@IИVMЯЭЮZКXЛУМНQWОT_ПPРШЩСC&ТВOХЅЗЖ\?dg\\=b>c1345абч6цuдъьыефfг2iиvmяэюzкxлумнqwоt8пpршщс7тµвєoхѕзж\+<€•][АЕИІОꙊѸѠЫѢЮꙖѦѴѺ]))(?!['`\^]) #
        [/((^[\u0410\u0415\u0418\u0406\u041e\ua64a\u0478\u0460\u042b\u0462\u042e\ua656\u0466\u0474\u047a])|([^\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436'`\^~\u042a\u0427\u0414\u0413\u041d\u041e\u0420\u0421\u0412\u0425\u0417\u0416~#$%\u0410\u0411\u0427\u0426U\u0414\u042a\u042c\u042b\u0415\u0424F\u0413@I\u0418VM\u042f\u042d\u042eZ\u041aX\u041b\u0423\u041c\u041dQW\u041eT_\u041fP\u0420\u0428\u0429\u0421C&\u0422\u0412O\u0425\u0405\u0417\u0416\?dg\\\=b>c1345\u0430\u0431\u04476\u0446u\u0434\u044a\u044c\u044b\u0435\u0444f\u04332i\u0438vm\u044f\u044d\u044ez\u043ax\u043b\u0443\u043c\u043dqw\u043et8\u043fp\u0440\u0448\u0449\u04417\u0442\xb5\u0432\u0454o\u0445\u0455\u0437\u0436\+<\u20ac\u2022][\u0410\u0415\u0418\u0406\u041e\ua64a\u0478\u0460\u042b\u0462\u042e\ua656\u0466\u0474\u047a]))'/g,    '$1$'], // ((?<=^[АЕИІОꙊѸѠЫѢЮꙖѦѴѺ])|(?<=[^АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖабчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж'`\^~ЪЧДГНОРСВХЗЖ~#$%АБЧ\^ЦUДЪЬЫЕФFГ@IИVMЯЭЮZКXЛУМНQWОT_ПPРШЩСC&ТВOХЅЗЖ\?dg\\=b>c1345абч6цuдъьыефfг2iиvmяэюzкxлумнqwоt8пpршщс7тµвєoхѕзж\+<€•][АЕИІОꙊѸѠЫѢЮꙖѦѴѺ]))' $
        [/((^[\u0410\u0415\u0418\u0406\u041e\ua64a\u0478\u0460\u042b\u0462\u042e\ua656\u0466\u0474\u047a])|([^\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436'`\^~\u042a\u0427\u0414\u0413\u041d\u041e\u0420\u0421\u0412\u0425\u0417\u0416~#$%\u0410\u0411\u0427\u0426U\u0414\u042a\u042c\u042b\u0415\u0424F\u0413@I\u0418VM\u042f\u042d\u042eZ\u041aX\u041b\u0423\u041c\u041dQW\u041eT_\u041fP\u0420\u0428\u0429\u0421C&\u0422\u0412O\u0425\u0405\u0417\u0416\?dg\\\=b>c1345\u0430\u0431\u04476\u0446u\u0434\u044a\u044c\u044b\u0435\u0444f\u04332i\u0438vm\u044f\u044d\u044ez\u043ax\u043b\u0443\u043c\u043dqw\u043et8\u043fp\u0440\u0448\u0449\u04417\u0442\xb5\u0432\u0454o\u0445\u0455\u0437\u0436\+<\u20ac\u2022][\u0410\u0415\u0418\u0406\u041e\ua64a\u0478\u0460\u042b\u0462\u042e\ua656\u0466\u0474\u047a]))`/g,    '$1%'] // ((?<=^[АЕИІОꙊѸѠЫѢЮꙖѦѴѺ])|(?<=[^АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖабчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж'`\^~ЪЧДГНОРСВХЗЖ~#$%АБЧ\^ЦUДЪЬЫЕФFГ@IИVMЯЭЮZКXЛУМНQWОT_ПPРШЩСC&ТВOХЅЗЖ\?dg\\=b>c1345абч6цuдъьыефfг2iиvmяэюzкxлумнqwоt8пpршщс7тµвєoхѕзж\+<€•][АЕИІОꙊѸѠЫѢЮꙖѦѴѺ]))` %
    ];

    var C = [
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])'/g, '$11'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])' 1
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])`/g, '$12'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])` 2
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\^/g, '$16'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])\^ 6
        [/3~/g, '~'], // 3~ ~
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])~/g,    '$17'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])~ 7
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u042a/g,  '$18'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Ъ 8
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0425/g,  '$1<'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Х <
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u041d/g,  '$1='], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Н =
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0420/g,  '$1>'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Р >
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0427/g,  '$1?'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Ч ?
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0412/g,  '$1+'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])В +
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u041e/g,  '$1b'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])О b
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0421/g,  '$1c'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])С c
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0414/g,  '$1d'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Д d
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0413/g,  '$1g'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Г g
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0417/g,  '$1\x88'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])З 
        [/([\u0430\u0431\u0447\u0446\u0479\u0434\u0131\u044a\u044c\u044b\u0435\u0444\u0473\u0433\u0456\u0438\u0475\ua657\u0463\u044e\u0467\u043a\u046f\u043b\ua64b\u043c\u043d\u047d\u0461\u043e\u047f\u043f\u0471\u0440\u0448\u0449\u0441\u0442\u0443\u0432\u0454\u047b\u0445\u0455\u0437\u0436])\u0416/g,  '$1\x95'], // (?<=[абчцѹдıъьыефѳгіиѵꙗѣюѧкѯлꙋмнѽѡоѿпѱршщстувєѻхѕзж])Ж 
        [/([\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416])`/g,   '$1@'], // (?<=[АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖ])` @
        [/([\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416])~/g,   '$1&'], // (?<=[АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖ])~ &
        [/([\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416])'/g,   '$1~'], // (?<=[АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖ])' ~
        [/([\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416])\^/g,  '$1^'], // (?<=[АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖ])\^ ^
        [/([\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416])\u042a/g,  '$1_'], // (?<=[АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖ])Ъ _
        [/([\u0410\u0411\u0427\u0426\u0478\u0414\u042a\u042c\u042b\u0415\u0424\u0472\u0413\u0406\u0418\u0474\ua656\u0462\u042e\u0466\u041a\u046e\u041b\ua64a\u041c\u041d\u047c\u0460\u041e\u047e\u041f\u0470\u0420\u0428\u0429\u0421\u0422\u0412\u0415\u047a\u0425\u0405\u0417\u0416])\u0421/g,  '$1C'], // (?<=[АБЧЦѸДЪЬЫЕФѲГІИѴꙖѢЮѦКѮЛꙊМНѼѠОѾПѰРШЩСТВЕѺХЅЗЖ])С C
        [/\u0472/g, 'F'], // Ѳ F
        [/\u0406/g, 'I'], // І I
        [/\u047a/g, 'O'], // Ѻ O
        [/\u0470/g, 'P'], // Ѱ P
        [/\u047c/g, 'Q'], // Ѽ Q
        [/\u047e/g, 'T'], // Ѿ T
        [/\u0478/g, 'U'], // Ѹ U
        [/\u0474/g, 'V'], // Ѵ V
        [/\u0460/g, 'W'], // Ѡ W
        [/\u046e/g, 'X'], // Ѯ X
        [/\u0466/g, 'Z'], // Ѧ Z
        [/\u0473/g, 'f'], // ѳ f
        [/\u0456/g, 'i'], // і i
        [/\u047b/g, 'o'], // ѻ o
        [/\u0471/g, 'p'], // ѱ p
        [/\u047d/g, 'q'], // ѽ q
        [/\u047f/g, 't'], // ѿ t
        [/\u0479/g, 'u'], // ѹ u
        [/\u0475/g, 'v'], // ѵ v
        [/\u0461/g, 'w'], // ѡ w
        [/\u046f/g, 'x'], // ѯ x
        [/\u0467/g, 'z'], // ѧ z
        [/\u0443/g, '\xb5'], // у µ
        [/\ua64a/g, '\u0423'], // Ꙋ У
        [/\u0462/g, '\u042d'], // Ѣ Э
        [/\ua656/g, '\u042f'], // Ꙗ Я
        [/\ua64b/g, '\u0443'], // ꙋ у
        [/\u0463/g, '\u044d'], // ѣ э
        [/\ua657/g, '\u044f'], // ꙗ я
        [/V(?=[#$%&@\^~1234567])/g,  '\u7770'], // V(?=[#$%&@\^~1234567]) 睰
        [/([\u0410\u0430\u0415\u0435\u0454])V/g,    '$1\u7770'], // (?<=[АаЕеє])V 睰
        [/([\u0410\u0430\u0415\u0435\u0454][#$%&@\^~1234567])V/g,   '$1\u7770'], // (?<=[АаЕеє][#$%&@\^~1234567])V 睰
        [/V/g,  'M'], // V M
        [/\u7770/g, 'V'], // 睰 V
        [/v(?=[#$%&@\^~1234567])/g,    '\u7771'], // v(?=[#$%&@\^~1234567]) 睱
        [/([\u0410\u0430\u0415\u0435\u0454])v/g,    '$1\u7771'], // (?<=[АаЕеє])v 睱
        [/([\u0410\u0430\u0415\u0435\u0454][#$%&@\^~1234567])v/g,   '$1\u7771'], // (?<=[АаЕеє][#$%&@\^~1234567])v 睱
        [/v/g,   'm'], // v m
        [/\u7771/g, 'v'], // 睱 v
        [/I(?![#$%&@\^~C1234567\+gd\u2022\u20ac=b>c<\?])/g, '\u0406'], // I(?![#$%&@\^~C1234567\+gd•€=b>c<\?]) І
        [/i(?![#$%&@\^~C1234567\+gd\u2022\u20ac=b>c<\?])/g, '\u0456'], // i(?![#$%&@\^~C1234567\+gd•€=b>c<\?]) і
        [/\u01317/g,    '\u2039'], // ı7 ‹
        [/\u0131/g,     'i'], // ı i
        [/z5/g,         '|'], // z5 |
        [/\u0410$/g,    '\u0403'], // А$ Ѓ
        [/\u04304/g,    '\u0453'], // а4 ѓ
        [/U$/g,         '\u040c'], // U$ Ќ
        [/U4/g,         '\u040c'], // U4 Ќ
        [/\u042f$/g,    '\u040b'], // Я$ Ћ
        [/O$/g,         '\u040f'], // O$ Џ
        [/u4/g,         '\u045c'], // u4 ќ
        [/\u044f4/g,    '\u045b'], // я4 ћ
        [/o4/g,         '\u045f'], // o4 џ
        [/I$/g,         '\u0408'], // I$ Ј
        [/i4/g,         '\u0458'], // i4 ј
        [/\u044f5/g,    '\xb1'], // я5 ±
        [/\u043e1/g,    '0'], // о1 0
        [/\u04367/g,    '9'], // ж7 9
        [/\u04302/g,    'A'], // а2 A
        [/\u044d6/g,    'B'], // э6 B
        [/\u0434c/g,    'D'], // дc D
        [/\u04352/g,    'E'], // е2 E
        [/\u04337/g,    'G'], // г7 G
        [/w1/g,         'H'], // w1 H
        [/i2/g,         'J'], // i2 J
        [/\u042f3/g,    'K'], // Я3 K
        [/\u043bd/g,    'L'], // лd L
        [/O#/g,         'N'], // O# N
        [/\u04407/g,    'R'], // р7 R
        [/z2/g,         'S'], // z2 S
        [/\u04432/g,    'Y'], // у2 Y
        [/\u04301/g,    'a'], // а1 a
        [/\u04351/g,    'e'], // е1 e
        [/\u044b1/g,    'h'], // ы1 h
        [/i1/g,         'j'], // i1 j
        [/\u044f3/g,    'k'], // я3 k
        [/\u043b7/g,    'l'], // л7 l
        [/o3/g,         'n'], // o3 n
        [/\u0440c/g,    'r'], // рc r
        [/z1/g,         's'], // z1 s
        [/\u04431/g,    'y'], // у1 y
        [/\u04436/g,    '{'], // у6 {
        [/\u04387/g,    '}'], // и7 }
        [/v1/g,         '\u0402'], // v1 Ђ
        [/x7/g,         '\u2026'], // x7 …
        [/\u04306/g,    '\u2020'], // а6 †
        [/i6/g,         '\u2021'], // i6 ‡
        [/z6/g,         '\u2030'], // z6 ‰
        [/Z#/g,         '\u0409'], // Z# Љ
        [/i7/g,         '\u2039'], // i7 ‹
        [/W#/g,         '\u040a'], // W# Њ
        [/vg/g,         '\u0452'], // vg ђ
        [/\u04427/g,    '\u2122'], // т7 ™
        [/z3/g,         '\u0459'], // z3 љ
        [/v6/g,         '\u203a'], // v6 ›
        [/w3/g,         '\u045a'], // w3 њ
        [/U#/g,         '\u040e'], // U# Ў
        [/U3/g,         '\u040e'], // U3 Ў
        [/u3/g,         '\u045e'], // u3 ў
        [/\u0410#/g,    '\u0490'], // А# Ґ
        [/\u04457/g,    '\xa6'], // х7 ¦
        [/\u04477/g,    '\xa7'], // ч7 §
        [/\u044d2/g,    '\u0401'], // э2 Ё
        [/\u04417/g,    '\xa9'], // с7 ©
        [/\u0440d/g,    '\xae'], // рd ®
        [/I#/g,         '\u0407'], // I# Ї
        [/\u04303/g,    '\u0491'], // а3 ґ
        [/\u044d1/g,    '\u0451'], // э1 ё
        [/\u04307/g,    '\u2116'], // а7 №
        [/i3/g,         '\u0457'] // i3 ї
    ];

    if (!isAffix) {
        // Полный набор правил конвертации
        var conversion = A.concat(B, C);
    } else {
        // Набор правил конвертации
        // без тех правил, что создают придыхания.
        // Предназначено для тех случаев, когда
        // необходимо отконвертировать, части слов,
        // например, окончания. Без данной опции
        // если часть слова начинается на гласную,
        // над ней неправильно возникает придыхание.
        var conversion = A.concat(C);
    }

    var conversion_len = conversion.length;

    var pattern, replacement;
    for (var i = 0; i < conversion_len; i++) {
        pattern     = conversion[i][0];
        replacement = conversion[i][1];
        ucs8_text   = ucs8_text.replace(pattern, replacement);
    }
    return ucs8_text;
}

function antconc_civilrus_word(word){
    var civilword = word;
    var conversion = [
        // Все буквы -- строчные.
        [/\u0454/g, '\u0435'], // широкое есть --> е
        [/\u0463/g, '\u0435'], // ять --> е
        [/\u0455/g, '\u0437'], // зело --> з
        [/\u0456/g, '\u0438'], // и десятиричное --> и
        [/\u0475/g, '\u0438'], // ижица --> и
        [/\uA64B/g, '\u0443'], // монограф ук --> у
        [/\u0479/g, '\u0443'], // диграф ук -->  у
        [/\u0461/g, '\u043E'], // омега --> о
        [/\u047B/g, '\u043E'], // широкое о --> о
        [/\u047D/g, '\u043E'], // оле --> о
        [/\u047F/g, '\u043E\u0442'], // от --> от
        [/\uA657/g, '\u044F'], // йотированное а --> я
        [/\u0467/g, '\u044F'], // юс малый --> я
        [/\u046F/g, '\u043A\u0441'], // кси --> кс
        [/\u0471/g, '\u043F\u0441'], // пси --> пс
        [/\u0473/g, '\u0444'], // фита --> ф
        [/\u0430\u0475/g, '\u0430\u0432'], // а + ижица --> ав
        [/\u0435\u0475/g, '\u0435\u0432'], // е + ижица --> ев
        [/\u0454\u0475/g, '\u0435\u0432'], // широкое есть + ижица --> ев
        [/'/g,   ''], // акут --x
        [/`/g,   ''], // гравис --x
        [/\^/g,  ''], // циркумфлекс --x
        [/~/g,  '*'], // титло --> *
        [/\u042A/g, '\u044A'], // паерок --> ъ
        [/\u0412/g, '*'], // веди-титло --> *
        [/\u0413/g, '*'], // глаголь-титло --> *
        [/\u0414/g, '*'], // добро-титло --> *
        [/\u0416/g, '*'], // живете-титло --> *
        [/\u0417/g, '*'], // земля-титло --> *
        [/\u041D/g, '*'], // наш-титло --> *
        [/\u041E/g, '*'], // он-титло --> *
        [/\u0420/g, '*'], // рцы-титло --> *
        [/\u0421/g, '*'], // слово-титло --> *
        [/\u0425/g, '*'], // хер-титло --> *
        [/\u0427/g, '*'], // червь-титло --> *
        [/\u044A$/g, ''], // конечный еръ --x
    ];
    var conversion_len = conversion.length;

    var pattern, replacement;
    for (var i = 0; i < conversion_len; i++) {
        pattern     = conversion[i][0];
        replacement = conversion[i][1];
        civilword   = civilword.replace(pattern, replacement);
    }
    return civilword;
}
