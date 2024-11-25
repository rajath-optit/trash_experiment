import pandas as pd
import os
from datetime import datetime
import xlsxwriter
import matplotlib.pyplot as plt

# Define service categories
categories = {
    'Security and Identity': ['IAM', 'ACM', 'KMS', 'GuardDuty', 'Secret Manager', 'Secret Hub', 'SSM'],
    'Compute': ['Auto Scaling', 'EC2', 'ECS', 'EKS', 'Lambda', 'EMR', 'Step Functions'],
    'Storage': ['EBS', 'ECR', 'S3', 'DLM', 'Backup'],
    'Network': ['API Gateway', 'CloudFront', 'Route 53', 'VPC', 'ELB', 'ElasticCache', 'CloudTrail'],
    'Database': ['RDS', 'DynamoDB', 'Athena', 'Glue'],
    'Other': ['CloudFormation', 'CodeDeploy', 'Config', 'SNS', 'SQS', 'WorkSpaces', 'EventBridge', 'Config']
}

# Map numerical priorities to words
priority_map = {1: "High", 2: "Medium", 3: "Low"}

def create_simplified_report_with_pivot(report_file, final_report_file):
    # Read input report file (CSV or Excel)
    if report_file.endswith('.csv'):
        df = pd.read_csv(report_file)
    elif report_file.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(report_file)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
    
    # Ensure 'status' column is clean (convert to string if necessary)
    df['status'] = df['status'].astype(str)

    # Map status to "safe" or "open issue"
    df['is_open_issue'] = df['status'].apply(lambda x: 1 if x == 'alarm' else 0)

    # Replace numerical priority with words
    df['priority'] = df['priority'].map(priority_map)

    # Create a new Excel writer object to write multiple sheets
    with pd.ExcelWriter(final_report_file, engine='xlsxwriter') as writer:
        # Write the 'safe' and 'unsafe' DataFrames to separate sheets
        safe_df = df[df['status'] != 'alarm']
        unsafe_df = df[df['status'] == 'alarm']
        safe_df.to_excel(writer, sheet_name='safe', index=False)
        unsafe_df.to_excel(writer, sheet_name='unsafe', index=False)

        # Initialize a list to collect data for the final summary table
        summary_data = []
        sr_no = 1
        
        # Process each service and leave a one-line gap after each service
        for service in categories.keys():
            service_df = df[df['title'].isin(categories[service])]
            
            # Group by Control Title and sum Open Issues per title
            service_grouped = service_df.groupby(
                ['title', 'control_title', 'control_description', 'priority'], as_index=False
            ).agg({'is_open_issue': 'sum'})

            # Add grouped data to summary table
            for _, row in service_grouped.iterrows():
                summary_data.append({
                    'Sr No': sr_no,
                    'Service': row['title'],
                    'Control Title': row['control_title'],
                    'Description': row['control_description'],
                    'Open Issues': row['is_open_issue'],
                    'Priority': row['priority']
                })
                sr_no += 1
            
            # Insert a blank row to separate services (if we have added any data)
            if summary_data:
                summary_data.append({
                    'Sr No': '',
                    'Service': '',
                    'Control Title': '',
                    'Description': '',
                    'Open Issues': '',
                    'Priority': ''
                })

        # Convert the summary data to a DataFrame
        summary_df = pd.DataFrame(summary_data)

        # Write the summary table to the 'table' sheet
        summary_df.to_excel(writer, sheet_name='table', index=False)

        # Create the 'table_safe' sheet, similar to the 'table' sheet but for safe controls
        safe_summary_data = []
        sr_no_safe = 1
        
        for service in categories.keys():
            service_df_safe = safe_df[safe_df['title'].isin(categories[service])]
            
            # Group by Control Title and sum Open Issues per title (safe controls)
            service_grouped_safe = service_df_safe.groupby(
                ['title', 'control_title', 'control_description', 'priority'], as_index=False
            ).agg({'is_open_issue': 'sum'})

            # Add grouped data to the safe summary table
            for _, row in service_grouped_safe.iterrows():
                safe_summary_data.append({
                    'Sr No': sr_no_safe,
                    'Service': row['title'],
                    'Control Title': row['control_title'],
                    'Description': row['control_description'],
                    'Open Issues': row['is_open_issue'],
                    'Priority': row['priority']
                })
                sr_no_safe += 1
            
            # Insert a blank row to separate services
            if safe_summary_data:
                safe_summary_data.append({
                    'Sr No': '',
                    'Service': '',
                    'Control Title': '',
                    'Description': '',
                    'Open Issues': '',
                    'Priority': ''
                })

        # Convert the safe summary data to a DataFrame
        safe_summary_df = pd.DataFrame(safe_summary_data)

        # Write the summary table to the 'table_safe' sheet
        safe_summary_df.to_excel(writer, sheet_name='table_safe', index=False)

        # Create an 'experiment' sheet to test graphs
        experiment_data = pd.DataFrame({
            'title': ['Account', 'ACM', 'EC2', 'S3'],
            'control_title': ['AWS account should be part of AWS Organizations', 'ACM certificates should not expire', 'EC2 instances should be secured', 'S3 should be encrypted'],
            'control_description': ['Ensure AWS account is part of Organizations', 'Ensure certificates are not expiring', 'Ensure EC2 is secure', 'Ensure S3 is encrypted'],
            'region': ['global', 'ap-south-1', 'us-east-1', 'us-west-1'],
            'account_id': ['376921607482', '376921607483', '376921607484', '376921607485'],
            'resource': ['arn:aws::', 'arn:aws:acm:', 'arn:aws:ec2:', 'arn:aws:s3:'],
            'reason': ['CapitalMindTech', 'CapitalMindTech', 'CapitalMindTech', 'CapitalMindTech'],
            'priority': [1, 2, 3, 1],
            'status': ['ok', 'alarm', 'ok', 'alarm']
        })

        experiment_data.to_excel(writer, sheet_name='experiment', index=False)
        
    print(f"Final report with pivot table saved as {final_report_file}")

def create_graphs(df, final_report_file):
    # Plot Open Issues by Service (Unsafe)
    plt.figure(figsize=(10, 6))
    open_issues_by_service = df.groupby('title')['is_open_issue'].sum()
    open_issues_by_service.plot(kind='bar', color='skyblue', title="Open Issues by Service")
    plt.ylabel('Open Issues')
    plt.xlabel('Service')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(final_report_file.replace('.xlsx', '_open_issues_by_service.png'))
    plt.close()

    # Plot Safe Controls by Service (Safe)
    plt.figure(figsize=(10, 6))
    safe_controls_by_service = df[df['status'] != 'alarm'].groupby('title').size()
    safe_controls_by_service.plot(kind='bar', color='lightgreen', title="Safe Controls by Service")
    plt.ylabel('Safe Controls')
    plt.xlabel('Service')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(final_report_file.replace('.xlsx', '_safe_controls_by_service.png'))
    plt.close()

    # Priority Breakdown (Open Issues)
    plt.figure(figsize=(10, 6))
    priority_breakdown = df.groupby('priority')['is_open_issue'].sum()
    priority_breakdown.plot(kind='pie', autopct='%1.1f%%', title="Open Issues by Priority")
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(final_report_file.replace('.xlsx', '_priority_breakdown.png'))
    plt.close()

    # Safe vs Unsafe Controls (Pie Chart)
    plt.figure(figsize=(10, 6))
    safe_unsafe_controls = [df[df['status'] != 'alarm'].shape[0], df[df['status'] == 'alarm'].shape[0]]
    plt.pie(safe_unsafe_controls, labels=['Safe Controls', 'Unsafe Controls'], autopct='%1.1f%%', startangle=90)
    plt.title('Safe vs Unsafe Controls')
    plt.tight_layout()
    plt.savefig(final_report_file.replace('.xlsx', '_safe_vs_unsafe_controls.png'))
    plt.close()

    print("Graphs created successfully!")

def main():
    # Ask the user to input the report file name
    report_file = input("Enter the report file name (e.g., aws_compliance_benchmark.csv): ").strip()

    # Validate if the file exists
    if not os.path.exists(report_file):
        print(f"File '{report_file}' not found.")
        return

    # Define the output file name for the final report
    final_report_file = f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    # Generate the report
    create_simplified_report_with_pivot(report_file, final_report_file)
    
    # Load the dataframe for graph creation
    df = pd.read_excel(final_report_file, sheet_name='safe')

    # Create graphs
    create_graphs(df, final_report_file)

if __name__ == "__main__":
    main()
