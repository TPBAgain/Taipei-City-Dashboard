#not test/used yet
import pandas as pd
import os

def filter_restaurants(input_file, output_file):
    # Read the CSV file
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except UnicodeDecodeError:
        # Try with different encoding if utf-8 fails
        df = pd.read_csv(input_file, encoding='big5')
    
    # Filter rows where 登錄項目 is 餐飲場所
    filtered_df = df[df['登錄項目'] == '餐飲場所']
    
    # Save to a new CSV file
    filtered_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Original file had {len(df)} rows.")
    print(f"Filtered file has {len(filtered_df)} rows.")
    print(f"Filtered data saved to {output_file}")

if __name__ == "__main__":
    input_file = "97_2.csv"
    output_file = "97_2_restaurants.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
    else:
        filter_restaurants(input_file, output_file)