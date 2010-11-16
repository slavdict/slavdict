DECLARE @wordFormList;
SET @wordFormList = STRING(4,20,10);

DECLARE @deriv;
SET @deriv = INTEGER(1,50000, 1);

DECLARE @s2;
SET @s2 = STRING(4, 15, 7);

DECLARE @link_to_entry;
SET @link_to_entry = INTEGER(1,50000,9);

DECLARE @ni, @ss, @nni;
	
DECLARE @i, @im;
SET @i = 50000;
SET @im = 149000;


WHILE @i < 201000
BEGIN
INSERT INTO dictionary_entry(

  civil_equivalent,
  hidden,
  homonym_gloss,
  
  part_of_speech_id,
  uninflected,
  word_forms_list,
  gender_id,
  
  genitive,
  short_form,
  possessive,
  sg1,
  sg2,
  
  derivation_entry_id,
  link_to_entry_id,
  additional_info,
  status_id,
  percent_status,
  editor_id,
  antconc_query,
  grequiv_status) VALUES (
  
  'слово среднего размера', False,'',
  3,False,'@wordFormList',25,
  'а','принужде`нъ',True,'-и`','-ешися',
  @deriv,@deriv,'допо информация',2,78,7,'запрос АнтК','0');


	SET @ss =@s2;
	SET @ni = 0;
	WHILE @ni < 3
	BEGIN

		INSERT INTO dictionary_orthographicvariant
		( entry_id, idem, is_reconstructed, is_approved )
		VALUES( @i, 'вариа^нтъ', false, false );
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



		SET @nni = 0;
		WHILE @nni < 3
		BEGIN
			INSERT INTO dictionary_example(
				  meaning_id,
				  hidden,
				  example,
				  context,
				  address_text,
				  additional_info)
			VALUES (@im, false, '@ss', '@ss', 'Адрес @i', '@ss');

			SET @nni = @nni + 1;
		END


		SET @im = @im + 1;
		SET @ni = @ni + 1;
	END
  
SET @i = @i + 1;
END