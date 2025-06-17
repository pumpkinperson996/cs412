# models.py
# Name: Shuwei Zhu
# Email: david996@bu.edu
# Description: Django models for voter analytics application with CSV data import functionality

from django.db import models
import csv
import os
from datetime import datetime

class Voter(models.Model):
    """
    Model representing a registered voter in Newton, MA.
    Contains demographic information and voting history.
    
    This model stores all the data from the Newton voters CSV file,
    including personal information, address, registration details,
    and voting participation in the last 5 elections.
    """
    
    # Personal Information
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    
    # Address Information
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    
    # Registration Information
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.CharField(max_length=10)
    
    # Voting History
    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)
    
    # Calculated Field
    voter_score = models.IntegerField(default=0)
    
    def __str__(self):
        """String representation of a Voter"""
        return f"{self.first_name} {self.last_name} - {self.street_number} {self.street_name}"
    
    class Meta:
        ordering = ['last_name', 'first_name']


def load_data():
    """
    Load voter data from CSV file into the database.
    Processes newton_voters.csv and creates Voter model instances.
    
    This function:
    1. Clears any existing voter data to avoid duplicates
    2. Reads the CSV file from the project root directory
    3. Parses each row and converts data types appropriately
    4. Calculates voter_score based on election participation
    5. Uses bulk_create for efficient database insertion
    
    """
    # Clear existing data
    Voter.objects.all().delete()
    
    # Path to CSV file (adjust path as needed)
    csv_file_path = 'newton_voters.csv'
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        voters_to_create = []
        
        for row in csv_reader:
            # Parse dates
            dob = datetime.strptime(row['Date of Birth'], '%Y-%m-%d').date()
            dor = datetime.strptime(row['Date of Registration'], '%Y-%m-%d').date()
            
            # Convert voting history to boolean
            v20state = row['v20state'].strip().upper() == 'TRUE'
            v21town = row['v21town'].strip().upper() == 'TRUE'
            v21primary = row['v21primary'].strip().upper() == 'TRUE'
            v22general = row['v22general'].strip().upper() == 'TRUE'
            v23town = row['v23town'].strip().upper() == 'TRUE'
            
            # Calculate voter score
            voter_score = sum([v20state, v21town, v21primary, v22general, v23town])
            
            # Create Voter instance
            voter = Voter(
                last_name=row['Last Name'].strip(),
                first_name=row['First Name'].strip(),
                street_number=row['Residential Address - Street Number'].strip(),
                street_name=row['Residential Address - Street Name'].strip(),
                apartment_number=row.get('Residential Address - Apartment Number', '').strip(),
                zip_code=row['Residential Address - Zip Code'].strip(),
                date_of_birth=dob,
                date_of_registration=dor,
                party_affiliation=row['Party Affiliation'],  # Keep the 2-char field as is
                precinct_number=row['Precinct Number'].strip(),
                v20state=v20state,
                v21town=v21town,
                v21primary=v21primary,
                v22general=v22general,
                v23town=v23town,
                voter_score=voter_score
            )
            
            voters_to_create.append(voter)
            
            # Bulk create every 1000 records for efficiency
            if len(voters_to_create) >= 1000:
                Voter.objects.bulk_create(voters_to_create)
                voters_to_create = []
        
        # Create remaining voters
        if voters_to_create:
            Voter.objects.bulk_create(voters_to_create)
    
    print(f"Successfully loaded {Voter.objects.count()} voters")

