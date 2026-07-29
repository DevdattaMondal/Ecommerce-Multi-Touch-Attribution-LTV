import duckdb
import pandas as pd
from pathlib import Path

# Base directory where this script is located
BASE_DIR = Path(__file__).resolve().parent

# Database path
DB_FILE = BASE_DIR / "thelook_ecommerce.db"

# Output directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

def run_sql_transformations():
    con = duckdb.connect(str(DB_FILE))
    print("Connected to DuckDB for SQL transformations...\n")

    # 1. Build Conversion Paths
    conversion_paths_query = """
    WITH completed_orders AS (
        SELECT
            o.order_id,
            o.user_id,
            o.created_at AS order_created_at,
            SUM(oi.sale_price) AS order_value
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status NOT IN ('Cancelled', 'Returned')
        GROUP BY o.order_id, o.user_id, o.created_at
    ),
    user_touchpoints AS (
        SELECT
            co.order_id,
            co.user_id,
            co.order_value,
            e.traffic_source,
            e.created_at AS event_time
        FROM completed_orders co
        JOIN events e
            ON co.user_id = e.user_id
            AND e.created_at <= co.order_created_at
    ),
    ordered_paths AS (
        SELECT
            order_id,
            user_id,
            order_value,
            traffic_source,
            ROW_NUMBER() OVER (
                PARTITION BY order_id
                ORDER BY event_time ASC
            ) AS touch_order
        FROM user_touchpoints
    )
    SELECT
        order_id,
        user_id,
        order_value,
        STRING_AGG(traffic_source, ' > ') AS path
    FROM ordered_paths
    GROUP BY order_id, user_id, order_value;
    """

    df_paths = con.execute(conversion_paths_query).df()
    output_file = DATA_DIR / "conversion_paths.csv"
    df_paths.to_csv(output_file, index=False)

    print(f"Saved {len(df_paths):,} rows to {output_file}")

    # 2. Extract LTV Cohort Data
    cohort_data_query = """
    SELECT
        u.id AS user_id,
        DATE_TRUNC('month', CAST(u.created_at AS DATE)) AS signup_month,
        DATE_TRUNC('month', CAST(o.created_at AS DATE)) AS transaction_month,
        DATEDIFF(
            'month',
            DATE_TRUNC('month', CAST(u.created_at AS DATE)),
            DATE_TRUNC('month', CAST(o.created_at AS DATE))
        ) AS month_offset,
        SUM(oi.sale_price) AS net_revenue
    FROM users u
    JOIN orders o
        ON u.id = o.user_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('Cancelled', 'Returned')
    GROUP BY 1,2,3,4;
    """

    df_cohort = con.execute(cohort_data_query).df()

    output_file = DATA_DIR / "cohort_raw_data.csv"
    df_cohort.to_csv(output_file, index=False)

    print(f"Saved {len(df_cohort):,} rows to {output_file}")

    print("\n" + "=" * 50)
    print("SQL TRANSFORMATIONS COMPLETED")
    print("=" * 50)
    print(f"Conversion Paths : {len(df_paths):,}")
    print(f"Cohort Records   : {len(df_cohort):,}")
    print(f"Output Folder    : {DATA_DIR}")
    print("=" * 50)

    con.close()


if __name__ == "__main__":
    run_sql_transformations()
