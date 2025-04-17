import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from database import execute_query, get_sqlalchemy_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reports directory
REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_report_file(data, title, report_type):
    """Generate a report file in Excel format with charts"""
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    filename = os.path.join(REPORTS_DIR, f"{report_type}-{timestamp}.xlsx")
    
    # Create a Pandas Excel writer
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    
    # Write DataFrame to Excel
    df.to_excel(writer, sheet_name='Report', index=False)
    
    # Access the XlsxWriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Report']
    
    # Create a chart object
    if len(data) > 0 and 'total' in df.columns:
        chart = workbook.add_chart({'type': 'column'})
        
        # Configure the series of the chart from the dataframe data
        chart.add_series({
            'name': 'Total',
            'categories': ['Report', 1, 0, len(df), 0],
            'values': ['Report', 1, df.columns.get_loc('total'), len(df), df.columns.get_loc('total')],
        })
        
        # Configure the chart
        chart.set_title({'name': title})
        chart.set_x_axis({'name': 'Items'})
        chart.set_y_axis({'name': 'Amount'})
        
        # Insert the chart into the worksheet
        worksheet.insert_chart('H2', chart)
    
    # Save the Excel file
    writer.save()
    
    return filename

def get_sales_report():
    """Generate sales report from Perfex CRM database"""
    query = """
    SELECT 
        YEAR(date) as year,
        MONTH(date) as month,
        COUNT(*) as count,
        SUM(total) as total
    FROM tblinvoices
    WHERE status != 5 -- Not cancelled
    GROUP BY YEAR(date), MONTH(date)
    ORDER BY YEAR(date) DESC, MONTH(date) DESC
    LIMIT 24; -- Last 24 months
    """
    
    data = execute_query(query)
    
    # Add month name
    for row in data:
        row['month_name'] = time.strftime('%B', time.strptime(str(row['month']), '%m'))
        row['period'] = f"{row['month_name']} {row['year']}"
    
    return generate_report_file(data, 'Sales Report', 'sales')

def get_payments_report():
    """Generate payments report from Perfex CRM database"""
    query = """
    SELECT 
        YEAR(tblinvoicepaymentrecords.date) as year,
        MONTH(tblinvoicepaymentrecords.date) as month,
        COUNT(*) as count,
        SUM(tblinvoicepaymentrecords.amount) as total,
        tblpaymentmodes.name as payment_mode
    FROM tblinvoicepaymentrecords
    LEFT JOIN tblpaymentmodes ON tblpaymentmodes.id = tblinvoicepaymentrecords.paymentmode
    GROUP BY YEAR(tblinvoicepaymentrecords.date), MONTH(tblinvoicepaymentrecords.date), tblpaymentmodes.name
    ORDER BY YEAR(tblinvoicepaymentrecords.date) DESC, MONTH(tblinvoicepaymentrecords.date) DESC
    LIMIT 100;
    """
    
    data = execute_query(query)
    
    # Add month name
    for row in data:
        row['month_name'] = time.strftime('%B', time.strptime(str(row['month']), '%m'))
        row['period'] = f"{row['month_name']} {row['year']}"
    
    return generate_report_file(data, 'Payments Report', 'payments')

def get_invoices_report():
    """Generate invoices report from Perfex CRM database"""
    query = """
    SELECT 
        tblinvoices.id,
        tblinvoices.number,
        tblinvoices.date,
        tblinvoices.duedate,
        tblinvoices.total,
        tblinvoices.subtotal,
        tblinvoices.total_tax,
        tblclients.company as client_name,
        CASE
            WHEN tblinvoices.status = 1 THEN 'Unpaid'
            WHEN tblinvoices.status = 2 THEN 'Paid'
            WHEN tblinvoices.status = 3 THEN 'Partially Paid'
            WHEN tblinvoices.status = 4 THEN 'Overdue'
            WHEN tblinvoices.status = 5 THEN 'Cancelled'
            ELSE 'Unknown'
        END as status_text
    FROM tblinvoices
    LEFT JOIN tblclients ON tblclients.userid = tblinvoices.clientid
    ORDER BY tblinvoices.date DESC
    LIMIT 100;
    """
    
    data = execute_query(query)
    
    return generate_report_file(data, 'Invoices Report', 'invoices')

def get_estimates_report():
    """Generate estimates report from Perfex CRM database"""
    query = """
    SELECT 
        tblestimates.id,
        tblestimates.number,
        tblestimates.date,
        tblestimates.expirydate,
        tblestimates.total,
        tblestimates.subtotal,
        tblestimates.total_tax,
        tblclients.company as client_name,
        CASE
            WHEN tblestimates.status = 1 THEN 'Draft'
            WHEN tblestimates.status = 2 THEN 'Sent'
            WHEN tblestimates.status = 3 THEN 'Declined'
            WHEN tblestimates.status = 4 THEN 'Accepted'
            WHEN tblestimates.status = 5 THEN 'Expired'
            ELSE 'Unknown'
        END as status_text
    FROM tblestimates
    LEFT JOIN tblclients ON tblclients.userid = tblestimates.clientid
    ORDER BY tblestimates.date DESC
    LIMIT 100;
    """
    
    data = execute_query(query)
    
    return generate_report_file(data, 'Estimates Report', 'estimates')

def get_proposals_report():
    """Generate proposals report from Perfex CRM database"""
    query = """
    SELECT 
        tblproposals.id,
        tblproposals.subject,
        tblproposals.datecreated,
        tblproposals.open_till,
        tblproposals.total,
        tblproposals.subtotal,
        tblproposals.total_tax,
        tblclients.company as client_name,
        CASE
            WHEN tblproposals.status = 0 THEN 'Draft'
            WHEN tblproposals.status = 1 THEN 'Open'
            WHEN tblproposals.status = 2 THEN 'Declined'
            WHEN tblproposals.status = 3 THEN 'Accepted'
            WHEN tblproposals.status = 4 THEN 'Sent'
            ELSE 'Unknown'
        END as status_text
    FROM tblproposals
    LEFT JOIN tblclients ON tblclients.userid = tblproposals.rel_id AND tblproposals.rel_type = 'customer'
    ORDER BY tblproposals.datecreated DESC
    LIMIT 100;
    """
    
    data = execute_query(query)
    
    return generate_report_file(data, 'Proposals Report', 'proposals') 