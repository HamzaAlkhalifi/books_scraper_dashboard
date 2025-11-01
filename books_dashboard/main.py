from dash import Dash, Input, Output, callback, dcc, html, callback_context
import dash_bootstrap_components as dbc
import id
import duckdb
from plotly.subplots import make_subplots
import plotly.express as px 

def selectAllBtn() -> dbc.Col:
    return dbc.Col(
            dbc.Button("Select All", id= id.SELECT_ALL_BTN)
    )

def clearAllBtn() -> dbc.Col:
    return dbc.Col(
        dbc.Button("Clear All", id= id.CLEAR_ALL_BTN)
    )


def selectCategory() -> dbc.Col:

    with duckdb.connect("library.ddb") as conn:
        df = conn.sql("SELECT DISTINCT category FROM books")
        categories = [row[0] for row in df.fetchall()]

    @callback(
        Output(id.SELECT_CATEGORY, "value"),
        Input(id.SELECT_ALL_BTN, "n_clicks"),
        Input(id.CLEAR_ALL_BTN, "n_clicks"),
        prevent_initial_call=True
    )
    def selectAll(n, n_c):
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == id.SELECT_ALL_BTN:
            return categories
        elif triggered_id == id.CLEAR_ALL_BTN:
            return []

    return dbc.Col([
        dbc.DropdownMenu(
            label="Select Categories",
            children=[
                dbc.Checklist(
                    options=[{"label": cat, "value": cat} for cat in categories],
                    value=categories,
                    id=id.SELECT_CATEGORY,
                    inline=True,
                    className="dropdown-checklist"
                )
            ])        
    ], width=8,)


def filtersLayout() -> dbc.Row:
    return dbc.Row([
                selectCategory(),
                selectAllBtn(),
                clearAllBtn()
            ], align="center", justify="between")
#============================================



def summaryValues() -> dbc.Col:
    @callback(
        Output(id.SUMMARY_VALUES, "children"),
        Input(id.SELECT_CATEGORY, "value")
    )
    def summary(value):
        if value:
            with duckdb.connect("library.ddb") as conn:
                placeholders = ",".join("?" for _ in value)
                df= conn.execute(f"SELECT AVG(price) FROM books WHERE category IN ({placeholders})", value)
                avg= df.fetchone()[0]
                highest = conn.execute(
                    f"""
                        SELECT title, category, price 
                        FROM books 
                        WHERE category IN ({placeholders}) 
                        ORDER BY price DESC 
                        LIMIT 5
                    """,
                    value
                ).fetchall()
            if avg is None:
                return dbc.Alert("No data found for selected categories.", color="info")

            highest_paragraphs = [
                html.P(f"- {title} | {cat} | ${price:.2f}") 
                for title, cat, price in highest
            ]
            
            return dbc.Card([
                dbc.CardHeader([
                    html.H4("AVG Price of the Selected Categories"),
                    html.H1(f"{avg:.2f}")]),
                dbc.CardBody([
                    html.H6("These books are the highest by price:"),
                    *highest_paragraphs,
                ]),
            ])
        else:
            return dbc.Alert("You Have Not Selected any Category", color="warning")

    return dbc.Col(id= id.SUMMARY_VALUES, align="left")



def bar_line_chart() -> dbc.Col:
    @callback(
        Output(id.CHART, "children"),
        Input(id.SELECT_CATEGORY, "value")
    )
    def chart(value):
        if value:
            with duckdb.connect("library.ddb") as conn:
                placeholders = ",".join("?" for _ in value)

                df= conn.execute(f"""
                    SELECT category,
                            count(*) as count, 
                            avg(price) as price 
                    FROM books 
                    GROUP BY category 
                    HAVING category IN ({placeholders})""",
                    value).df()
                

            fig = make_subplots(specs=[[{"secondary_y":True}]])

            bar_plot = px.bar(df, x= "category", y= "count", color_discrete_sequence=["skyblue"])
            bar_plot.update_traces(name= "Count", showlegend= True)
            for trace in bar_plot.data:
                fig.add_trace(trace, secondary_y=False)


            line_plot = px.line(df, x="category", y="price", color_discrete_sequence=['purple'], line_shape= "spline", markers=True)
            line_plot.update_traces(line=dict(width= 2, dash="dot"), opacity= 0.7, name="AVG. Price", showlegend= True)
            for trace in line_plot.data:
                fig.add_trace(trace, secondary_y=True)

            fig.update_layout(title="<b>Categories Count</b><br><sup>& AVG. Price</sup>", xaxis_title= "Category",
                              hovermode="x unified", font=dict(family="Arial", size=14, color="#888888"), height=600,)
            fig.update_yaxes(title="Count",secondary_y=False, showgrid=False)
            fig.update_yaxes(title="AVG. Price", secondary_y=True, showgrid= False)


                        
            return dcc.Graph(figure=fig)
        else:
            return dbc.Alert("You Have Not Selected any Category", color="warning")            

    return dbc.Col(id= id.CHART, width=8)

def dashboardLayout() -> dbc.Row:
    return dbc.Row([
        summaryValues(),
        bar_line_chart(),
    ], align="center")



def main():
    app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
    app.layout = dbc.Container([dbc.Stack([
        filtersLayout(),
        dashboardLayout(),
    ], gap=3)], class_name="mt-4")
    app.run()
    
if __name__ == "__main__":
    main()
