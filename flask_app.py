from flask import Flask, render_template
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objs as go

app = Flask(__name__)

# Set up database connection parameters
dbname = "E-Commerce_Transactions_db"
user = "postgres"
password = "postgres"
host = "localhost" 
port = "5432"

# Function to establish database connection
def connect_to_database():
    try:
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        print("Database connection established.")
        return connection
    except Exception as e:
        print("An error occurred while connecting to the database:", e)
        return None

# Homepage route
@app.route('/')
def homepage():
    return render_template('dashboard.html')

# Route to handle map visualization
@app.route('/map')
def map():
    try:
        connection = connect_to_database()
        if connection is None:
            return "Unable to establish database connection."

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM ecommerce_transactions;")

        rows = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]

        ecomm_transactions_df = pd.DataFrame(rows, columns=column_names)

        # Cleaning 1 (Addresses)
        ecomm_transactions_df['shipping_address'] = ecomm_transactions_df['shipping_address'].str.replace('\n', ', ')
        ecomm_transactions_df['billing_address'] = ecomm_transactions_df['billing_address'].str.replace('\n', ', ')

        # Clean 2 
        clean_transactn_df = ecomm_transactions_df.copy()

        clean_transactn_df['shipping_state'] = ecomm_transactions_df['shipping_address'].str.extract(r',\s*([A-Za-z]{2})\s*\d{5}')
        clean_transactn_df['billing_state'] = ecomm_transactions_df['billing_address'].str.extract(r',\s*([A-Za-z]{2})\s*\d{5}')

        states = pd.concat([clean_transactn_df['shipping_state'], clean_transactn_df['billing_state']], axis=0)

        # Remove duplicates and sort
        states = states.drop_duplicates().sort_values()

        fraudulent_transactions_by_state = clean_transactn_df[clean_transactn_df['is_fraudulent'] == 1].groupby('shipping_state').size()

        # Create map visualization
        state_map = go.Figure(data=go.Choropleth(
            locations=states,
            z=fraudulent_transactions_by_state,
            locationmode='USA-states',
            colorscale='Reds',
            colorbar_title='Fraudulent Transactions'
        ))

        state_map.update_layout(
            title_text='Fraudulent Transactions by State',
            geo_scope='usa',
            geo=dict(
                showcoastlines=True,  # Show state boundaries
                projection_type='albers usa',  # Use Albers USA projection
                lataxis=dict(range=[25, 50]),  # Set latitude axis range
                lonaxis=dict(range=[-130, -65]),  # Set longitude axis range
            ),
            margin=dict(l=0, r=0, t=0, b=0),  # Adjust margins to make the plot tight
            width=800,  # Set width of the plot
            height=500  # Set height of the plot
        )

        cursor.close()
        connection.close()

        # Generate HTML code for the map
        map_html = state_map.to_html(full_html=False)

        return render_template('dashboard.html', map_html=map_html)

    except Exception as e:
        return "An error occurred: {}".format(e)

# Route to handle bar chart
@app.route('/barchart')
def barchart():
    try:
        connection = connect_to_database()
        if connection is None:
            return "Unable to establish database connection."

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ecommerce_transactions WHERE is_fraudulent = 1;")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        ecomm_transactions_df = pd.DataFrame(rows, columns=column_names)

        fraudulent_transactions_df = ecomm_transactions_df[ecomm_transactions_df['is_fraudulent'] == 1]

        connection.close()

        fig = px.bar(fraudulent_transactions_df, x='payment_method', y='transaction_amount', 
                     title='Transaction Amount by Payment Method',
                     labels={'transaction_amount': 'Transaction Amount', 'payment_method': 'Payment Method'})

        plot_div = fig.to_html(full_html=False)

        return render_template('dashboard.html', plot_div=plot_div)

    except Exception as e:
        return "An error occurred: {}".format(e)

# Route to handle seasonal charts
@app.route('/seasons')
def chart():
    try:
        connection = connect_to_database()
        if connection is None:
            return "Unable to establish database connection."

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ecommerce_transactions WHERE is_fraudulent = 1;")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        ecomm_transactions_df = pd.DataFrame(rows, columns=column_names)

        def categorize_season(transaction_date):
            transaction_date = pd.Timestamp(transaction_date)
            if spring_begin <= transaction_date <= spring_end:
                return 'Spring'
            elif transaction_date >= winter_begin or transaction_date <= winter_end:
                return "Winter"

        winter_begin = pd.Timestamp('2023-12-01')
        winter_end = pd.Timestamp('2023-03-19')
        spring_begin = pd.Timestamp('2024-03-20')
        spring_end = pd.Timestamp('2024-06-20')

        ecomm_transactions_df['Seasons'] = ecomm_transactions_df['transaction_date'].apply(categorize_season)

        connection.close()

        season_result = ecomm_transactions_df.groupby(['Seasons', 'product_category'])['is_fraudulent'].sum().reset_index()

        spring_data = season_result[season_result['Seasons'] == 'Spring']
        winter_data = season_result[season_result['Seasons'] == 'Winter']

        fig = px.bar(spring_data, x='product_category', y='is_fraudulent', 
                     title='Fraudulent Transactions by Product Category in Spring',
                     labels={'is_fraudulent': 'Number of Fraudulent Transactions', 'product_category': 'Product Category'})

        fig2 = px.bar(winter_data, x='product_category', y='is_fraudulent', 
                      title='Fraudulent Transactions by Product Category in Winter',
                      labels={'is_fraudulent': 'Number of Fraudulent Transactions', 'product_category': 'Product Category'})

        spring_plot_div = fig.to_html(full_html=False)
        winter_plot_div = fig2.to_html(full_html=False)

        return render_template('dashboard.html', spring_plot_div=spring_plot_div, winter_plot_div=winter_plot_div)

    except Exception as e:
        return "An error occurred: {}".format(e)

# Define main behavior
if __name__ == '__main__':
    app.run(debug=True)