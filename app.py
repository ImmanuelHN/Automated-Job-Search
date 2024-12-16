import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import time
import random

def scrape_timesjobs(search_term, location, num_jobs=5):
    """
    Scrape job listings from TimesJobs.com
    
    Parameters:
    search_term (str): Job title to search for
    location (str): Location to search in
    num_jobs (int): Number of jobs to scrape (default is 5)
    """
    try:
        # Format the TimesJobs URL
        url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={search_term.replace(' ', '+')}&txtLocation={location.replace(' ', '+')}"
        
        # Headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        print(f"Fetching jobs for: {search_term} in {location}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings
            jobs_data = []
            job_cards = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')[:num_jobs]
            
            if not job_cards:
                print("No job listings found. Please try different search terms.")
                return None
            
            print(f"Found {len(job_cards)} job listings")
            
            for job in job_cards:
                try:
                    # Extract job details
                    title = job.find('h2').get_text(strip=True) if job.find('h2') else 'N/A'
                    company = job.find('h3', class_='joblist-comp-name').get_text(strip=True) if job.find('h3', class_='joblist-comp-name') else 'N/A'
                    location = job.find('ul', class_='top-jd-dtl clearfix').find('span').get_text(strip=True) if job.find('ul', class_='top-jd-dtl clearfix') else 'N/A'
                    skills = job.find('span', class_='srp-skills').get_text(strip=True) if job.find('span', class_='srp-skills') else 'N/A'
                    
                    job_info = {
                        'Job Title': title,
                        'Company': company,
                        'Location': location,
                        'Skills Required': skills
                    }
                    
                    jobs_data.append(job_info)
                    print(f"Scraped: {title} at {company}")
                    
                    # Add a small random delay between processing jobs
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"Error processing job listing: {str(e)}")
                    continue
            
            return jobs_data
            
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the website. Please check your internet connection.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def save_to_csv(jobs_data, filename=None):
    """
    Save the scraped jobs data to a CSV file
    
    Parameters:
    jobs_data (list): List of dictionaries containing job information
    filename (str): Optional custom filename
    """
    try:
        if not jobs_data:
            print("No data to save")
            return
        
        # Create directory for CSV files if it doesn't exist
        os.makedirs('job_listings', exist_ok=True)
        
        # Generate filename with timestamp if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join('job_listings', f'job_listings_{timestamp}.csv')
        
        # Save to CSV using pandas
        df = pd.DataFrame(jobs_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # Using utf-8-sig for better Excel compatibility
        print(f"Data successfully saved to: {filename}")
        
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")

def main():
    try:
        # Get user input
        search_term = input("Enter job title to search for: ")
        location = input("Enter location: ")
        
        # Scrape the jobs
        jobs_data = scrape_timesjobs(search_term, location)
        
        # Save to CSV if data was successfully scraped
        if jobs_data:
            save_to_csv(jobs_data)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()