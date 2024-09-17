-- models/bronze/bronze_s3_cadastros.sql
WITH raw_data AS (
  SELECT *
  FROM read_parquet('s3://crm-taipy-bucket/datasets/bronze/cadastros/cadastros*.parquet')
)

SELECT
  id,
  nome,
  data_nascimento,
  cpf,
  cep,
  cidade,
  estado,
  pais,
  genero,
  telefone,
  email,
  data_cadastro
FROM raw_data
