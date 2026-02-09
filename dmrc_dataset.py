import csv

# ==========================================
# PART 1: VERIFIED DMRC MASTER DATASET
# ==========================================

# Ordered list of stations for every line (Correct as of 2026)
METRO_NETWORKS = {
    "Red Line": [
        "Shaheed Sthal", "Hindon River", "Arthala", "Mohan Nagar", "Shyam Park", 
        "Major Mohit Sharma Rajendra Nagar", "Raj Bagh", "Shaheed Nagar", "Dilshad Garden", 
        "Jhilmil", "Mansarovar Park", "Shahdara", "Welcome", "Seelampur", "Shastri Park", 
        "Kashmere Gate", "Tis Hazari", "Pul Bangash", "Pratap Nagar", "Shastri Nagar", 
        "Inderlok", "Kanhaiya Nagar", "Keshav Puram", "Netaji Subhash Place", 
        "Kohat Enclave", "Pitampura", "Rohini East", "Rohini West", "Rithala"
    ],
    "Yellow Line": [
        "Samaypur Badli", "Rohini Sector 18-19", "Haiderpur Badli Mor", "Jahangirpuri", 
        "Adarsh Nagar", "Azadpur", "Model Town", "GTB Nagar", "Vishwa Vidyalaya", 
        "Vidhan Sabha", "Civil Lines", "Kashmere Gate", "Chandni Chowk", "Chawri Bazar", 
        "New Delhi", "Rajiv Chowk", "Patel Chowk", "Central Secretariat", "Udyog Bhawan", 
        "Lok Kalyan Marg", "Jor Bagh", "Dilli Haat INA", "AIIMS", "Green Park", 
        "Hauz Khas", "Malviya Nagar", "Saket", "Qutab Minar", "Chhatarpur", "Sultanpur", 
        "Ghitorni", "Arjan Garh", "Guru Dronacharya", "Sikanderpur", "MG Road", 
        "IFFCO Chowk", "Millennium City Centre Gurugram"
    ],
    "Blue Line": [
        "Dwarka Sector 21", "Dwarka Sector 8", "Dwarka Sector 9", "Dwarka Sector 10", 
        "Dwarka Sector 11", "Dwarka Sector 12", "Dwarka Sector 13", "Dwarka Sector 14", 
        "Dwarka", "Dwarka Mor", "Nawada", "Uttam Nagar West", "Uttam Nagar East", 
        "Janakpuri West", "Janakpuri East", "Tilak Nagar", "Subhash Nagar", "Tagore Garden", 
        "Rajouri Garden", "Ramesh Nagar", "Moti Nagar", "Kirti Nagar", "Shadipur", 
        "Patel Nagar", "Rajendra Place", "Karol Bagh", "Jhandewalan", "Ramakrishna Ashram Marg", 
        "Rajiv Chowk", "Barakhamba Road", "Mandi House", "Supreme Court", "Indraprastha", 
        "Yamuna Bank", "Akshardham", "Mayur Vihar Phase-1", "Mayur Vihar Extension", 
        "New Ashok Nagar", "Noida Sector 15", "Noida Sector 16", "Noida Sector 18", 
        "Botanical Garden", "Golf Course", "Noida City Centre", "Noida Sector 34", 
        "Noida Sector 52", "Noida Sector 61", "Noida Sector 59", "Noida Sector 62", 
        "Noida Electronic City"
    ],
    "Blue Line Branch": [
        "Yamuna Bank", "Laxmi Nagar", "Nirman Vihar", "Preet Vihar", "Karkarduma", 
        "Anand Vihar ISBT", "Kaushambi", "Vaishali"
    ],
    "Green Line": [
        "Inderlok", "Ashok Park Main", "Punjabi Bagh", "Shivaji Park", "Madipur", 
        "Paschim Vihar East", "Paschim Vihar West", "Peeragarhi", "Udyog Nagar", 
        "Maharaja Surajmal Stadium", "Nangloi", "Nangloi Railway Station", "Rajdhani Park", 
        "Mundka", "Mundka Industrial Area", "Ghevra Metro Station", "Tikri Kalan", 
        "Tikri Border", "Pandit Shree Ram Sharma", "Bahadurgarh City", "Brigadier Hoshiar Singh"
    ],
    "Green Line Branch": [
        "Kirti Nagar", "Satguru Ram Singh Marg", "Ashok Park Main"
    ],
    "Violet Line": [
        "Kashmere Gate", "Lal Quila", "Jama Masjid", "Delhi Gate", "ITO", "Mandi House", 
        "Janpath", "Central Secretariat", "Khan Market", "Jawaharlal Nehru Stadium", 
        "Jangpura", "Lajpat Nagar", "Moolchand", "Kailash Colony", "Nehru Place", 
        "Kalkaji Mandir", "Govind Puri", "Harkesh Nagar Okhla", "Jasola Apollo", 
        "Sarita Vihar", "Mohan Estate", "Tughlakabad Station", "Badarpur Border", 
        "Sarai", "NHPC Chowk", "Mewala Maharajpur", "Sector 28 Faridabad", 
        "Badkal Mor", "Old Faridabad", "Neelam Chowk Ajronda", "Bata Chowk", 
        "Escorts Mujesar", "Sant Surdas (Sihi)", "Raja Nahar Singh"
    ],
    "Pink Line": [
        "Majlis Park", "Azadpur", "Shalimar Bagh", "Netaji Subhash Place", "Shakurpur", 
        "Punjabi Bagh West", "ESI - Basaidarapur", "Rajouri Garden", "Mayapuri", 
        "Naraina Vihar", "Delhi Cantt", "Durgabai Deshmukh South Campus", 
        "Sir M. Vishveshwaraya Moti Bagh", "Bhikaji Cama Place", "Sarojini Nagar", 
        "Dilli Haat INA", "South Extension", "Lajpat Nagar", "Vinobapuri", "Ashram", 
        "Sarai Kale Khan - Nizamuddin", "Mayur Vihar Phase-1", "Mayur Vihar Pocket I", 
        "Trilokpuri - Sanjay Lake", "East Vinod Nagar - Mayur Vihar-II", 
        "Mandawali - West Vinod Nagar", "IP Extension", "Anand Vihar ISBT", "Karkarduma", 
        "Karkarduma Court", "Krishna Nagar", "East Azad Nagar", "Welcome", "Jaffrabad", 
        "Maujpur - Babarpur", "Gokulpuri", "Johri Enclave", "Shiv Vihar"
    ],
    "Magenta Line": [
        "Janakpuri West", "Dabri Mor - Janakpuri South", "Dashrath Puri", "Palam", 
        "Sadar Bazaar Cantonment", "Terminal 1 IGI Airport", "Shankar Vihar", 
        "Vasant Vihar", "Munirka", "RK Puram", "IIT Delhi", "Hauz Khas", "Panchsheel Park", 
        "Chirag Delhi", "Greater Kailash", "Nehru Enclave", "Kalkaji Mandir", 
        "Okhla NSIC", "Sukhdev Vihar", "Jamia Millia Islamia", "Okhla Vihar", 
        "Jasola Vihar Shaheen Bagh", "Kalindi Kunj", "Okhla Bird Sanctuary", "Botanical Garden"
    ],
    "Grey Line": [
        "Dwarka", "Nangli", "Najafgarh", "Dhansa Bus Stand"
    ],
    "Airport Express": [
        "New Delhi", "Shivaji Stadium", "Dhaula Kuan", "Delhi Aerocity", "IGI Airport", 
        "Dwarka Sector 21", "Yashobhoomi Dwarka Sector 25"
    ]
}

def generate_dmrc_dataset():
    """
    Generates a list of dictionaries for all DMRC stations.
    Each dictionary represents a station on a specific line.
    """
    dataset = []
    
    # Prefix map for station codes
    PREFIX_MAP = {
        "Red Line": "RD", "Yellow Line": "YL", "Blue Line": "BL", 
        "Blue Line Branch": "BLB", "Green Line": "GR", "Green Line Branch": "GRB",
        "Violet Line": "VT", "Pink Line": "PK", "Magenta Line": "MG", 
        "Grey Line": "GY", "Airport Express": "AE"
    }

    # First pass: Identify all lines for each station to determine interchanges
    station_lines_map = {}
    for line, stations in METRO_NETWORKS.items():
        for station in stations:
            if station not in station_lines_map:
                station_lines_map[station] = set()
            station_lines_map[station].add(line)

    # Second pass: Build the dataset
    for line, stations in METRO_NETWORKS.items():
        for i, station_name in enumerate(stations):
            # Determine neighbors on the same line
            neighbors = []
            if i > 0:
                neighbors.append(stations[i-1])
            if i < len(stations) - 1:
                neighbors.append(stations[i+1])
            
            # Determine interchange info
            all_lines = station_lines_map[station_name]
            interchange_lines = list(all_lines - {line})
            is_interchange = len(interchange_lines) > 0
            
            # Generate Station Code
            prefix = PREFIX_MAP.get(line, "XX")
            code = f"{prefix}{i+1:02d}"
            
            record = {
                "name": station_name,
                "line": line,
                "code": code,
                "neighbors": neighbors,
                "interchange": is_interchange,
                "interchange_lines": interchange_lines
            }
            dataset.append(record)
            
    return dataset

# The Master Dataset Variable
STATION_DATASET = generate_dmrc_dataset()

def save_dataset_to_csv(filename="dmrc_master_stations.csv"):
    """
    Exports the dataset to a CSV file.
    """
    if not STATION_DATASET:
        return
    
    headers = ["station_name", "lines", "code", "neighbors", "interchange", "interchange_lines"]
    
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in STATION_DATASET:
                row_csv = {}
                row_csv['station_name'] = row['name']
                all_lines = [row['line']] + row['interchange_lines']
                row_csv['lines'] = ",".join(all_lines)
                row_csv['code'] = row['code']
                row_csv['neighbors'] = ",".join(row['neighbors'])
                row_csv['interchange'] = "Yes" if row['interchange'] else "No"
                row_csv['interchange_lines'] = ",".join(row['interchange_lines'])
                writer.writerow(row_csv)
        print(f"✅ Successfully generated {filename} with {len(STATION_DATASET)} records.")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

if __name__ == "__main__":
    # When run directly, generate the CSV
    save_dataset_to_csv()