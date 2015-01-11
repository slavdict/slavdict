DECLARE @s;
SET @s = STRING(4, 15, 7);

DECLARE @link_to_entry;
SET @link_to_entry = INTEGER(1,49999,9);

DECLARE @i, @ni, @ss;
SET @i = 10000;
SET @ss =@s;
WHILE @i < 49999
BEGIN

	SET @ni = 0;
	WHILE @ni < 3
	BEGIN

		INSERT INTO dictionary_orthographicvariant
		( entry_id, idem, is_reconstructed, is_approved )
		VALUES( @i, 'орфогРа`фварЪ', false, false );
		INSERT INTO dictionary_meaning(
			entry_container_id,
			hidden ,
			link_to_entry_id,
			metaphorical,
			meaning,
			gloss,
			additional_info,
			substantivus)
		VALUES (@i, false, @link_to_entry, false, '@ss', '@ss', '@ss', false);

		SET @ni = @ni + 1;
	END
	SET @i = @i + 1;
END  