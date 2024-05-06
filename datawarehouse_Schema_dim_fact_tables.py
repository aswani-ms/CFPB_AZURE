# Databricks notebook source
# MAGIC %md
# MAGIC       Fact Table
# MAGIC         loans
# MAGIC        /  |  \
# MAGIC       /   |   \
# MAGIC customers loan_types payment_status
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Creating a new schema called 'dw'
# MAGIC CREATE SCHEMA IF NOT EXISTS dw;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC drop TABLE dw.dim_customers 

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC -- Creating a dimension table for customers in the 'dw' schema
# MAGIC CREATE TABLE dw.dim_customers (
# MAGIC     customer_id STRING,
# MAGIC     first_name STRING,
# MAGIC     last_name STRING,
# MAGIC     gender STRING,
# MAGIC     email STRING,
# MAGIC     phone_number STRING,
# MAGIC     address STRING,
# MAGIC     income DECIMAL(28, 12),
# MAGIC     state STRING,
# MAGIC     birthday DATE,
# MAGIC     hair_color STRING,
# MAGIC     credit_score BIGINT
# MAGIC );
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE dw.dim_loans (
# MAGIC     loan_id STRING,
# MAGIC     customer_id STRING,
# MAGIC     lender_state STRING,
# MAGIC     origination_date DATE,
# MAGIC     due_date DATE,
# MAGIC     term_weeks BIGINT,
# MAGIC     principal_amount DECIMAL(28, 12),
# MAGIC     total_due_amount DECIMAL(28, 12),
# MAGIC     paid_amount DECIMAL(28, 12),
# MAGIC     fee_amount DECIMAL(28, 12),
# MAGIC     collateral_assessment DECIMAL(28, 12),
# MAGIC     collateral_sold DECIMAL(28, 12),
# MAGIC     defaulted STRING
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Creating dimension table for loan types
# MAGIC CREATE TABLE dw.dim_loan_types (
# MAGIC     loan_type_id INT PRIMARY KEY,
# MAGIC     description STRING
# MAGIC );
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Creating dimension table for payment status
# MAGIC CREATE TABLE dw.dim_payment_status (
# MAGIC     status_id INT PRIMARY KEY,
# MAGIC     status_description STRING
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC -- Creating the fact table for loans
# MAGIC CREATE TABLE dw.fact_loans (
# MAGIC     loan_id STRING PRIMARY KEY,
# MAGIC     customer_id STRING,
# MAGIC     loan_type_id INT,
# MAGIC     status_id INT,
# MAGIC     loan_amount DECIMAL(10,2),
# MAGIC     start_date DATE,
# MAGIC     end_date DATE,
# MAGIC     FOREIGN KEY (customer_id) REFERENCES dw.dim_customers(customer_id),
# MAGIC     FOREIGN KEY (loan_type_id) REFERENCES dw.dim_loan_types(loan_type_id),
# MAGIC     FOREIGN KEY (status_id) REFERENCES dw.dim_payment_status(status_id)
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE dw.fact_transactions (
# MAGIC     transaction_id STRING,
# MAGIC     loan_id STRING,
# MAGIC     customer_id STRING,
# MAGIC     transaction_date DATE,
# MAGIC     amount DECIMAL(28, 12),
# MAGIC     direction STRING,
# MAGIC     is_late STRING,
# MAGIC     fee DECIMAL(10, 2)
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from stg.loans

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO dw.fact_transactions
# MAGIC SELECT
# MAGIC     t.id_string AS transaction_id,
# MAGIC     t.loan_id_string AS loan_id,
# MAGIC     l.customer_id_string AS customer_id,
# MAGIC     t.date AS transaction_date,
# MAGIC     t.amount,
# MAGIC     t.direction,
# MAGIC     t.is_late,
# MAGIC     t.fee
# MAGIC FROM 
# MAGIC     stg.transactions t
# MAGIC JOIN 
# MAGIC     stg.loans l ON t.loan_id_string = l.id_string;
# MAGIC
# MAGIC