import pandas as pd


def clean_inbound_data(input_path, output_path):
    """
    Cleans the inbound data by converting date columns, handling missing values,
    and removing outliers.
    """
    df = pd.read_csv(input_path)

    # Convert INBOUND_DATE to datetime and handle potential errors
    df["INBOUND_DATE"] = pd.to_datetime(df["INBOUND_DATE"], errors="coerce")

    # Drop rows where INBOUND_DATE is NaT (due to conversion errors)
    df.dropna(subset=["INBOUND_DATE"], inplace=True)

    # Handle missing values in other columns (e.g., fill with a specific value or drop)
    # For this case, we'll drop rows with any missing values
    df.dropna(inplace=True)

    # Remove outliers in NET_QUANTITY_MT using the IQR method
    Q1 = df["NET_QUANTITY_MT"].quantile(0.25)
    Q3 = df["NET_QUANTITY_MT"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[
        (df["NET_QUANTITY_MT"] >= lower_bound) & (df["NET_QUANTITY_MT"] <= upper_bound)
    ]

    # Save the cleaned data
    df.to_csv(output_path, index=False)
    print(f"Cleaned inbound data saved to {output_path}")


def clean_outbound_data(input_path, output_path):
    """
    Cleans the outbound data by converting date columns, handling missing values,
    and removing outliers.
    """
    df = pd.read_csv(input_path)

    # Convert OUTBOUND_DATE to datetime and handle potential errors
    df["OUTBOUND_DATE"] = pd.to_datetime(df["OUTBOUND_DATE"], errors="coerce")

    # Drop rows where OUTBOUND_DATE is NaT
    df.dropna(subset=["OUTBOUND_DATE"], inplace=True)

    # Handle missing values
    df.dropna(inplace=True)

    # Remove outliers in NET_QUANTITY_MT
    Q1 = df["NET_QUANTITY_MT"].quantile(0.25)
    Q3 = df["NET_QUANTITY_MT"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[
        (df["NET_QUANTITY_MT"] >= lower_bound) & (df["NET_QUANTITY_MT"] <= upper_bound)
    ]

    # Save the cleaned data
    df.to_csv(output_path, index=False)
    print(f"Cleaned outbound data saved to {output_path}")


if __name__ == "__main__":
    # Define file paths
    inbound_input = "/Users/pakinnuntasukkasem/Downloads/bootcathon/Inbound.csv"
    inbound_output = (
        "/Users/pakinnuntasukkasem/Downloads/bootcathon/Inbound_cleaned.csv"
    )
    outbound_input = "/Users/pakinnuntasukkasem/Downloads/bootcathon/Outbound.csv"
    outbound_output = (
        "/Users/pakinnuntasukkasem/Downloads/bootcathon/Outbound_cleaned.csv"
    )

    # Clean the datasets
    clean_inbound_data(inbound_input, inbound_output)
    clean_outbound_data(outbound_input, outbound_output)
