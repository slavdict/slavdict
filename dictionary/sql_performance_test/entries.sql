DECLARE @wordFormList;
SET @wordFormList = STRING(4,20,10);

DECLARE @deriv;
SET @deriv = INTEGER(3000,10000, 1);

DECLARE @i;
SET @i = 9999;
WHILE @i < 50000
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
  'а','принужде`нъ',True,'-ю','-еши',
  @deriv,@deriv,'дополнительная информация',2,78,7,'запрос для АнтКонка','0');
SET @i = @i + 1;
END