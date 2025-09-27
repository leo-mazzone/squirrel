from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine

from squirrel.dag import ask
from squirrel.dates import process_question_dates


def test_date_integration_with_dag():
    """Integration test: verify date processing works end-to-end with the DAG"""
    engine = create_engine("sqlite:///chinook.db")
    response, debug = ask("What invoices were created this year?", engine)

    # Extract the generated SQL from debug info
    retriever_node = [
        d
        for d in debug
        if d["payload"]["name"] == "retriever_node" and d["type"] == "task_result"
    ][0]
    sql = dict(retriever_node["payload"]["result"])["sql"]

    current_year = datetime.now().year

    # Verify the SQL contains a filter for the current year
    assert str(current_year) in sql.lower()
    # Verify we got a meaningful response (not a refusal)
    assert "cannot answer" not in response.lower()


# Direct tests for exact SQL filter generation


def test_this_year_sql_filter():
    """Test that 'this year' generates exactly the right SQL filter"""
    result = process_question_dates("What invoices were created this year?")

    current_year = datetime.now().year
    expected_filter = f"BETWEEN '{current_year}-01-01' AND '{current_year}-12-31'"

    sql_filters = result["sql_date_filters"]
    assert len(sql_filters) == 1
    assert sql_filters[0] == expected_filter


def test_last_year_sql_filter():
    """Test that 'last year' generates exactly the right SQL filter"""
    result = process_question_dates("What invoices were created last year?")

    last_year = datetime.now().year - 1
    expected_filter = f"BETWEEN '{last_year}-01-01' AND '{last_year}-12-31'"

    sql_filters = result["sql_date_filters"]
    assert len(sql_filters) == 1
    assert sql_filters[0] == expected_filter


def test_this_month_sql_filter():
    """Test that 'this month' generates exactly the right SQL filter"""
    result = process_question_dates("What invoices were created this month?")

    now = datetime.now()
    # Calculate last day of current month
    next_month = now.replace(day=28) + relativedelta(days=4)
    last_day = (next_month - relativedelta(days=next_month.day)).day

    expected_filter = (
        f"BETWEEN '{now.year}-{now.month:02d}-01' "
        f"AND '{now.year}-{now.month:02d}-{last_day:02d}'"
    )

    sql_filters = result["sql_date_filters"]
    assert len(sql_filters) == 1
    assert sql_filters[0] == expected_filter


def test_last_month_sql_filter():
    """Test that 'last month' generates exactly the right SQL filter"""
    result = process_question_dates("What invoices were created last month?")

    last_month = datetime.now() - relativedelta(months=1)
    # Calculate last day of last month
    next_month = last_month.replace(day=28) + relativedelta(days=4)
    last_day = (next_month - relativedelta(days=next_month.day)).day

    expected_filter = (
        f"BETWEEN '{last_month.year}-{last_month.month:02d}-01' "
        f"AND '{last_month.year}-{last_month.month:02d}-{last_day:02d}'"
    )

    sql_filters = result["sql_date_filters"]
    assert len(sql_filters) == 1
    assert sql_filters[0] == expected_filter


def test_explicit_year_sql_filter():
    """Test that explicit years generate exactly the right SQL filter"""
    result = process_question_dates("What invoices were created in 2023?")

    expected_filter = "BETWEEN '2023-01-01' AND '2023-12-31'"

    sql_filters = result["sql_date_filters"]
    assert len(sql_filters) == 1
    assert sql_filters[0] == expected_filter


def test_date_range_sql_filter():
    """Test that date ranges generate exactly the right SQL filter"""
    result = process_question_dates("What invoices were created between 2020 and 2022?")

    expected_filter = "BETWEEN '2020-01-01' AND '2022-12-31'"

    sql_filters = result["sql_date_filters"]
    assert len(sql_filters) == 1
    assert sql_filters[0] == expected_filter


def test_no_dates_empty_filters():
    """Test that questions without dates have empty SQL filters"""
    result = process_question_dates("What is the total number of genres?")

    sql_filters = result["sql_date_filters"]
    assert len(sql_filters) == 0
