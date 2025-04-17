import os
import time
import xlsxwriter
from database import execute_query
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()

# Reports directory
REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_report_file(data, title, report_type):
    """Generate a report file in Excel format"""
    # Create a BytesIO object to store the Excel file in memory
    output = BytesIO()
    
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Report')
    
    # Add a bold format for headers
    bold = workbook.add_format({'bold': True})
    
    # Write headers
    if data:
        headers = list(data[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, bold)
        
        # Write data
        for row, item in enumerate(data, start=1):
            for col, key in enumerate(headers):
                worksheet.write(row, col, item.get(key, ''))
        
        # Add a chart if there's a 'total' column
        if 'total' in headers:
            chart = workbook.add_chart({'type': 'column'})
            
            # Configure the series of the chart
            chart.add_series({
                'name': 'Total',
                'categories': ['Report', 1, 0, len(data), 0],
                'values': ['Report', 1, headers.index('total'), len(data), headers.index('total')],
            })
            
            # Configure the chart
            chart.set_title({'name': title})
            chart.set_x_axis({'name': 'Items'})
            chart.set_y_axis({'name': 'Amount'})
            
            # Insert the chart into the worksheet
            worksheet.insert_chart('H2', chart)
    
    # Close the workbook
    workbook.close()
    
    # Reset the buffer position
    output.seek(0)
    
    return output

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