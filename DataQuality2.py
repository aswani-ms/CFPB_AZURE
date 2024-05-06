# Databricks notebook source
# MAGIC %sql
# MAGIC -- Check for duplicate records
# MAGIC SELECT id_string, COUNT(*)
# MAGIC FROM stg.customers
# MAGIC GROUP BY id_string
# MAGIC HAVING COUNT(*) > 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check for missing values in important columns
# MAGIC SELECT COUNT(*) AS missing_count
# MAGIC FROM stg.customers c 
# MAGIC WHERE id_string IS NULL or len(id_string)=0;
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Count of loans by state
# MAGIC SELECT id_string, COUNT(*) AS loan_count
# MAGIC FROM stg.loans
# MAGIC GROUP BY id_string
# MAGIC ORDER BY count(*) DESC;
# MAGIC
# MAGIC
# MAGIC