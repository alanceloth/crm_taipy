-- models/bronze/bronze_s3_pedidos.sql
WITH raw_data AS (
  SELECT * 
  FROM read_parquet('s3://crm-taipy-bucket/datasets/bronze/pedidos/pedidos*.parquet')
)
SELECT
  id_pedido,
  cpf,
  valor_pedido,
  valor_frete,
  valor_desconto,
  cupom,
  endereco_entrega_logradouro,
  endereco_entrega_numero,
  endereco_entrega_bairro,
  endereco_entrega_cidade,
  endereco_entrega_estado,
  endereco_entrega_pais,
  status_pedido,
  data_pedido  
FROM raw_data
