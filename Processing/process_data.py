import os
import shutil
import pandas as pd
from datetime import datetime

incoming = "Incoming"
processing = "Processing"
processed = "Processed"


for folder in [incoming, processing, processed]:
    os.makedirs(folder, exist_ok=True)


processed_files = os.listdir(processed)


files = [f for f in os.listdir(incoming) if f.endswith(".csv")]

for file in files:
    try:
       
        already_done = any(p.startswith(file) for p in processed_files)

        if already_done:
            print(f"Skipping duplicate: {file}")
            continue

       
        src = os.path.join(incoming, file)
        proc_path = os.path.join(processing, file)
        shutil.move(src, proc_path)

        with open(proc_path, "r") as f:    
          df = pd.read_csv(proc_path)

        
        df = df.rename(columns={"Transaction Date": "Date"})

        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        
        df['Processed_Time'] = datetime.now()

        with open (proc_path, "w",newline="") as f:
          df.to_csv(proc_path, index=False)

        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        name = file.replace(".csv", "")
        new_filename = f"{name}_{timestamp}.csv"
        
        final_path = os.path.join(processed, new_filename)
        shutil.move(proc_path, final_path)

        print(f"Processed: {new_filename}")

    except Exception as e:
        print(f"Error processing {file}: {e}")