# Databricks notebook source
# MAGIC %sql
# MAGIC describe table stg.customers

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE stg.loans  
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE stg.transactions;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM stg.customers LIMIT 10;
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM stg.loans LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM stg.transactions LIMIT 10;