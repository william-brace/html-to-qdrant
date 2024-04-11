import subprocess

# List of links to download
linksNY = [
    'https://paidfamilyleave.ny.gov/',
    'https://paidfamilyleave.ny.gov/employees',
    'https://paidfamilyleave.ny.gov/eligibility',
    'https://paidfamilyleave.ny.gov/paid-family-leave-bonding',
    'https://paidfamilyleave.ny.gov/paid-family-leave-family-care',
    'https://paidfamilyleave.ny.gov/paid-family-leave-military-families',
    'https://paidfamilyleave.ny.gov/benefits',
    'https://paidfamilyleave.ny.gov/cost',
    'https://paidfamilyleave.ny.gov/protections',
    'https://paidfamilyleave.ny.gov/COVID19',
    'https://paidfamilyleave.ny.gov/if-you-are-quarantined-yourself',
    'https://paidfamilyleave.ny.gov/if-your-minor-dependent-child-quarantined',
    'https://paidfamilyleave.ny.gov/new-york-paid-family-leave-covid-19-faqs',
    'https://paidfamilyleave.ny.gov/paid-family-leave-and-other-benefits',
    'https://paidfamilyleave.ny.gov/bonding-leave-birth-child',
    'https://paidfamilyleave.ny.gov/bonding-leave-adoption-child',
    'https://paidfamilyleave.ny.gov/bonding-leave-fostering-child',
    'https://paidfamilyleave.ny.gov/2024',
    'https://paidfamilyleave.ny.gov/employer-responsibilities-and-resources',
    'https://paidfamilyleave.ny.gov/handling-requests',
    'https://paidfamilyleave.ny.gov/public-employers',
    'https://paidfamilyleave.ny.gov/self-employed-individuals',
    'https://paidfamilyleave.ny.gov/out-state-employers',
    'https://paidfamilyleave.ny.gov/paid-family-leave-information-health-care-providers',
    'https://paidfamilyleave.ny.gov/paid-family-leave-and-other-benefits',
    'https://paidfamilyleave.ny.gov/employer-responsibilities-and-resources',
    'https://paidfamilyleave.ny.gov/handling-requests',
    'https://paidfamilyleave.ny.gov/obtaining-and-funding-policy',
    'https://paidfamilyleave.ny.gov/public-employers',
    'https://paidfamilyleave.ny.gov/self-employed-individuals',
    'https://paidfamilyleave.ny.gov/out-state-employers',
]

linksCO = [
  "https://famli.colorado.gov/",
  "https://famli.colorado.gov/individuals-and-families/my-famli",
  "https://famli.colorado.gov/individuals-and-families/my-famli/my-famli-user-guide-for-claimants/my-famli-user-guide-getting",
  "https://famli.colorado.gov/individuals-and-families/my-famli/my-famli-user-guide-for-claimants/my-famli-user-guide-filing-a",
  "https://famli.colorado.gov/individuals-and-families/my-famli/my-famli-user-guide-for-claimants/my-famli-user-guide-reasons-for",
  "https://famli.colorado.gov/individuals-and-families/my-famli/my-famli-user-guide-for-claimants/my-famli-user-guide-next-steps",
  "https://famli.colorado.gov/individuals-and-families",
  "https://famli.colorado.gov/individuals-and-families/premium-and-benefits-calculator",
  "https://famli.colorado.gov/individuals-and-families/how-famli-leave-can-be-used",
  "https://famli.colorado.gov/individuals-and-families/famli-and-fmla",
  "https://famli.colorado.gov/individuals-and-families/self-employed-workers",
  "https://famli.colorado.gov/individuals-and-families/local-government-employees",
  "https://famli.colorado.gov/individuals-and-families/parental-bonding-leave",
  "https://famli.colorado.gov/individuals-and-families/medical-leave-to-care-for-yourself",
  "https://famli.colorado.gov/individuals-and-families/medical-leave-to-care-for-a-family-member",
  "https://famli.colorado.gov/individuals-and-families/military-family-members-exigency-leave",
  "https://famli.colorado.gov/individuals-and-families/safe-leave-domestic-violence",
  "https://famli.colorado.gov/individuals-and-families/individuals-and-families-faqs",
  "https://famli.colorado.gov/individuals-and-families/appeals",
  "https://famli.colorado.gov/individuals-and-families/report-famli-fraud",
  "https://famli.colorado.gov/individuals-and-families/report-famli-noncompliance-or-audit-issues",
  "https://famli.colorado.gov/employers",
  "https://famli.colorado.gov/employers/my-famli-employer",
  "https://famli.colorado.gov/employers/employer-faqs",
  "https://famli.colorado.gov/employers/local-governments",
  "https://famli.colorado.gov/employers/local-governments/faqs-for-local-governments",
  "https://famli.colorado.gov/employers/third-party-administrators-tpas",
  "https://famli.colorado.gov/employers/famli-other-types-of-leave",
  "https://famli.colorado.gov/employers/private-plans",
  "https://famli.colorado.gov/employers/small-business-corner",
  "https://famli.colorado.gov/health-care-providers",
  "https://famli.colorado.gov/health-care-providers/health-care-providers-faqs",
  "https://famli.colorado.gov/health-care-providers/my-famli-user-guide-for-health-care-providers",
  "https://famli.colorado.gov/proposed/adopted-rules"
]


# wget command options
wget_options = [
    '-np',  # No parent directories
    '-nd',  # No directory structure
    '-A.html,.txt,.tmp',  # File extensions to download
    '-P', 'websites',  # Output directory
]

# Iterate over the links and download each one
for link in linksNY:
    # Construct the wget command
    wget_command = ['wget'] + wget_options + [link]
    
    # Execute the wget command using subprocess
    subprocess.run(wget_command, check=True)
    
    print(f'Downloaded: {link}')

print('Downloading completed.')