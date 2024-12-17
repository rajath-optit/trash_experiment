import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
import xlsxwriter
import json
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='compliance_report.log'
)

# Advanced Configuration
class ComplianceConfig:
    """
    Centralized configuration management for compliance reporting
    """
    # Service criticality weights
    SERVICE_CRITICALITY = {
        'Security and Identity': 1.5,
        'Compute': 1.3,
        'Database': 1.4,
        'Network': 1.2,
        'Storage': 1.1,
        'Other': 1.0
    }

    # Priority impact scores
    PRIORITY_IMPACT = {
        'High': 10,
        'Medium': 5,
        'Low': 2,
        'Safe': 0
    }

    # Color mapping for reporting
    COLOR_MAP = {
        'High': '#FF0000',     # Red
        'Medium': '#FFA500',   # Orange
        'Low': '#FFFF00',      # Yellow
        'Safe': '#00FF00',     # Green
        'No Priority': '#C0C0C0'  # Gray
    }

# Define service categories
CATEGORIES = {
    'Security and Identity': ['IAM', 'ACM', 'KMS', 'GuardDuty', 'Secret Manager', 'Secret Hub', 'SSM'],
    'Compute': ['Auto Scaling', 'EC2', 'ECS', 'EKS', 'Lambda', 'EMR', 'Step Functions'],
    'Storage': ['EBS', 'ECR', 'S3', 'DLM', 'Backup'],
    'Network': ['API Gateway', 'CloudFront', 'Route 53', 'VPC', 'ELB', 'ElasticCache', 'CloudTrail'],
    'Database': ['RDS', 'DynamoDB', 'Athena', 'Glue'],
    'Other': ['CloudFormation', 'CodeDeploy', 'Config', 'SNS', 'SQS', 'WorkSpaces', 'EventBridge']
}

class AdvancedComplianceReporter:
    def __init__(self, 
                 input_file: str, 
                 priority_file: str = "PowerPipeControls_Annotations.xlsx",
                 config: ComplianceConfig = None):
        """
        Advanced AWS Compliance Reporter Initialization
        
        Args:
            input_file (str): Path to input compliance report
            priority_file (str): Path to priority annotations
            config (ComplianceConfig): Custom configuration object
        """
        self.input_file = input_file
        self.priority_file = priority_file
        self.config = config or ComplianceConfig()
        self.temp_dir = "compliance_reports"  # Directory for reports and plots

        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)

        # Metadata tracking
        self.metadata = {
            'report_timestamp': datetime.now(),
            'total_controls': 0,
            'compliance_score': 0.0,
            'trend_analysis': {},
            'risk_profile': {}
        }
        
        # Initialize data
        try:
            self.df = self._load_input_file()
            self.priority_df = self._load_priority_database()
            logging.info(f"Successfully loaded input file: {input_file}")
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            raise

    def _load_input_file(self):
        """
        Load input file with advanced error handling
        """
        try:
            if self.input_file.endswith(".csv"):
                return pd.read_csv(self.input_file, low_memory=False)
            elif self.input_file.endswith((".xlsx", ".xls")):
                return pd.read_excel(self.input_file, engine='openpyxl')
            else:
                raise ValueError("Unsupported file type. Use CSV or Excel.")
        except Exception as e:
            logging.error(f"Error loading input file: {e}")
            raise

    def _load_priority_database(self):
        """
        Load priority database with error handling
        """
        try:
            return pd.read_excel(self.priority_file)
        except Exception as e:
            logging.error(f"Error loading priority database: {e}")
            raise

    def enrich_data(self):
        """
        Advanced data enrichment with risk scoring
        """
        enriched_df = self.df.copy()
        
        for idx, row in enriched_df.iterrows():
            control_title = row.get("control_title", "")
            status = row.get("status", "")

            # Find matching priority row
            matching_row = self.priority_df[self.priority_df["control_title"] == control_title]

            if not matching_row.empty:
                priority = matching_row.iloc[0]["priority"]
                recommendation = matching_row.iloc[0]["Recommendation Steps/Approach"]

                # Risk calculation
                risk_score = self._calculate_risk_score(priority, status)
                
                # Assign enriched data
                enriched_df.at[idx, "priority"] = priority
                enriched_df.at[idx, "Recommendation Steps/Approach"] = recommendation
                enriched_df.at[idx, "risk_score"] = risk_score
            else:
                # Default values if no match
                enriched_df.at[idx, "priority"] = "No Priority"
                enriched_df.at[idx, "Recommendation Steps/Approach"] = "No recommendation available"
                enriched_df.at[idx, "risk_score"] = 0

        return enriched_df

    def _calculate_risk_score(self, priority: str, status: str) -> float:
        """
        Comprehensive risk scoring mechanism
        
        Args:
            priority (str): Issue priority
            status (str): Compliance status
        
        Returns:
            float: Calculated risk score
        """
        # Base priority impact
        priority_impact = self.config.PRIORITY_IMPACT.get(priority, 0)
        
        # Status multiplier
        status_multiplier = {
            'alarm': 1.5,
            'ok': 0.1,
            'info': 0.2,
            'skip': 0.1
        }.get(status, 1)
        
        # Calculate risk score
        risk_score = priority_impact * status_multiplier
        
        return round(risk_score, 2)

    def calculate_compliance_score(self):
        """
        Compute comprehensive compliance health score
        """
        total_controls = len(self.df)
        passed_controls = len(self.df[self.df['status'].isin(['ok', 'info', 'skip'])])
        
        # Weighted compliance calculation
        compliance_score = (passed_controls / total_controls) * 100
        
        # Store metadata
        self.metadata['total_controls'] = total_controls
        self.metadata['compliance_score'] = compliance_score
        
        return compliance_score

    def generate_executive_summary(self, enriched_df):
        """
        Create a detailed, actionable executive summary
        """
        # Calculate compliance score
        compliance_score = self.calculate_compliance_score()
        
        # Identify high-risk services
        high_risk_services = (
            enriched_df[enriched_df['risk_score'] > 5]
            .groupby('title')['risk_score']
            .sum()
            .nlargest(5)
        )
        
        # Generate summary
        summary = {
            'Report Timestamp': str(self.metadata['report_timestamp']),
            'Overall Compliance Score': f"{compliance_score:.2f}%",
            'Total Controls': self.metadata['total_controls'],
            'Key Findings': {
                'High Risk Services': dict(high_risk_services),
                'Top Recommendations': self._extract_top_recommendations(enriched_df)
            }
        }
        
        # Log summary
        logging.info(f"Executive Summary Generated: {json.dumps(summary, indent=2)}")
        
        return summary

    def _extract_top_recommendations(self, enriched_df, top_n=5):
        """
        Extract top recommendations based on risk score
        """
        recommendations = (
            enriched_df[enriched_df['risk_score'] > 0]
            .sort_values('risk_score', ascending=False)
            .head(top_n)[['title', 'control_title', 'Recommendation Steps/Approach', 'risk_score']]
        )
        
        return recommendations.to_dict('records')

    def generate_visualizations(self, enriched_df):
        """
        Generate multiple visualizations for the report
        """
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)

        # 1. Priority Distribution Heatmap
        plt.figure(figsize=(12, 8))
        priority_pivot = pd.pivot_table(
            enriched_df, 
            index='title', 
            columns='priority', 
            aggfunc='size', 
            fill_value=0
        )
        
        sns.heatmap(priority_pivot, annot=True, cmap='YlOrRd', fmt='g')
        plt.title('AWS Compliance Priority Distribution')
        plt.xlabel('Priority')
        plt.ylabel('Services')
        plt.tight_layout()
        heatmap_path = os.path.join(self.temp_dir, 'priority_heatmap.png')
        plt.savefig(heatmap_path)
        plt.close()

        # 2. Risk Score Bar Chart
        plt.figure(figsize=(12, 6))
        risk_by_service = enriched_df.groupby('title')['risk_score'].sum()
        risk_by_service.sort_values(ascending=False).plot(kind='bar')
        plt.title('Cumulative Risk Score by AWS Service')
        plt.xlabel('Service')
        plt.ylabel('Cumulative Risk Score')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        risk_chart_path = os.path.join(self.temp_dir, 'risk_score_chart.png')
        plt.savefig(risk_chart_path)
        plt.close()

        return {
            'heatmap_path': heatmap_path,
            'risk_chart_path': risk_chart_path
        }

    def generate_comprehensive_report(self):
        """
        Generate comprehensive report with multiple analysis sheets
        """
        # Enrich data
        enriched_df = self.enrich_data()

        # Generate unique filename
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Excel report
        output_file = os.path.join(self.temp_dir, f"{base_name}_compliance_report_{timestamp}.xlsx")

        # Generate executive summary
        exec_summary = self.generate_executive_summary(enriched_df)

        # Generate visualizations
        viz_paths = self.generate_visualizations(enriched_df)

        # Save executive summary to JSON
        json_file = os.path.join(self.temp_dir, f"{base_name}_executive_summary_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(exec_summary, f, indent=2)

        # Create Excel Report
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Raw Data Sheet
            enriched_df.to_excel(writer, sheet_name='Compliance Data', index=False)
            
            # Priority Summary Sheet
            priority_summary = enriched_df.groupby('priority').size().reset_index(name='count')
            priority_summary.to_excel(writer, sheet_name='Priority Summary', index=False)

        print(f"Comprehensive report generated:")
        print(f"- Excel Report: {output_file}")
        print(f"- Executive Summary: {json_file}")
        print(f"- Heatmap: {viz_paths['heatmap_path']}")
        print(f"- Risk Score Chart: {viz_paths['risk_chart_path']}")

        return {
            'excel_report': output_file,
            'executive_summary': json_file,
            'visualizations': viz_paths
        }

def main():
    print("Advanced AWS Compliance Reporting Tool")
    
    # Input file selection
    input_file = input("Enter input compliance report file (CSV/Excel): ").strip()
    
    try:
        # Optional priority file
        priority_file = input("Enter priority annotations file (default: PowerPipeControls_Annotations.xlsx): ").strip() or "PowerPipeControls_Annotations.xlsx"
        
        # Create advanced reporter
        reporter = AdvancedComplianceReporter(input_file, priority_file)
        
        # Generate comprehensive report
        reporter.generate_comprehensive_report()

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
