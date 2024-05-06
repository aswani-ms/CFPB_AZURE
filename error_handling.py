# Databricks notebook source
# MAGIC %sql
# MAGIC -- Creating an error table for invalid loans data
# MAGIC CREATE TABLE stg.loans_errors AS
# MAGIC SELECT *
# MAGIC FROM stg.loans l 
# MAGIC WHERE id_string IS NULL OR l.origination_date IS NULL OR principal_amount < 0; -- Add other error conditions here
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Deleting invalid data from the original loans table
# MAGIC DELETE FROM stg.loans
# MAGIC WHERE id_string IS NULL OR origination_date IS NULL OR principal_amount < 0; -- Add other error conditions here
# MAGIC

# COMMAND ----------

# Python cell in Databricks Notebook
error_df = spark.sql("SELECT * FROM stg.loans_errors")
error_df.write.format("csv").save("/mnt/data/error_files/loan_errors.csv")

