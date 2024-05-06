# CFPB_AZURE

# Data Engineering Project

## 1. Understanding the Dataset

### Structure and Foreign Keys

The dataset includes three entities: `customers`, `loans`, and `transactions`, along with the relationships between them. `loans` have information about the customers, and `transactions` have information about loans and customers.

- **Customers**: Details about the customers taking out loans, including fields like `customer_id`, `name`, `address`, `phone_number`, and `email`.
- **Loans**: Information about the loans, such as `loan_id`, `customer_id`, `loan_amount`, `interest_rate`, `start_date`, `due_date`, and `status`.
- **Transactions**: Records of transactions related to the loans, including `transaction_id`, `loan_id`, `transaction_date`, `transaction_type`, and `amount`.

**Foreign Keys**:
- `customer_id` in the `Loans` table links each loan to a customer in the `Customers` table.
- `loan_id` in the `Transactions` table links each transaction to a specific loan in the `Loans` table, allowing for tracking of all financial activities related to each loan. It also gets information about the customer through the `loans` table.

### Uniqueness Issues

No uniqueness issues were identified, but null values were observed in primary keys for `loans` and `transactions`. These need to be filtered out during the data cleansing process. In the new schema, `id_strings` will be defined in each table as primary keys to prevent duplicate values.

The id_string fields are currently defined as strings. Through verification using SQL queries, it has been observed that these values are in fact numeric and do not contain any special characters. Here are the queries used for verification:
```sql
SELECT id_string
FROM stg.customers
WHERE id_string RLIKE '^[0-9]+$'  -- Checks for purely numeric
LIMIT 10;

SELECT id_string
FROM stg.customers
WHERE id_string RLIKE '^[A-Za-z0-9]+$' AND id_string RLIKE '[A-Za-z]'  -- Checks for alphanumeric
LIMIT 10;
```
Based on these findings, the id_string fields could potentially be converted to numeric types to improve performance. However, for the purposes of this exercise, they have been left as strings. This decision allows us to focus on other aspects of the dataset and avoids the complexities involved in altering the database schema at this stage


### Optimizing for Analysis

- Create views for `transactions` and `loans` to view relevant information quickly.
- Create dimension and fact tables in Databricks for efficient reporting.
- Create reusable notebooks to flush out invalid data into an error table.

## 2. Data Quality Checks

Examples of code used for data quality checks will be provided from Databricks notebooks.

### Data Quality Issues

- Transactions without `loan_id` or `transaction_id` are considered invalid.
- Without a `loan_id`, a transaction cannot be tied to either a loan or a customer.

### Assumptions

- Common sense assumptions that transactions without `loan_id` or `transaction_id` are not valid.
- Without a `loan_id`, you cannot tie a transaction to either a loan or customer.

## 3. Data Modeling

Assuming that this data would be used primarily for reporting purposes, a star schema with dimensions and facts would be more relevant. Proposed tables include `DimCustomer`, `DimLoan`, and `FactTransaction`. This will help with performance, and the ETL process will be used to transform the data from the normalized database to the star schema.

* In the repository, I have attached some screenshots and pdfs of notebooks that i wrote in  Sql

## 4. File Processing

### Ensuring Expected File Arrival Times and Formats

**Using Event-Based Triggers in Azure Data Factory (ADF)**:
- Set up: Created a Storage Service account, uploaded CSV files to Azure Blob Storage.
- Configured ADF to use event-based triggers that activates when new files are uploaded to Azure Blob Storage.
- Utilized the Blob Storage event grid to monitor for `BlobCreated`  events, indicating new file uploads.
- Set up alerts in Azure Monitor to notify administrators if expected uploads do not occur as scheduled.

**Ensuring Files Arrive in the Expected Formats**:
- Initial Checks in ADF: Implement preliminary schema and format validations during the data ingestion phase. Null values and blanks for primary key fields are filtered out in this phase.
- Complex Validations in Azure Databricks: Use notebooks to execute more detailed validations, such as checking for correct data types, mandatory fields, and referential data integrity.
- Error Handling and Notifications: Configure error logging and automated notifications for files that fail validations.
- Documentation and Continuous Improvement: Maintain detailed documentation of expected file formats and establish a feedback loop with data providers.

### Integrating New Data

**Scenario 1: New files contain only new records or updated records since the last delivery**

```sql
-- Insert new transaction data into the transactions table
INSERT INTO stg.transactions
SELECT *
FROM staging_transactions;
```
staging_transaction table is created for every new file --Delete old data and insert records from new file.
Since we are sure of getting only new records, there is no need for overhead of merge, or checking for pre-existing records. Hence a straight insert is sufficient.



**Scenario 2: New files contain new records, updated records, and unchanged records**

```sql
-- SQL MERGE command to update existing records and insert new ones into stg.transactions from staging_transactions
MERGE INTO stg.transactions AS old
USING staging_transactions AS new
ON old.transaction_id = new.transaction_id

-- When records match, and there is a difference, update the existing record
WHEN MATCHED AND (old.amount <> new.amount OR old.date <> new.date OR old.status <> new.status) THEN UPDATE SET
    old.customer_id = new.customer_id,
    old.amount = new.amount,
    old.date = new.date,
    old.status = new.status

-- When no records match (i.e., these are new records), insert the new records into the main table
WHEN NOT MATCHED THEN INSERT (
    transaction_id,
    customer_id,
    amount,
    date,
    status
) VALUES (
    new.transaction_id,
    new.customer_id,
    new.amount,
    new.date,
    new.status
);
```
Merge statement handles updates for existing records, and inserts the new records.
### Managing Processed Files

- Archive: Move processed files to an archival storage location, such as Azure Blob Storage with a cool or archive tier, to maintain a historical record while optimizing storage costs.
- Logging and Audit: Maintain a log of all processed files, including timestamps and outcomes, for auditing, troubleshooting, and compliance tracking.

### Maintaining File Lineage

Create a `FileMetadata` table to store information about the files, including their origin, load time, size, record count, and checksum.

```sql
CREATE TABLE FileMetadata (
    FileID INT PRIMARY KEY AUTO_INCREMENT,
    FileName VARCHAR(255),
    FileOrigin VARCHAR(255),
    LoadTime DATETIME,
    FileSize BIGINT,
    RecordCount INT,
    FileChecksum VARCHAR(255)
);
```

Record an entry into this metadata table every time a file is processed.

## 5. Data Quality Reporting and Error Handling

### Tracking Quality Check Results

- **Dedicated SQL Tables**: Establish dedicated tables in a SQL database (e.g., Azure SQL Database or Azure Synapse Analytics) to log the outcomes of all data quality checks. Each entry in this table would record the date and time of the check, details of the check performed (such as the type of check and fields involved), the outcome (pass or fail), and detailed error messages or descriptions of anomalies detected.

```sql
CREATE TABLE DataQualityLogs (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    CheckDate DATETIME,
    CheckType VARCHAR(255),
    CheckOutcome VARCHAR(50),
    Details VARCHAR(MAX)
);
```

- **Notebooks**: Notebooks can also be used for automated and repeatable data quality checks, with the option of integrating visualizations and creating specialized dashboards.

### Reporting on Quality Checks

Generate regular reports and dashboards using tools like Power BI to provide insights into the health of the data pipeline and data quality trends over time. Display key metrics, including pass/fail rates, types of errors found, and trends in data quality. Can leverage the data quality tables and meta data tables created in previous steps.

### Handling Failed Quality Checks

1. **Isolation and Correction**: Move erroneous data to a separate quarantine area, where it can be analyzed and corrected. This prevents the propagation of poor-quality data through subsequent stages of the data pipeline. Example: I created a table called `stg.loans_errors` to push erroneous records, which could be scheduled for alerting and potential reprocessing.
2. **Notification and Manual Review**: Set up automated alerts to notify data engineers or relevant stakeholders when data fails quality checks. Provide tools and processes for manual review and correction of the data.
3. **Reprocessing**: Once the data is corrected, it should be reprocessed through the pipeline to ensure it meets all quality standards before being used in downstream processes.



## 6. Data Pipeline Monitoring

### Monitoring Pipeline Activity

- **Azure Monitor**: Set up alerts for metrics such as runtime duration, success rate, and failure rates. Configure alerts to notify  via email or pager duties or other sms services if certain thresholds are breached.
- **ADF Monitoring**: Utilize the monitoring dashboard in ADF to get real-time insights into pipeline runs, activity failures, and performance bottlenecks.

### Ensuring Timely and Error-free Execution

- **Scheduled Triggers**: Set up scheduled triggers in ADF to start the pipeline at specific times.
- **Dependency Conditions**: Configure pipeline activities with precedence constraints to ensure downstream activities only start if upstream activities succeed.

### Tracking Pipeline Run Information

- **Logging**: Use Azure SQL Database to log details of each pipeline run, including start time,

# Effective Data Pipeline Monitoring and Management

Effective monitoring and management of data pipeline activities are crucial for ensuring reliability, performance, and timely data availability. Here's how you can set up and manage these aspects of your ETL/ELT processes:

### **1. Monitoring Pipeline Activity**

**Process**: Implement comprehensive monitoring using Azure Monitor along with Azure Data Factory's (ADF) built-in monitoring features. These tools allow you to track run history, performance, and the health of your pipelines.

**Example**:

- **Azure Monitor**: Set up alerts for metrics such as runtime duration, success rate, and failure rates. You can configure alerts to notify you via email or SMS if certain thresholds are breached.
- **ADF Monitoring**: Utilize the monitoring dashboard in ADF to get real-time insights into pipeline runs, activity failures, and performance bottlenecks.

### **2. Ensuring Pipelines Run According to Schedule**

**Process**: Schedule pipelines in ADF using triggers that can be time-based (scheduled) or event-based (triggered by data arrival). Use dependency conditions to manage task sequences and ensure that pipelines execute in the correct order and at the right time.

**Example**:

- **Scheduled Trigger**: Set up a daily trigger in ADF to start the pipeline at a specific time each day.
- **Dependency Conditions**: Configure pipeline activities with precedence constraints that ensure a downstream activity only starts if the upstream activities succeed.

### **3. Tracking Information for Pipeline Runs**

**Process**: Track key metrics for each pipeline run to facilitate debugging and optimization. Metrics can include start time, end time, duration, data volume processed, and success/failure status.

**Example**:

- **Logging**: Use Azure SQL Database to log details of each pipeline run. Here's a simple table structure for logging:

 ```sql
 CREATE TABLE PipelineRunLogs (
   RunID INT PRIMARY KEY,
   PipelineName VARCHAR(255),
   StartTime DATETIME,
   EndTime DATETIME,
   DurationInSeconds INT,
   Status VARCHAR(50),
   ErrorMessage VARCHAR(MAX)
 );

### Error Handling in ADF: Use the "Retry" policy in ADF activities to automatically retry failed activities a specified number of times. For example:
{
  "policy": {
    "timeout": "01:00:00",
    "retry": 3,
    "retryIntervalInSeconds": 30,
    "secureOutput": false,
    "secureInput": false
  }
}
Tracking and Alerting: Using Azure Monitor to set up alerts based on logs or metrics that indicate failures. These alerts can help quickly pinpoint issues and initiate recovery processes.
