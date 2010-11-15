DECLARE @s, @ss;
SET @s = STRING(4, 12, 15);

DECLARE @link_to_entry;
SET @link_to_entry = INTEGER(1,3000,9);

DECLARE @i, @ni;
SET @i = 9640;

WHILE @i < 29810
BEGIN

	SET @ni = 0;
	WHILE @ni < 4
	BEGIN
		SET @ss = @s;
		INSERT INTO dictionary_example(
			  meaning_id,
			  hidden,
			  example,
			  context,
			  address_text,
			  additional_info)
		VALUES (@i, false, '@ss', '@ss', 'Адрес @i', '@ss');

		SET @ni = @ni + 1;
	END
	SET @i = @i + 1;
END  