DECLARE @s;
SET @s = STRING(4, 20, 1);

DECLARE @i, @ni;
SET @i = 3277;

WHILE @i < 10000
BEGIN

	SET @ni = 0;
	WHILE @ni < 3
	BEGIN
		INSERT INTO dictionary_orthographicvariant
		( entry_id, idem, is_reconstructed, is_approved )
		VALUES( @i, '@s', false, false );

		SET @ni = @ni + 1;
	END
	SET @i = @i + 1;
END  